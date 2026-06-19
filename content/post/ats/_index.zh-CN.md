---
title: ATS 列车自动监控系统
description: 轨道交通列车自动监控系统（ATS）后台架构与前端模块深度解析
date: 2023-01-10T09:00:00+08:00
lastmod: 2025-05-08T10:00:00+08:00
tags:
  - ATS
  - 轨道交通
  - 列车自动监控
categories:
  - 轨道交通
  - 技术分享
mermaid: true
photos:
  - https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=modern%20rail%20transit%20control%20center%20with%20multiple%20monitoring%20screens%20showing%20train%20schedules%20and%20metro%20map%2C%20blue%20tone%2C%20professional%20dispatch%20room&image_size=landscape_16_9
---

## 专栏介绍

本专栏系统解析轨道交通列车自动监控系统（Automatic Train Supervision, ATS）的整体架构、模块关系与核心业务信息流，涵盖后台服务架构与前端 ControlMonitor 监控系统，帮助读者深入理解 ATS 系统的设计思想与实现细节。

### 后台系统架构

| 文章 | 简介 |
|------|------|
| [HFS1 项目整体说明](./整体说明/) | 从系统规模、分层架构到核心业务模块，全面了解 ATS 系统的全貌 |
| [系统模块关系与架构分析](./系统模块关系与架构分析/) | 深入分析模块依赖关系、通信机制与业务架构设计 |
| [业务信息流分析](./业务信息流分析/) | 详解进路选排、移动授权、跳停、清客等核心业务的信息流转过程 |

### 前端 ControlMonitor 监控系统

| 文章 | 简介 |
|------|------|
| [前端系统架构与功能模块分析](./系统架构分析/) | 基于 Qt 框架的 ControlMonitor 插件化架构设计与核心组件解析 |
| [ControlMonitor 主程序模块](./ControlMonitor模块功能说明/) | 系统主程序入口，负责初始化、数据中心管理、插件加载与系统级消息处理 |
| [PublicExternals 公共外部库](./PublicExternals模块功能说明/) | 系统底层核心组件集合，提供协议实现、插件公共库和网络通信功能 |
| [CmCtrlCmdProcPlug 控制命令处理插件](./CmCtrlCmdProcPlug模块功能说明/) | 处理信号控制、列车控制、站台控制等控制命令的执行与管理 |
| [CmDataMaintainPlug 数据维护插件](./CmDataMaintainPlug模块功能说明/) | 系统数据的加载、初始化、维护与监控任务管理 |
| [CmOperAreaManagePlug 操作区域管理插件](./CmOperAreaManagePlug模块功能说明/) | 操作区域划分、分配、释放及外部数据接收处理 |
| [CmSignalDisplayPlug 信号显示插件](./CmSignalDisplayPlug模块功能说明/) | 信号状态与信号设备的可视化展示及交互操作 |
| [CmSignalProcPlug 信号处理插件](./CmSignalProcPlug模块功能说明/) | 信号的接收、处理与分发，确保系统及时响应信号状态变化 |
| [CmTrainDispatchPlug 列车调度插件](./CmTrainDispatchPlug模块功能说明/) | 列车调度命令的生成、发送、管理及列车状态监控 |
| [CmTrainNumProcPlug 列车号处理插件](./CmTrainNumProcPlug模块功能说明/) | 列车号的管理、显示与处理，提供列车信息列表与交互 |
| [UserManagerPlug 用户管理插件](./UserManagerPlug模块功能说明/) | 用户管理、角色管理与权限分配，提供系统访问控制 |
