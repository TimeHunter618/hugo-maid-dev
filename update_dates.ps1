$postDir = "f:\project\go\hugo_extended_withdeploy_0.163.2_windows-amd64\dev4\content\post"

$files = Get-ChildItem -Path $postDir -Recurse -Filter "*.zh-CN.md" | 
         Where-Object { $_.FullName -notmatch "\\llm\\" }

$yearDistribution = @(
    @{ Year = 2021; Weight = 0.10 },
    @{ Year = 2022; Weight = 0.15 },
    @{ Year = 2023; Weight = 0.20 },
    @{ Year = 2024; Weight = 0.25 },
    @{ Year = 2025; Weight = 0.20 },
    @{ Year = 2026; Weight = 0.10 }
)

$fileCount = $files.Count
Write-Host "Total files to update: $fileCount"

$random = New-Object System.Random

foreach ($file in $files) {
    $r = $random.NextDouble()
    $cumulative = 0
    $selectedYear = 2024
    
    foreach ($yearItem in $yearDistribution) {
        $cumulative += $yearItem.Weight
        if ($r -lt $cumulative) {
            $selectedYear = $yearItem.Year
            break
        }
    }
    
    if ($selectedYear -eq 2026) {
        $month = $random.Next(1, 7)
    } else {
        $month = $random.Next(1, 13)
    }
    
    $daysInMonth = [DateTime]::DaysInMonth($selectedYear, $month)
    $day = $random.Next(1, $daysInMonth + 1)
    $hour = $random.Next(0, 24)
    $minute = $random.Next(0, 60)
    $second = $random.Next(0, 60)
    
    $dateStr = "{0:0000}-{1:00}-{2:00}T{3:00}:{4:00}:{5:00}+08:00" -f $selectedYear, $month, $day, $hour, $minute, $second
    
    $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
    $lines = $content -split "`n"
    
    for ($i = 0; $i -lt $lines.Length; $i++) {
        if ($lines[$i] -match '^\s*date:\s*\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}') {
            $lines[$i] = "date: $dateStr"
            if ($i + 1 -lt $lines.Length -and $lines[$i + 1] -match '^\s*lastmod:') {
                $lines[$i + 1] = "lastmod: $dateStr"
            }
            break
        }
    }
    
    $fixed = $lines -join "`n"
    [System.IO.File]::WriteAllText($file.FullName, $fixed, [System.Text.Encoding]::UTF8)
    
    Write-Host "Updated: $($file.Name) -> $selectedYear"
}

Write-Host "Done!"