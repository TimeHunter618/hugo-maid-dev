$postDir = "f:\project\go\hugo_extended_withdeploy_0.163.2_windows-amd64\dev4\content\post"

$files = Get-ChildItem -Path $postDir -Recurse -Filter "*.zh-CN.md" | 
         Where-Object { $_.FullName -notmatch "\\llm\\" }

foreach ($file in $files) {
    $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
    
    if ($content -match '^---\s*\n' -and $content -notmatch '\n---\s*$') {
        $lines = $content -split "`n"
        $lastLine = $lines[-1].Trim()
        if ($lastLine -ne '---') {
            $content = $content.TrimEnd() + "`n---`n"
            [System.IO.File]::WriteAllText($file.FullName, $content, [System.Text.Encoding]::UTF8)
            Write-Host "Fixed: $($file.FullName)"
        }
    }
}

Write-Host "Done!"