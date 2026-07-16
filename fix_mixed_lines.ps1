$postDir = "f:\project\go\hugo_extended_withdeploy_0.163.2_windows-amd64\dev4\content\post"

$files = Get-ChildItem -Path $postDir -Recurse -Filter "*.zh-CN.md" | 
         Where-Object { $_.FullName -notmatch "\\llm\\" }

foreach ($file in $files) {
    $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
    
    $lines = $content -split "`n"
    $inFrontmatter = $false
    $inTags = $false
    $inCategories = $false
    $newLines = @()
    
    foreach ($line in $lines) {
        if ($line -match '^---') {
            if ($inFrontmatter) {
                $inFrontmatter = $false
                $inTags = $false
                $inCategories = $false
            } else {
                $inFrontmatter = $true
            }
            $newLines += $line
            continue
        }
        
        if ($inFrontmatter) {
            if ($line -match '^\s*tags:\s*$') {
                $inTags = $true
                $inCategories = $false
                $newLines += $line
                continue
            }
            
            if ($line -match '^\s*categories:\s*$') {
                $inCategories = $true
                $inTags = $false
                $newLines += $line
                continue
            }
            
            if (($inTags -or $inCategories) -and $line -match '^\s*-\s*') {
                $trimmed = $line.Trim()
                
                if ($trimmed -match '^-\s*(.+?)\?\s*(math|mermaid|photos|draft|weight):\s*') {
                    $item = "- $($matches[1])"
                    $field = "$($matches[2]): $($line.Substring($line.IndexOf($matches[2]) + $matches[2].Length + 1))"
                    $newLines += "  $item"
                    $newLines += $field
                    continue
                }
                
                if ($trimmed -match '^-\s*(.+?)\?$') {
                    $newLines += "  - $($matches[1])"
                    continue
                }
            }
            
            if ($line -match '^\s*(math|mermaid|photos|draft|weight|date|lastmod|title|description|tags|categories):') {
                $inTags = $false
                $inCategories = $false
            }
        }
        
        $newLines += $line
    }
    
    $fixed = $newLines -join "`n"
    
    if ($content -ne $fixed) {
        [System.IO.File]::WriteAllText($file.FullName, $fixed, [System.Text.Encoding]::UTF8)
        Write-Host "Fixed: $($file.Name)"
    }
}

Write-Host "Done!"