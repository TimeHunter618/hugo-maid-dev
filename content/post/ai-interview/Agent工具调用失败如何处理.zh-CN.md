---
title: "Agent工具调用失败如何处理"
description: "处理工具调用失败的常见策略，系统级Agent工具调用的完整方案"
date: 2026-02-05T04:14:46+08:00
lastmod: 2026-02-05T04:14:46+08:00
weight: 2
tags:
  - AI面试
  - Agent
  - 工具调用
  - 故障处理
categories:
  - AI面试
  - 技术分享
math: true
mermaid: true
photos:
  - https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1920&q=80
---

## 问题背景

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

处理工具调用失败需要综合运用重试、熔断和降级策略，确保系统在面对外部依赖故障时仍能保持可用。
