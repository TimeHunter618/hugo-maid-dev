import os

post_dir = r"f:\project\go\hugo_extended_withdeploy_0.163.2_windows-amd64\dev4\content\post\ai-interview"

files_to_fix = [
    'Agent工具调用失败如何处理.zh-CN.md',
    'Chrome插件如何安全调用AI.zh-CN.md',
    '如何做模型微调与数据集准备.zh-CN.md',
    '多Agent系统如何设计.zh-CN.md',
    'SpringAI如何接入多种模型.zh-CN.md',
    '429速率限制怎么解决.zh-CN.md',
    'RAG召回率低怎么优化.zh-CN.md',
    '大模型如何做本地化部署.zh-CN.md',
]

for filename in files_to_fix:
    filepath = os.path.join(post_dir, filename)
    try:
        with open(filepath, 'rb') as f:
            raw = f.read()
        
        if raw.startswith(b'\xef\xbb\xbf'):
            content = raw[3:]
        else:
            content = raw
        
        text = content.decode('gbk', errors='replace')
        
        text = text.replace('???---', '---')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"Fixed: {filename}")
        
    except Exception as e:
        print(f"Error processing {filename}: {e}")

print("\nDone!")
