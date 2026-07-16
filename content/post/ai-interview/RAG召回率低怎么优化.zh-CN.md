---
title: "RAG召回率低怎么优化"
description: "向量数据库优化、查询改写、多路召回、重排序，提升RAG系统召回率"
date: 2023-01-25T16:45:00+08:00
lastmod: 2023-01-25T16:45:00+08:00
weight: 7
tags:
  - AI面试
  - RAG
  - 召回率
  - 向量检索
categories:
  - AI面试
  - 技术分享
math: true
mermaid: true
photos:
  - https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=1920&q=80
---

## 问题诊断

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

RAG召回率优化需要综合运用查询改写、多路召回和重排序等技术。
