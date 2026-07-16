import os
import re

post_dir = r"f:\project\go\hugo_extended_withdeploy_0.163.2_windows-amd64\dev4\content\post\ai-interview"

file_info = {
    'Agent工具调用失败如何处理.zh-CN.md': {
        'title': 'Agent工具调用失败如何处理',
        'description': '处理工具调用失败的常见策略，系统级Agent工具调用的完整方案',
        'tags': ['AI面试', 'Agent', '工具调用', '故障处理'],
        'categories': ['AI面试', '技术分享']
    },
    'Chrome插件如何安全调用AI.zh-CN.md': {
        'title': 'Chrome插件如何安全调用AI',
        'description': 'API Key安全、通信协议、隔离机制，AI插件安全实践',
        'tags': ['AI面试', 'Chrome', 'AI安全', '浏览器扩展'],
        'categories': ['AI面试', '技术分享']
    },
    '如何做模型微调与数据集准备.zh-CN.md': {
        'title': '如何做模型微调与数据集准备',
        'description': '数据集构建、LoRA/QLoRA微调、高效微调策略、系统级大模型微调全流程',
        'tags': ['AI面试', '模型微调', 'LoRA', '数据集'],
        'categories': ['AI面试', '技术分享']
    },
    '多Agent系统如何设计.zh-CN.md': {
        'title': '多Agent系统如何设计',
        'description': 'Agent协作模式、任务分配、通信机制、冲突解决，复杂多Agent系统设计',
        'tags': ['AI面试', '多Agent', '系统设计', '协作'],
        'categories': ['AI面试', '技术分享']
    },
    'SpringAI如何接入多种模型.zh-CN.md': {
        'title': 'SpringAI如何接入多种模型',
        'description': 'OpenAI、DeepSeek、GLM等多模型接入、统一API封装、模型切换策略',
        'tags': ['AI面试', 'SpringAI', '模型接入', 'OpenAI'],
        'categories': ['AI面试', '技术分享']
    },
    '429速率限制怎么解决.zh-CN.md': {
        'title': '429速率限制怎么解决',
        'description': '限流策略、重试机制、多Key轮询、请求合并，解决API速率限制问题',
        'tags': ['AI面试', '速率限制', '限流', 'API'],
        'categories': ['AI面试', '技术分享']
    },
    'RAG召回率低怎么优化.zh-CN.md': {
        'title': 'RAG召回率低怎么优化',
        'description': '向量数据库优化、查询改写、多路召回、重排序，提升RAG系统召回率',
        'tags': ['AI面试', 'RAG', '召回率', '向量检索'],
        'categories': ['AI面试', '技术分享']
    },
    '大模型如何做本地化部署.zh-CN.md': {
        'title': '大模型如何做本地化部署',
        'description': '模型量化、推理框架选择、资源调度、服务封装，大模型本地化部署实践',
        'tags': ['AI面试', '大模型', '本地化部署', '模型量化'],
        'categories': ['AI面试', '技术分享']
    },
}

for filename, info in file_info.items():
    filepath = os.path.join(post_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        new_lines = []
        in_frontmatter = False
        frontmatter_end = 0
        
        for i, line in enumerate(lines):
            if line.strip() == '---':
                if in_frontmatter:
                    frontmatter_end = i
                    break
                else:
                    in_frontmatter = True
            new_lines.append(line)
        
        new_frontmatter = f"""---
title: "{info['title']}"
description: "{info['description']}"
date: {lines[3].split(': ')[1] if len(lines) > 3 else '2024-01-01T00:00:00+08:00'}
lastmod: {lines[4].split(': ')[1] if len(lines) > 4 else '2024-01-01T00:00:00+08:00'}
weight: {lines[5].split(': ')[1] if len(lines) > 5 else '1'}
tags:
"""
        
        for tag in info['tags']:
            new_frontmatter += f"  - {tag}\n"
        
        new_frontmatter += "categories:\n"
        for cat in info['categories']:
            new_frontmatter += f"  - {cat}\n"
        
        new_frontmatter += "math: true\nmermaid: true\nphotos:\n"
        
        for i in range(len(lines)):
            if 'photos:' in lines[i]:
                for j in range(i+1, len(lines)):
                    if lines[j].strip() == '---':
                        break
                    if '- ' in lines[j]:
                        new_frontmatter += lines[j] + '\n'
                break
        
        new_frontmatter += '---'
        
        rest_content = '\n'.join(lines[frontmatter_end+1:])
        
        new_content = new_frontmatter + '\n' + rest_content
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Fixed: {filename}")
        
    except Exception as e:
        print(f"Error processing {filename}: {e}")

print("\nDone!")
