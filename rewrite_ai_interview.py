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

在实际的Agent系统中，工具调用失败是不可避免的。可能的原因包括：网络超时、API限流、服务宕机、参数错误等。一个健壮的系统需要能够优雅地处理这些失败情况。

## 核心策略

### 1. 重试机制

**面试思路**：首先要考虑哪些异常值得重试，哪些不需要重试。比如网络超时、服务暂时不可用适合重试；但参数错误、认证失败等业务逻辑错误重试是没有意义的。

**重试策略要点**：

- **指数退避**：每次重试的间隔时间应该递增，避免在服务恢复前持续冲击
- **最大重试次数**：设置上限，防止无限循环
- **抖动**：在退避时间基础上添加随机抖动，避免多个请求同时重试

```java
public class ToolRetryHandler {
    private static final int MAX_RETRIES = 3;
    private static final long BASE_DELAY_MS = 1000;
    
    public <T> T executeWithRetry(ToolCall<T> toolCall) throws ToolException {
        Exception lastException = null;
        for (int attempt = 1; attempt <= MAX_RETRIES; attempt++) {
            try {
                return toolCall.execute();
            } catch (TransientException e) {
                lastException = e;
                long delay = BASE_DELAY_MS * (long) Math.pow(2, attempt - 1);
                Thread.sleep(delay);
            }
        }
        throw new ToolException("Max retries exceeded", lastException);
    }
}
```

**关键点**：区分瞬时异常（TransientException）和永久异常。只有瞬时异常才需要重试。

### 2. 熔断机制

**面试思路**：当某个工具持续失败时，继续重试只会浪费资源并加重服务负担。熔断机制可以在检测到服务不可用时快速失败，给服务恢复的时间。

**熔断状态机**：

- **关闭状态**：正常处理请求
- **打开状态**：检测到连续失败后打开，直接拒绝请求
- **半开状态**：经过冷却时间后，允许少量请求测试服务是否恢复

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

**关键点**：熔断机制需要与监控系统配合，及时发现服务异常并恢复。

### 3. 降级策略

**面试思路**：当主服务不可用时，能否提供一个降级方案？比如返回缓存数据、使用备用服务、或者返回默认值。

**降级方案类型**：

- **缓存降级**：返回最近的缓存结果
- **备用服务降级**：切换到备用服务
- **默认值降级**：返回预设的默认值
- **静默失败**：记录日志，然后优雅地失败

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

**关键点**：降级方案需要提前设计，并且要考虑降级后的用户体验。

## 面试回答框架

当面试官问到这个问题时，可以按照以下框架回答：

1. **分层处理**：重试 -> 熔断 -> 降级，三层递进
2. **异常分类**：区分瞬时异常和永久异常
3. **具体策略**：指数退避、状态机、缓存备用
4. **监控告警**：配合监控系统及时发现和处理问题
5. **用户体验**：降级方案要保证基本功能可用

## 总结

处理工具调用失败需要综合运用重试、熔断和降级策略，确保系统在面对外部依赖故障时仍能保持可用。关键是要区分不同类型的失败，采取合适的处理方式，同时做好监控和告警。"""
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

Chrome插件的安全问题尤为重要，因为插件可以访问用户的浏览数据。如果API Key泄露，可能导致：API费用被滥用、用户数据被泄露、服务被恶意调用等问题。

## 安全策略

### 1. API Key保护

**面试思路**：API Key不能明文存储在前端代码中，也不能通过网络明文传输。需要使用安全的存储方式和传输协议。

**存储方案**：

- **chrome.storage.local**：使用浏览器提供的本地存储，比localStorage更安全
- **加密存储**：对API Key进行加密后再存储
- **不要硬编码**：绝对不能把API Key写在代码中

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

**关键点**：storage.local虽然比localStorage安全，但仍然可能被其他扩展或恶意脚本访问。更安全的做法是使用后台脚本作为代理。

### 2. 后台脚本隔离

**面试思路**：将敏感操作放在后台脚本中执行，可以隔离来自网页的恶意代码访问。

**隔离策略**：

- **后台脚本**：所有API调用都在background script中执行
- **消息通信**：通过chrome.runtime.sendMessage进行通信
- **参数验证**：在后台脚本中对所有输入进行验证

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

**关键点**：后台脚本可以访问所有扩展权限，但不会被网页脚本直接访问，提供了一层安全隔离。

### 3. 权限最小化

**面试思路**：遵循最小权限原则，只请求必要的权限。

**权限策略**：

- **host permissions**：只允许访问必要的API域名
- **activeTab**：只在当前活动标签页生效
- **storage**：只请求存储权限

```json
{
    "permissions": [
        "storage",
        "activeTab",
        "https://api.example.com/*"
    ]
}
```

**关键点**：减少权限可以降低安全风险，即使插件被攻击，攻击者能做的事情也有限。

## 面试回答框架

当面试官问到这个问题时，可以按照以下框架回答：

1. **存储安全**：加密存储、使用chrome.storage、避免硬编码
2. **传输安全**：HTTPS、后台脚本代理
3. **隔离机制**：content script与background script分离
4. **权限控制**：最小权限原则、细粒度权限配置
5. **输入验证**：在后台脚本中验证所有输入

## 总结

Chrome插件调用AI时需要注意API Key的安全存储、后台脚本隔离和权限最小化。同时，要做好输入验证和错误处理，防止恶意用户滥用插件功能。"""
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

模型微调是将预训练模型适配到特定任务的过程。数据集质量直接影响微调效果，而选择合适的微调方法可以显著降低资源消耗。

## 数据集准备

### 1. 数据格式

**面试思路**：不同的模型和框架要求不同的数据格式。常见的格式有JSON、CSV、Parquet等。

**通用数据格式**：

```json
{
    "instruction": "解释什么是机器学习",
    "response": "机器学习是一种人工智能技术，让计算机从数据中学习规律...",
    "history": [],
    "input": ""
}
```

**格式要点**：

- **instruction**：任务指令
- **response**：期望的输出
- **history**：对话历史（适用于多轮对话）
- **input**：额外的输入信息

### 2. 数据清洗

**面试思路**：数据质量是微调成功的关键。需要去除噪声数据、过滤低质量样本、统一格式。

**清洗步骤**：

1. **去重**：去除重复样本
2. **过滤**：过滤长度过短或过长的样本
3. **格式统一**：确保所有样本格式一致
4. **质量评估**：人工抽查或自动评估

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

**关键点**：数据清洗是一个迭代过程，需要不断优化清洗规则。

### 3. LoRA微调配置

**面试思路**：LoRA（Low-Rank Adaptation）是一种高效的微调方法，通过冻结预训练模型权重，只训练低秩矩阵来适配新任务。

**LoRA与QLoRA的区别**：

| 特性 | LoRA | QLoRA |
|------|------|-------|
| 量化 | 不量化 | 4-bit/8-bit量化 |
| 显存占用 | 中等 | 低 |
| 训练速度 | 中等 | 快 |
| 模型精度 | 高 | 接近全精度 |

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

**参数说明**：

- **r**：低秩矩阵的秩，通常取8或16
- **lora_alpha**：缩放因子，通常是r的4倍
- **target_modules**：需要微调的模块，通常是注意力层的q_proj和v_proj
- **lora_dropout**：dropout比例

## 面试回答框架

当面试官问到这个问题时，可以按照以下框架回答：

1. **数据收集**：确定数据源、收集足够样本
2. **数据清洗**：去重、过滤、格式统一
3. **数据格式**：选择合适的格式、构建训练样本
4. **选择微调方法**：LoRA vs QLoRA vs Full Fine-tuning
5. **配置参数**：秩、学习率、batch size等
6. **训练与评估**：监控loss、验证效果

## 总结

模型微调需要高质量的数据集和合适的参数配置。LoRA是目前最常用的高效微调方法，而QLoRA通过量化进一步降低了显存需求。数据清洗是整个流程中最耗时但最重要的环节。"""
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

多Agent系统是指由多个自主Agent组成的系统，它们通过协作完成复杂任务。常见的应用场景包括：智能客服、代码生成、数据分析等。

## 协作模式

### 1. 任务分配

**面试思路**：如何将复杂任务合理分配给各个Agent？需要考虑Agent的能力、当前负载和任务优先级。

**分配策略**：

- **能力匹配**：根据Agent的专长分配任务
- **负载均衡**：避免某个Agent过载
- **优先级调度**：高优先级任务优先分配

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

**关键点**：任务分配需要动态调整，根据Agent的实时状态进行调度。

### 2. 通信协议

**面试思路**：Agent之间如何高效通信？需要定义统一的消息格式和通信协议。

**消息类型**：

- **任务分配**：管理者向执行者分配任务
- **任务完成**：执行者向管理者报告任务完成
- **状态更新**：Agent向系统报告自身状态
- **错误报告**：Agent报告异常情况

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

**通信模式**：

- **同步通信**：请求-响应模式
- **异步通信**：发布-订阅模式
- **点对点通信**：直接消息传递

### 3. 冲突解决

**面试思路**：当多个Agent竞争同一资源或目标冲突时，如何解决？

**冲突类型**：

- **资源冲突**：多个Agent需要同一资源
- **目标冲突**：Agent的目标相互矛盾
- **通信冲突**：消息传递顺序导致不一致

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

**解决策略**：

- **优先级策略**：根据优先级决定资源分配
- **协商策略**：Agent之间协商解决
- **仲裁策略**：由中央管理者决定

## 面试回答框架

当面试官问到这个问题时，可以按照以下框架回答：

1. **系统架构**：分层架构、角色分工
2. **任务分配**：能力匹配、负载均衡、优先级
3. **通信机制**：消息格式、通信模式、协议设计
4. **冲突解决**：冲突类型识别、解决策略
5. **监控与协调**：全局状态管理、异常处理
6. **扩展性**：如何添加新Agent、如何扩展系统

## 总结

多Agent系统设计需要考虑任务分配、通信机制和冲突解决等关键问题。一个良好设计的系统应该具备灵活性、可扩展性和容错能力，能够适应不同的业务场景和需求变化。"""
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

SpringAI通过统一的API抽象，使得接入多种AI模型变得简单高效。开发者可以专注于业务逻辑，而不需要关心底层模型的差异。同时，SpringAI还提供了丰富的功能，如向量数据库集成、函数调用等，是构建AI应用的优秀选择。"""
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

429错误表示请求过于频繁，超出了API的速率限制。这是API调用中常见的问题，需要合理的策略来应对。

## 解决方案

### 1. 令牌桶限流

**面试思路**：在客户端实现限流，避免触发服务端的速率限制。

**令牌桶原理**：

- 系统以固定速率向桶中添加令牌
- 每次请求需要消耗一个令牌
- 如果桶中没有令牌，则请求需要等待或被拒绝

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

**关键点**：令牌桶算法可以平滑处理突发流量，同时保证长期的平均速率。

### 2. 多Key轮询

**面试思路**：当单个API Key达到限制时，切换到备用Key。

**轮询策略**：

- **顺序轮询**：按顺序使用每个Key
- **加权轮询**：根据Key的配额加权选择
- **故障转移**：当某个Key被限流时自动切换

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

**关键点**：需要监控每个Key的使用情况，及时发现被限流的Key。

### 3. 请求合并

**面试思路**：将多个小请求合并成一个大请求，减少请求次数。

**合并策略**：

- **时间窗口合并**：在一定时间内收集请求，然后批量发送
- **结果缓存**：缓存重复请求的结果
- **批量接口**：使用API提供的批量接口

## 面试回答框架

当面试官问到这个问题时，可以按照以下框架回答：

1. **限流策略**：令牌桶、漏桶算法
2. **重试机制**：指数退避、抖动策略
3. **多Key轮询**：Key管理、故障转移
4. **请求合并**：批量请求、缓存策略
5. **监控告警**：实时监控、及时调整
6. **成本优化**：合理规划配额、选择合适的服务等级

## 总结

解决429速率限制需要结合限流、重试和多Key轮询等策略。在客户端实现限流可以从根本上避免触发速率限制，而多Key轮询和请求合并可以提高系统的吞吐量。同时，需要做好监控和告警，及时发现和处理问题。"""
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

RAG（Retrieval-Augmented Generation）系统的召回率直接影响生成质量。召回率低通常意味着相关文档没有被正确检索到。

## 优化策略

### 1. 查询改写

**面试思路**：用户的原始查询可能不够精确，需要进行改写以提高检索效果。

**改写方法**：

- **关键词扩展**：添加同义词、近义词
- **上下文融合**：结合对话历史
- **意图识别**：理解用户的真实意图

```python
def rewrite_query(query, history):
    if history:
        context = ' '.join([h['question'] for h in history[-3:]])
        return f"{context}. Now answer: {query}"
    return query
```

**关键点**：查询改写需要理解用户意图，可以使用小模型来完成这个任务。

### 2. 多路召回

**面试思路**：单一的检索方式可能无法覆盖所有相关文档，需要使用多种检索策略。

**检索方式**：

- **向量检索**：基于语义相似度
- **关键词检索**：基于精确匹配
- **语义检索**：基于语义理解
- **混合检索**：结合多种方式

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

**关键点**：多路召回可以提高召回率，但需要做好去重和重排序。

### 3. 重排序

**面试思路**：检索结果可能包含不相关的文档，需要进行重排序以提高相关性。

**排序方法**：

- **交叉编码器**：使用专门的排序模型
- **规则排序**：基于关键词匹配、位置等规则
- **机器学习排序**：训练排序模型

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

**关键点**：重排序可以显著提高检索质量，但会增加延迟。

## 面试回答框架

当面试官问到这个问题时，可以按照以下框架回答：

1. **问题诊断**：分析召回率低的原因（查询质量、检索方式、数据质量）
2. **查询优化**：查询改写、关键词扩展、意图识别
3. **检索策略**：多路召回、混合检索
4. **重排序**：交叉编码器、机器学习排序
5. **数据优化**：文档分割、向量化优化、数据质量提升
6. **评估指标**：召回率、精确率、MRR等

## 总结

RAG召回率优化需要综合运用查询改写、多路召回和重排序等技术。同时，数据质量和检索方式的选择也至关重要。通过不断的实验和调优，可以显著提升RAG系统的性能。"""
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

大模型本地化部署是指将模型部署在企业内部或本地服务器上，而不是使用云端API。这对于数据隐私、延迟敏感和成本控制等场景非常重要。

## 技术选型

### 1. 模型量化

**面试思路**：大模型通常需要大量显存，量化可以显著降低显存需求。

**量化类型**：

- **4-bit量化**：将权重从FP16压缩到4-bit，显存减少75%
- **8-bit量化**：将权重从FP16压缩到8-bit，显存减少50%
- **GPTQ量化**：基于梯度的量化方法，精度损失更小

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

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

**量化权衡**：

- **显存占用**：量化可以大幅降低显存需求
- **推理速度**：4-bit量化可能稍慢，但8-bit量化通常更快
- **模型精度**：量化会有一定的精度损失，但在大多数任务上影响不大

### 2. 推理框架

**面试思路**：选择合适的推理框架可以显著提升性能。

**框架对比**：

| 框架 | 特点 | 适用场景 |
|------|------|----------|
| vLLM | 高吞吐、连续批处理 | 高并发服务 |
| TGI | HuggingFace官方、功能全面 | 通用场景 |
| llama.cpp | 轻量级、跨平台 | 边缘设备 |

```python
from vllm import LLM, SamplingParams

llm = LLM(model="model-name", tensor_parallel_size=2)

sampling_params = SamplingParams(max_tokens=1024)
outputs = llm.generate(["Hello, how are you?"], sampling_params)
```

**选择建议**：

- **高并发场景**：选择vLLM
- **功能全面**：选择TGI
- **边缘设备**：选择llama.cpp

### 3. 服务封装

**面试思路**：将模型封装为API服务，方便外部调用。

**封装方式**：

- **REST API**：使用FastAPI或Flask
- **gRPC**：高性能RPC框架
- **WebSocket**：支持流式输出

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

**服务特性**：

- **请求队列**：避免请求过多导致服务崩溃
- **健康检查**：定期检查模型状态
- **日志监控**：记录请求和响应信息

## 面试回答框架

当面试官问到这个问题时，可以按照以下框架回答：

1. **模型选择**：根据需求选择合适的模型大小和类型
2. **量化方案**：4-bit/8-bit量化、GPTQ/AWQ
3. **推理框架**：vLLM/TGI/llama.cpp
4. **服务封装**：REST API/gRPC/WebSocket
5. **资源配置**：GPU显存、CPU核心、内存
6. **监控运维**：日志、告警、自动扩展

## 总结

大模型本地化部署需要考虑模型量化、推理框架选择和服务封装等关键环节。通过合理的技术选型和优化，可以在保证性能的同时降低成本和延迟，满足企业的实际需求。"""
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
