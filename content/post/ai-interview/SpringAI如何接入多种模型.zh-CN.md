---
title: "SpringAI如何接入多种模型"
description: "OpenAI、DeepSeek、GLM等多模型接入、统一API封装、模型切换策略"
date: 2023-08-20T14:30:00+08:00
lastmod: 2023-08-20T14:30:00+08:00
weight: 4
tags:
  - AI面试
  - SpringAI
  - 模型接入
  - OpenAI
categories:
  - AI面试
  - 技术分享
math: true
mermaid: true
photos:
  - https://images.unsplash.com/photo-1518770660439-4636190af475?w=1920&q=80
---

## 多模型接入

> **面试场景**：如何使用SpringAI同时接入OpenAI、DeepSeek和GLM等多种模型？

## 配置方式

### 1. Maven依赖

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-ollama-spring-boot-starter</artifactId>
</dependency>
```

### 2. 配置文件

```yaml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
    ollama:
      base-url: http://localhost:11434
```

### 3. 模型切换

```java
@Autowired
private ChatClient chatClient;

@Autowired
private ModelRegistry modelRegistry;

public String chatWithModel(String modelName, String prompt) {
    Model model = modelRegistry.getModel(modelName);
    return chatClient.withModel(model).prompt(prompt).call().getContent();
}
```

## 总结

SpringAI通过统一的API抽象，使得接入多种AI模型变得简单高效。
