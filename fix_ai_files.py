import os

post_dir = r"f:\project\go\hugo_extended_withdeploy_0.163.2_windows-amd64\dev4\content\post\ai-interview"

replacements = {
    '\u03b5\u03b9\u03c2\u03b4': '工具调用失败如何处理',
    '\u03b9\u03c0\u03c2\u03c7': '插件如何安全调用',
    '\u0123\u03a3\u03bc\u03c6\u03c9\u03c6': '如何做模型微调与数据集准备',
    '\u03b5\u03c6\u03b9\u03c3\u03c4\u03b5\u03bc\u03c9': '多Agent系统如何设计',
    '\u03a3\u03c0\u03c1\u03b9\u03bd\u03b7': '如何接入多种模型',
    '\u03c9\u03c6\u03c9': '速率限制怎么解决',
    '\u0391\u0393\u0391': '召回率低怎么优化',
    '\u0123\u03bf\u03bb\u03b5\u03b9\u03c6': '大模型如何做本地化部署',
    
    '\u03b5\u03b9\u03c2': '工具调用',
    '\u03b5\u03b9': '工具',
    '\u03b5': '工',
    '\u03c2': '用',
    '\u03bd': '接',
    '\u03a3': '模',
    '\u03c0': '插',
    '\u03bf': '大',
    '\u03c6': '做',
    '\u03bc': '微',
    '\u03c9': '率',
    '\u03b9\u03c0': '插件',
    '\u03b9\u03c3': '系统',
    '\u03c1\u03b9': '入',
    '\u03c4\u03b5': '设',
    '\u03c7': '全',
    '\u0123': '如',
    
    '\u03b5\u03c2\u03b4': '调用失败',
    '\u03a3\u03bc': '模型',
    '\u03bc\u03c6': '微调',
    '\u03c6\u03c9': '数据',
    '\u03c9\u03c6': '准备',
    '\u03b9\u03c0\u03c2': '插件如何',
    '\u03c0\u03c2\u03c7': '安全调用',
    '\u03bf\u03bb': '模型如何',
    '\u03bb\u03b5': '本地化',
    '\u03b5\u03b9\u03c6': '部署',
    '\u0391\u0393': '召回率',
    '\u0393\u0391': '优化',
    '\u03c9\u03c6\u03c9': '限制怎么',
    '\u03c6\u03c9\u03c6': '解决',
}

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

for file in files_to_fix:
    filepath = os.path.join(post_dir, file)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        modified = False
        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
                modified = True
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {file}")
        else:
            print(f"No changes: {file}")
            
    except Exception as e:
        print(f"Error processing {file}: {e}")

print("\nDone!")
