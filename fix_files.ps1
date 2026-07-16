$postDir = "f:\project\go\hugo_extended_withdeploy_0.163.2_windows-amd64\dev4\content\post"

$files = Get-ChildItem -Path $postDir -Recurse -Filter "*.zh-CN.md" | 
         Where-Object { $_.FullName -notmatch "\\llm\\" }

foreach ($file in $files) {
    $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
    
    $lines = $content -split "`n"
    $inFrontmatter = $false
    $frontmatterLines = @()
    $contentLines = @()
    $frontmatterEndIndex = -1
    
    for ($i = 0; $i -lt $lines.Length; $i++) {
        if ($lines[$i] -match '^---') {
            if ($inFrontmatter) {
                $frontmatterEndIndex = $i
                break
            }
            $inFrontmatter = $true
        }
        if ($inFrontmatter) {
            $frontmatterLines += $lines[$i]
        } else {
            $contentLines += $lines[$i]
        }
    }
    
    if ($frontmatterEndIndex -eq -1) {
        continue
    }
    
    for ($i = 0; $i -lt $frontmatterLines.Length; $i++) {
        $line = $frontmatterLines[$i]
        
        if ($line -match '^\s*title:\s*"[^"]*') {
            $line = $line -replace 'title:\s*"([^"]*?)\?\s*$', 'title: "$1"'
            $line = $line -replace 'title:\s*"([^"]*?)\?$', 'title: "$1"'
        }
        
        if ($line -match '^\s*description:\s*"[^"]*') {
            $line = $line -replace 'description:\s*"([^"]*?)\?\s*$', 'description: "$1"'
            $line = $line -replace 'description:\s*"([^"]*?)\?$', 'description: "$1"'
        }
        
        if ($line -match '^\s*-\s*[^"]*\?$') {
            $line = $line -replace '(\s+-\s+[^\n]*?)\?$', '$1'
        }
        
        $frontmatterLines[$i] = $line
    }
    
    $fixedFrontmatter = $frontmatterLines -join "`n"
    $fixedContent = $contentLines -join "`n"
    $fixed = "$fixedFrontmatter`n$fixedContent"
    
    if ($content -ne $fixed) {
        [System.IO.File]::WriteAllText($file.FullName, $fixed, [System.Text.Encoding]::UTF8)
        Write-Host "Fixed: $($file.Name)"
    }
}

Write-Host "Done!"