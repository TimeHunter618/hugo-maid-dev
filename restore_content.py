import os
import subprocess

post_dir = r"f:\project\go\hugo_extended_withdeploy_0.163.2_windows-amd64\dev4\content\post"
repo_dir = r"f:\project\go\hugo_extended_withdeploy_0.163.2_windows-amd64\dev4"
commit = "aa84588"

restored = 0
skipped = 0
errors = 0

for root, dirs, files in os.walk(post_dir):
    dirs[:] = [d for d in dirs if d != 'llm']
    
    for filename in files:
        if not filename.endswith('.zh-CN.md'):
            continue
        if filename == '_index.zh-CN.md':
            continue
            
        filepath = os.path.join(root, filename)
        rel_path = os.path.relpath(filepath, repo_dir).replace('\\', '/')
        
        # Read current content
        with open(filepath, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        current_lines = current_content.strip().split('\n')
        
        # Skip if already has body content (more than 25 lines typically means has body)
        if len(current_lines) > 30:
            skipped += 1
            continue
        
        # Get content from git history
        try:
            result = subprocess.run(
                ['git', 'show', f'{commit}:{rel_path}'],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                print(f"Git error for {filename}: {result.stderr[:100]}")
                errors += 1
                continue
            
            old_content = result.stdout
            
            # Extract body from old content (everything after second ---)
            parts = old_content.split('---')
            if len(parts) >= 3:
                body = '---'.join(parts[2:]).strip()
                
                if body:
                    # Keep current frontmatter, add body
                    new_content = current_content.rstrip() + '\n\n' + body + '\n'
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    restored += 1
                    print(f"Restored: {filename}")
                else:
                    print(f"No body in git for: {filename}")
                    errors += 1
            else:
                print(f"Invalid format in git for: {filename}")
                errors += 1
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            errors += 1

print(f"\n=== Summary ===")
print(f"Restored: {restored}")
print(f"Skipped (already has content): {skipped}")
print(f"Errors: {errors}")
