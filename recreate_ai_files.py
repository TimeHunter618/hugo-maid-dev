import os

post_dir = r"f:\project\go\hugo_extended_withdeploy_0.163.2_windows-amd64\dev4\content\post\ai-interview"

file_info = {
    'Agent工具调用失败如何处理.zh-CN.md': {
        'title': 'Agent工具调用失败如何处理',
        'description': '处理工具调用失败的常见策略，系统级Agent工具调用的完整方案',
        'date': '2026-02-05T04:14:46+08:00',
        'weight': '2',
        'tags': ['AI面试', 'Agent', '工具调用', '故障处理'],
        'categories': ['AI面试', '技术分享'],
        'photo': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1920&q=80',
        'content': """## 问题背景

> **面试场景**：当系统中的Agent调用外部工具失败时，如何设计健壮的重试和降级机制？

## 核心策略

### 1. 重试机制

```java
public class ToolRetryHandler {
    private static final int MAX_RETRIES = 3;
    private static final long BASE_DELAY_MS = 1000;
    
    public <T> T executeWithRetry(ToolCall<T> toolCall) throws ToolException {
        Exception lastException = null;
        for (int attempt = 1; attempt <= MAX_RETRIES; attempt++) {
            try {
                return toolCall.execute();
            } catch (Exception e) {
                lastException = e;
                long delay = BASE_DELAY_MS * (long) Math.pow(2, attempt - 1);
                Thread.sleep(delay);
            }
        }
        throw new ToolException("Max retries exceeded", lastException);
    }
}
```

### 2. 熔断机制

```java
public class CircuitBreaker {
    private static final int FAILURE_THRESHOLD = 5;
    private static final long COOLDOWN_MS = 30000;
    
    private int failureCount = 0;
    private long lastFailureTime = 0;
    private boolean isOpen = false;
    
    public synchronized boolean allowRequest() {
        if (isOpen) {
            if (System.currentTimeMillis() - lastFailureTime > COOLDOWN_MS) {
                isOpen = false;
                failureCount = 0;
                return true;
            }
            return false;
        }
        return true;
    }
    
    public synchronized void recordFailure() {
        failureCount++;
        lastFailureTime = System.currentTimeMillis();
        if (failureCount >= FAILURE_THRESHOLD) {
            isOpen = true;
        }
    }
}
```

### 3. 降级策略

```java
public class ToolFallbackHandler {
    private Map<String, ToolCall<?>> fallbackMap = new HashMap<>();
    
    public void registerFallback(String toolName, ToolCall<?> fallback) {
        fallbackMap.put(toolName, fallback);
    }
    
    public Object executeWithFallback(String toolName, ToolCall<?> primary) {
        try {
            return primary.execute();
        } catch (Exception e) {
            ToolCall<?> fallback = fallbackMap.get(toolName);
            if (fallback != null) {
                return fallback.execute();
            }
            throw e;
        }
    }
}
```

## 总结

处理工具调用失败需要综合运用重试、熔断和降级策略，确保系统在面对外部依赖故障时仍能保持可用。"""
    },
    'Chrome插件如何安全调用AI.zh-CN.md': {
        'title': 'Chrome插件如何安全调用AI',
        'description': 'API Key安全、通信协议、隔离机制，AI插件安全实践',
        'date': '2025-02-03T11:35:15+08:00',
        'weight': '8',
        'tags': ['AI面试', 'Chrome', 'AI安全', '浏览器扩展'],
        'categories': ['AI面试', '技术分享'],
        'photo': 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1920&q=80',
        'content': """## 安全挑战

> **面试场景**：Chrome插件中存储和使用AI API Key存在哪些安全风险？如何防范？

## 安全策略

### 1. API Key保护

```javascript
chrome.storage.local.get(['apiKey'], function(result) {
    if (result.apiKey) {
        chrome.runtime.sendMessage({
            type: 'CALL_AI',
            apiKey: result.apiKey,
            prompt: userInput
        });
    }
});
```

### 2. 后台脚本隔离

```javascript
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.type === 'CALL_AI') {
        fetch('https://api.example.com/ai', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + request.apiKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: request.prompt })
        }).then(response => response.json())
          .then(data => sendResponse(data))
          .catch(error => sendResponse({ error: error.message }));
        return true;
    }
});
```

### 3. 权限最小化

```json
{
    "permissions": [
        "storage",
        "activeTab",
        "https://api.example.com/*"
    ]
}
```

## 总结

Chrome插件调用AI时需要注意API Key的安全存储、后台脚本隔离和权限最小化。"""
    },
    '如何做模型微调与数据集准备.zh-CN.md': {
        'title': '如何做模型微调与数据集准备',
        'description': '数据集构建、LoRA/QLoRA微调、高效微调策略、系统级大模型微调全流程',
        'date': '2024-07-12T18:09:09+08:00',
        'weight': '6',
        'tags': ['AI面试', '模型微调', 'LoRA', '数据集'],
        'categories': ['AI面试', '技术分享'],
        'photo': 'https://images.unsplash.com/photo-1516414746402-935ce3621729?w=1920&q=80',
        'content': """## 微调流程

> **面试场景**：如何准备高质量的微调数据集？LoRA和QLoRA有什么区别？

## 数据集准备

### 1. 数据格式

```json
{
    "instruction": "解释什么是机器学习",
    "response": "机器学习是一种人工智能技术...",
    "history": []
}
```

### 2. 数据清洗

```python
import json

def clean_dataset(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cleaned = []
    for item in data:
        if len(item['response']) > 10 and len(item['response']) < 2000:
            cleaned.append(item)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
```

### 3. LoRA微调配置

```python
from peft import LoraConfig

lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
```

## 总结

模型微调需要高质量的数据集和合适的参数配置，LoRA是目前最常用的高效微调方法。"""
    },
    '多Agent系统如何设计.zh-CN.md': {
        'title': '多Agent系统如何设计',
        'description': 'Agent协作模式、任务分配、通信机制、冲突解决，复杂多Agent系统设计',
        'date': '2023-10-15T09:20:00+08:00',
        'weight': '5',
        'tags': ['AI面试', '多Agent', '系统设计', '协作'],
        'categories': ['AI面试', '技术分享'],
        'photo': 'https://images.unsplash.com/photo-1559324173-3b4a566a874d?w=1920&q=80',
        'content': """## 系统架构

> **面试场景**：设计一个多Agent协作系统，需要考虑哪些关键问题？

## 协作模式

### 1. 任务分配

```java
public class TaskAllocator {
    private List<Agent> agents;
    
    public Agent allocateTask(Task task) {
        return agents.stream()
            .min(Comparator.comparing(a -> a.getWorkload() + a.getCapabilityScore(task)))
            .orElse(null);
    }
}
```

### 2. 通信协议

```java
public interface Message {
    String getSender();
    String getReceiver();
    MessageType getType();
    Object getContent();
}

public enum MessageType {
    TASK_ASSIGN,
    TASK_COMPLETE,
    STATUS_UPDATE,
    ERROR_REPORT
}
```

### 3. 冲突解决

```java
public class ConflictResolver {
    public Resolution resolve(Conflict conflict) {
        switch (conflict.getType()) {
            case RESOURCE_CONFLICT:
                return resolveResourceConflict(conflict);
            case GOAL_CONFLICT:
                return resolveGoalConflict(conflict);
            default:
                return Resolution.createDefault();
        }
    }
}
```

## 总结

多Agent系统设计需要考虑任务分配、通信机制和冲突解决等关键问题。"""
    },
    'SpringAI如何接入多种模型.zh-CN.md': {
        'title': 'SpringAI如何接入多种模型',
        'description': 'OpenAI、DeepSeek、GLM等多模型接入、统一API封装、模型切换策略',
        'date': '2023-08-20T14:30:00+08:00',
        'weight': '4',
        'tags': ['AI面试', 'SpringAI', '模型接入', 'OpenAI'],
        'categories': ['AI面试', '技术分享'],
        'photo': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1920&q=80',
        'content': """## 多模型接入

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

SpringAI通过统一的API抽象，使得接入多种AI模型变得简单高效。"""
    },
    '429速率限制怎么解决.zh-CN.md': {
        'title': '429速率限制怎么解决',
        'description': '限流策略、重试机制、多Key轮询、请求合并，解决API速率限制问题',
        'date': '2023-07-10T10:00:00+08:00',
        'weight': '3',
        'tags': ['AI面试', '速率限制', '限流', 'API'],
        'categories': ['AI面试', '技术分享'],
        'photo': 'https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=1920&q=80',
        'content': """## 问题分析

> **面试场景**：当调用AI API遇到429错误时，有哪些解决方案？

## 解决方案

### 1. 令牌桶限流

```java
public class TokenBucket {
    private final int capacity;
    private final double refillRate;
    private double tokens;
    private long lastRefillTime;
    
    public TokenBucket(int capacity, double refillRate) {
        this.capacity = capacity;
        this.refillRate = refillRate;
        this.tokens = capacity;
        this.lastRefillTime = System.currentTimeMillis();
    }
    
    public synchronized boolean tryAcquire() {
        refill();
        if (tokens >= 1) {
            tokens--;
            return true;
        }
        return false;
    }
    
    private void refill() {
        long now = System.currentTimeMillis();
        double elapsed = (now - lastRefillTime) / 1000.0;
        tokens = Math.min(capacity, tokens + elapsed * refillRate);
        lastRefillTime = now;
    }
}
```

### 2. 多Key轮询

```java
public class ApiKeyRotator {
    private List<String> apiKeys;
    private int currentIndex = 0;
    
    public synchronized String getNextKey() {
        String key = apiKeys.get(currentIndex);
        currentIndex = (currentIndex + 1) % apiKeys.size();
        return key;
    }
}
```

## 总结

解决429速率限制需要结合限流、重试和多Key轮询等策略。"""
    },
    'RAG召回率低怎么优化.zh-CN.md': {
        'title': 'RAG召回率低怎么优化',
        'description': '向量数据库优化、查询改写、多路召回、重排序，提升RAG系统召回率',
        'date': '2023-01-25T16:45:00+08:00',
        'weight': '7',
        'tags': ['AI面试', 'RAG', '召回率', '向量检索'],
        'categories': ['AI面试', '技术分享'],
        'photo': 'https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=1920&q=80',
        'content': """## 问题诊断

> **面试场景**：RAG系统召回率低可能有哪些原因？如何优化？

## 优化策略

### 1. 查询改写

```python
def rewrite_query(query, history):
    if history:
        context = ' '.join([h['question'] for h in history[-3:]])
        return f"{context}. Now answer: {query}"
    return query
```

### 2. 多路召回

```python
def multi_retrieval(query):
    results = []
    
    vector_results = vector_db.search(query, top_k=5)
    keyword_results = keyword_search(query, top_k=3)
    semantic_results = semantic_search(query, top_k=3)
    
    results.extend(vector_results)
    results.extend(keyword_results)
    results.extend(semantic_results)
    
    return deduplicate_and_rerank(results)
```

### 3. 重排序

```python
from sentence_transformers import CrossEncoder

cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank(query, documents):
    pairs = [[query, doc['content']] for doc in documents]
    scores = cross_encoder.predict(pairs)
    
    scored_docs = list(zip(documents, scores))
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    
    return [doc for doc, _ in scored_docs[:5]]
```

## 总结

RAG召回率优化需要综合运用查询改写、多路召回和重排序等技术。"""
    },
    '大模型如何做本地化部署.zh-CN.md': {
        'title': '大模型如何做本地化部署',
        'description': '模型量化、推理框架选择、资源调度、服务封装，大模型本地化部署实践',
        'date': '2024-03-15T11:00:00+08:00',
        'weight': '9',
        'tags': ['AI面试', '大模型', '本地化部署', '模型量化'],
        'categories': ['AI面试', '技术分享'],
        'photo': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1920&q=80',
        'content': """## 部署方案

> **面试场景**：如何将大语言模型部署到本地环境？需要考虑哪些因素？

## 技术选型

### 1. 模型量化

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

model = AutoModelForCausalLM.from_pretrained(
    "model-name",
    quantization_config=bnb_config
)
```

### 2. 推理框架

```python
from vllm import LLM, SamplingParams

llm = LLM(model="model-name", tensor_parallel_size=2)

sampling_params = SamplingParams(max_tokens=1024)
outputs = llm.generate(["Hello, how are you?"], sampling_params)
```

### 3. 服务封装

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class InferenceRequest(BaseModel):
    prompt: str
    max_tokens: int = 1024

@app.post("/generate")
async def generate(request: InferenceRequest):
    outputs = llm.generate([request.prompt], sampling_params)
    return {"response": outputs[0].outputs[0].text}
```

## 总结

大模型本地化部署需要考虑模型量化、推理框架选择和服务封装等关键环节。"""
    },
}

for filename, info in file_info.items():
    filepath = os.path.join(post_dir, filename)
    
    frontmatter = f"""---
title: "{info['title']}"
description: "{info['description']}"
date: {info['date']}
lastmod: {info['date']}
weight: {info['weight']}
tags:
"""
    
    for tag in info['tags']:
        frontmatter += f"  - {tag}\n"
    
    frontmatter += "categories:\n"
    for cat in info['categories']:
        frontmatter += f"  - {cat}\n"
    
    frontmatter += f"""math: true
mermaid: true
photos:
  - {info['photo']}
---

{info['content']}
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
    
    print(f"Created: {filename}")

print("\nDone!")
