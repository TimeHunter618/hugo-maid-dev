---
title: 中间件与运维专栏
description: 常用中间件原理、部署与运维实践
date: 2026-06-21T04:00:00+08:00
lastmod: 2026-06-21T04:00:00+08:00
tags:
  - 中间件
  - 运维
categories:
  - 后端架构
math: true
mermaid: true
photos:
  - https://d-sketon.top/img/backwebp/bg3.webp
---

## 专栏介绍

本专栏系统梳理后端开发与运维中常用的中间件技术，覆盖消息队列、缓存、数据库中间件、Web 服务器、搜索引擎、分布式协调、容器化及性能调优等核心领域。每篇文章均从核心原理出发，结合架构图、配置示例、性能优化策略与常见问题排查，帮助读者从"会用"走向"精通"。

无论你是准备面试的工程师，还是负责线上系统稳定性的运维同学，都能在本专栏中找到可直接落地的实践方案。

### 分类导航

| 分类 | 文章 | 简介 |
|------|------|------|
| 消息队列 | [RabbitMQ 消息队列详解](./RabbitMQ消息队列详解.zh-CN.md) | AMQP 协议、Exchange 类型、消息可靠性、死信队列、延迟队列 |
| 消息队列 | [Kafka 高吞吐消息流处理](./Kafka高吞吐消息流处理.zh-CN.md) | 分区机制、消费者组、消息有序性、Exactly-Once、性能调优 |
| 消息队列 | [Kafka Streams流处理实战](./KafkaStreams流处理实战.zh-CN.md) | DSL API与Processor API、流与表、窗口聚合、状态管理、Exactly-Once语义 |
| 缓存中间件 | [Redis 核心原理与实战](./Redis核心原理与实战.zh-CN.md) | 数据结构、持久化 RDB/AOF、主从哨兵集群、缓存三大问题、分布式锁 |
| 缓存中间件 | [Redis Stream消息队列与发布订阅实战](./RedisStream消息队列与发布订阅实战.zh-CN.md) | Stream核心概念、XADD/XREAD消费者模式、消费者组、消息确认与重试、与List/PUBSUB对比 |
| Web 服务器 | [Nginx 反向代理与负载均衡](./Nginx反向代理与负载均衡.zh-CN.md) | 配置详解、负载均衡策略、限流、HTTPS 配置 |
| Web 服务器 | [Nginx Lua脚本扩展与API网关实践](./NginxLua脚本扩展与API网关实践.zh-CN.md) | OpenResty架构、Lua脚本开发、请求拦截与鉴权、限流熔断、API网关完整实现 |
| 搜索引擎 | [Elasticsearch 全文搜索引擎](./Elasticsearch全文搜索引擎.zh-CN.md) | 倒排索引、分词器、DSL 查询、集群分片副本 |
| 分布式协调 | [ZooKeeper 分布式协调](./ZooKeeper分布式协调.zh-CN.md) | ZAB 协议、Watch 机制、Leader 选举、分布式锁、配置中心 |
| 容器化 | [Docker 容器化部署实践](./Docker容器化部署实践.zh-CN.md) | Dockerfile 最佳实践、多阶段构建、网络模式、数据卷、Compose 编排 |
| 性能调优 | [JVM 调优与 GC 策略](./JVM调优与GC策略.zh-CN.md) | 内存模型、GC 算法对比、G1/ZGC 调优、OOM 排查、Arthas 诊断 |
