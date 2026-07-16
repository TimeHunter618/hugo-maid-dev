import os

post_dir = r"f:\project\go\hugo_extended_withdeploy_0.163.2_windows-amd64\dev4\content\post"

fixed_count = 0

for root, dirs, files in os.walk(post_dir):
    dirs[:] = [d for d in dirs if d != 'llm']
    
    for file in files:
        if file.endswith('.zh-CN.md'):
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'rb') as f:
                    raw = f.read()
                
                if raw.startswith(b'\xef\xbb\xbf'):
                    content = raw[3:]
                else:
                    content = raw
                
                try:
                    text = content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        text = content.decode('gbk')
                        text = text.replace('???---', '---')
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(text)
                        print(f"Fixed (GBK->UTF-8): {file}")
                        fixed_count += 1
                    except:
                        pass
                        
            except Exception as e:
                print(f"Error processing {file}: {e}")

print(f"\nDone! Total fixed: {fixed_count}")
