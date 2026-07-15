# ATS智能运维监控系统 - 项目介绍

## 1 项目简介

本项目是面向城市轨道交通信号系统的**实时设备监控与运维数据采集系统**，部署在ATS（Automatic Train Supervision，列车自动监控）系统内部，周期性采集全线设备运行状态，按标准通信协议打包上报至运维平台，实现"采-传-管"一体化的设备运维闭环。

系统覆盖全线100+台设备，从设备状态产生到上报运维平台延迟不超过30秒，采集成功率≥95%，系统可用性≥99.9%。

## 2 系统架构

采用**分布式采集 + 集中式汇聚**的两级架构：

```
                         运维平台 (外部系统)
                       接收二进制维护数据包
                              ▲
                              │ TCP
                              │
                    ┌─────────┴─────────┐
                    │   ops_hub (汇聚中心) │
                    │  SNMP采集→打包→发送  │
                    └─────────▲─────────┘
                              │ SNMP GET
                 ┌────────────┼────────────┐
                 │            │            │
            ops_agent     ops_agent    ops_agent
             (车站A)       (车站B)      (中心)
            系统资源       系统资源      系统资源
            双机状态       双机状态      双机状态
            接口状态       接口状态      接口状态
```

网络采用A/B双网冗余设计，ops_hub采集时优先走A网，A网不通自动切换B网。

## 3 核心模块

### 3.1 ops_agent（设备代理）

部署在每台被监控设备上（Linux/Windows），本地采集设备状态并通过SNMP协议暴露数据。

| 功能模块 | 说明 |
|----------|------|
| 系统资源监控 | CPU/内存使用率、进程数、线程数、硬盘占用率（psutil） |
| 双机热备检测 | 解析网卡漂移IP判断主备状态，漂移IP在主机上→主机(0x55)，否则→备机(0xAA) |
| 外部接口检测 | TCP接口通过netstat检测ESTABLISHED连接；UDP接口通过tcpdump双向抓包检测 |
| 数据输出 | 每30秒写入device_monitor.json和string_device_monitor.txt，供SNMP pass机制读取 |

### 3.2 ops_hub（汇聚中心）

部署在控制中心，负责全网数据采集、协议打包和TCP上报。

| 功能模块 | 说明 |
|----------|------|
| SNMP异步采集 | 基于aiosnmp+asyncio并发采集100+节点，总耗时3-5秒；A/B网自动切换 |
| 二进制协议打包 | 按《ATS维护机与智能运维系统接口适配协议》组装7种维护信息包 |
| TCP数据发送 | 多客户端广播、Keep-Alive保活、发送失败3次重试 |
| 缓存与预收集 | 后台线程每20秒预采集打包，发送时零延迟读缓存 |
| 中间文件 | 生成采集状态、发送明细、自身运行状态等JSON文件，供Web监控展示 |

三种发送包类型：

| 包类型 | 帧类型 | 周期 | 说明 |
|--------|--------|------|------|
| 维护信息包 | 0x8E | 20秒 | 设备状态全量上报（启停/运行/双机/硬盘/进程连接/接口状态） |
| 校时信息包 | 0x8D | 1秒 | 时间同步 |
| 版本信息包 | 0x8F | 30秒 | 系统/程序/数据/配置版本 |

### 3.3 generate_config（配置工具链）

从设备XML配置批量生成并部署配置文件。

| 脚本 | 功能 |
|------|------|
| 1_xml2json_ops_hub.py | XML→hub_config.json（ops_hub采集节点配置） |
| 3_xml2json_ops_agent.py | XML→ops_agent_*.json（各设备配置，含局码/站码/设备ID自动计算） |
| 5_assemble.py | SSH/SFTP批量部署到Linux设备，FTP部署到Windows设备 |
| 6_2iom.py | 生成设备清单Excel表格 |

### 3.4 utils（公共工具库）

| 模块 | 功能 |
|------|------|
| log_decorator.py | 基于loguru的日志装饰器，自动注入logger，按天轮转+zip压缩 |
| defines.py | 全部枚举定义（DualStatus/ConnectStatus/InfoCode/InterfaceType等） |
| json_utils.py | JSON工具类，支持json5注释和SimpleNamespace点号访问 |
| snmp_client.py | 基于pysnmp的SNMP v2c客户端 |
| network_checker.py | 跨平台ping检测工具 |

## 4 数据流程

```
ops_agent (每30秒)
  │ 采集系统资源/双机状态/接口状态
  │ 写入 string_device_monitor.txt
  ▼
SNMP pass 机制
  │ snmpd 调用 oid_handler 读取文件
  │ 返回 OID + string + JSON内容
  ▼
ops_hub (每20秒)
  │ aiosnmp 异步并发采集所有节点
  │ ping预检测 + 结果缓存
  │ 解析JSON → struct打包二进制帧
  │ 存入缓存
  ▼
TCP发送线程
  │ 从缓存读取 → send_raw_data
  │ 发送到运维平台
  │ 生成中间文件
  ▼
运维平台
  接收二进制维护数据包
```

## 5 技术栈

| 领域 | 技术 | 说明 |
|------|------|------|
| 开发语言 | Python 3.6+ | 兼容CentOS 7自带Python |
| SNMP采集 | aiosnmp / pysnmp | 异步采集性能最优，pysnmp功能完备 |
| 异步框架 | asyncio | Python原生，3.6兼容 |
| 日志 | loguru | 轮转/压缩/多级别分离 |
| 系统信息 | psutil | 跨平台CPU/内存/进程/磁盘 |
| 二进制打包 | struct | 精确控制字节序（小端/网络序） |
| 网络通信 | socket (TCP) | Keep-Alive保活、多客户端管理 |
| 配置格式 | JSON (json5) | 支持注释和尾随逗号 |
| 远程部署 | paramiko (SSH/SFTP) | 自动化配置分发 |
| 打包 | PyInstaller 4.10 | 单文件可执行，最后支持3.6的版本 |
| 表格生成 | openpyxl | Excel设备清单 |
| Web监控 | Flask | 轻量级中间文件可视化 |

## 6 部署方案

### 6.1 Linux部署目录

```
/rm/
├── bin/
│   ├── ops_agent              # 设备代理
│   └── ops_hub                # 汇聚中心
├── etc/
│   ├── private/
│   │   ├── ops_agent.json     # 设备代理配置
│   │   └── ops_hub.json       # 汇聚中心配置
│   └── public/
│       └── devices.xml        # 设备配置XML
├── log/
│   ├── ops_agent/             # 设备代理日志
│   └── ops_hub/               # 汇聚中心日志
└── script/
    └── rm.sh                  # 启停脚本
```

### 6.2 Windows部署

ops_agent部署为系统托盘程序（pystray），配置和日志存放在安装目录下，SNMP数据输出到`C:\snmp_files\`。

### 6.3 批量部署

通过 `5_assemble.py` 自动化部署：
- Linux设备：SSH连接→tar打包上传→解压到`/rm/`→设置权限→执行rm.sh重启
- Windows设备：FTP传输→备份旧目录→复制新文件
- 支持进度条显示和部署结果汇总

## 7 关键技术亮点

1. **异步并发采集**：100+节点SNMP采集从100+秒降至3-5秒（aiosnmp + asyncio.gather）
2. **预收集+缓存**：后台线程提前采集打包，发送线程零延迟读取，保证发送周期稳定
3. **双机热备检测**：通过网卡漂移IP（secondary标记）精确判断主备状态，双机切换后秒级感知
4. **UDP双向抓包检测**：tcpdump收发双向验证，解决UDP无连接状态难以检测的问题
5. **多编码自动探测**：UTF-8/GBK/GB2312自动切换，兼容不同操作系统返回数据
6. **二进制协议精确打包**：struct精确控制小端序/网络字节序，完全符合协议规范
7. **Python 3.6全兼容**：不使用asyncio.run()、海象运算符等3.7+特性
8. **中间文件可观测性**：by_code/by_device两个维度的hex详情，含device_ip方便问题定位

## 8 项目目录结构

```
ops_mgr/
├── projA/                          # ops_agent 设备代理
│   ├── ops_agent.py                # 主程序 (DeviceMonitor)
│   ├── check_dual_status.py        # 双机热备检测
│   ├── check_connections.py        # 接口连接检测
│   ├── check_system_info.py        # 系统资源采集
│   ├── platform_impl/              # 平台抽象层 (Linux/Windows)
│   ├── oid/                        # SNMP OID处理器
│   └── deploy/                     # 部署脚本和配置
├── projB/                          # ops_hub 汇聚中心
│   ├── ops_hub.py                  # 主程序 (ProgramB)
│   ├── packager.py                 # 打包门面
│   ├── core/
│   │   ├── config/config_loader.py # 配置加载
│   │   ├── data_collector.py       # 采集管理
│   │   ├── data_packager.py        # 协议打包
│   │   ├── cache_manager.py        # 缓存管理
│   │   ├── middle_file_generator.py# 中间文件
│   │   ├── network/tcp_server.py   # TCP通信
│   │   └── snmp/                   # SNMP采集器(策略模式)
│   └── send_protocol/              # 二进制协议定义
├── generate_config/                # 配置生成工具链
│   ├── 3_xml2json_ops_agent.py     # XML→agent配置
│   ├── 5_assemble.py               # SSH/FTP批量部署
│   └── 6_2iom.py                   # 设备清单生成
├── utils/                          # 公共工具库
│   ├── log_decorator.py            # 日志装饰器
│   ├── defines.py                  # 枚举定义
│   ├── json_utils.py               # JSON工具
│   └── snmp_client.py              # SNMP客户端
├── file/                           # 项目文档
└── requirements.txt                # 依赖清单
```
