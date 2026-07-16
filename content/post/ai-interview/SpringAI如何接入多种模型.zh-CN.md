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

在实际项目中，通常需要接入多种AI模型以应对不同的业务需求。SpringAI提供了统一的API抽象，使得多模型接入变得简单。

## 配置方式

### 1. Maven依赖

**面试思路**：SpringAI为不同的模型提供商提供了独立的starter，只需添加对应的依赖即可。

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

**依赖选择**：

- **OpenAI**：官方API，功能完整但成本较高
- **Ollama**：本地部署，适合隐私敏感场景
- **Azure OpenAI**：企业级服务，有更多管理功能

### 2. 配置文件

**面试思路**：在application.yml中配置不同模型的参数。

```yaml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      base-url: https://api.openai.com/v1
    ollama:
      base-url: http://localhost:11434
      model: llama3
```

**配置要点**：

- **API Key**：通过环境变量注入，不要硬编码
- **Base URL**：支持自定义API地址，方便使用代理或本地服务
- **Model**：指定默认模型

### 3. 模型切换

**面试思路**：如何在运行时动态切换模型？

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

**切换策略**：

- **按业务场景切换**：不同业务使用不同模型
- **按成本切换**：优先使用低成本模型
- **按性能切换**：根据响应速度选择模型

## 面试回答框架

当面试官问到这个问题时，可以按照以下框架回答：

1. **依赖管理**：添加对应模型的starter
2. **配置方式**：在配置文件中设置API Key和参数
3. **API使用**：使用统一的ChatClient接口
4. **模型切换**：通过ModelRegistry动态切换
5. **最佳实践**：环境变量注入、配置外部化、统一异常处理

## 总结

SpringAI通过统一的API抽象，使得接入多种AI模型变得简单高效。开发者可以专注于业务逻辑，而不需要关心底层模型的差异。同时，SpringAI还提供了丰富的功能，如向量数据库集成、函数调用等，是构建AI应用的优秀选择。
