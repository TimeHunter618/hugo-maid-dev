---
title: "Chrome插件如何安全调用AI"
description: "API Key安全、通信协议、隔离机制，AI插件安全实践"
date: 2025-02-03T11:35:15+08:00
lastmod: 2025-02-03T11:35:15+08:00
weight: 8
tags:
  - AI面试
  - Chrome
  - AI安全
  - 浏览器扩展
categories:
  - AI面试
  - 技术分享
math: true
mermaid: true
photos:
  - https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1920&q=80
---

## 安全挑战

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

Chrome插件调用AI时需要注意API Key的安全存储、后台脚本隔离和权限最小化。
