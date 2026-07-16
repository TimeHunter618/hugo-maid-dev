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

RAG召回率优化需要综合运用查询改写、多路召回和重排序等技术。同时，数据质量和检索方式的选择也至关重要。通过不断的实验和调优，可以显著提升RAG系统的性能。
