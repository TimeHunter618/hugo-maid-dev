$postDir = "f:\project\go\hugo_extended_withdeploy_0.163.2_windows-amd64\dev4\content\post"

$files = Get-ChildItem -Path $postDir -Recurse -Filter "*.zh-CN.md" | 
         Where-Object { $_.FullName -notmatch "\\llm\\" }

$totalFiles = $files.Count
Write-Host "Total files to process: $totalFiles"

$yearDistribution = @(
    @{ Year = 2021; Weight = 0.10 },
    @{ Year = 2022; Weight = 0.15 },
    @{ Year = 2023; Weight = 0.20 },
    @{ Year = 2024; Weight = 0.25 },
    @{ Year = 2025; Weight = 0.20 },
    @{ Year = 2026; Weight = 0.10 }
)

$files = $files | Sort-Object { Get-Random }

$currentIndex = 0
foreach ($dist in $yearDistribution) {
    $year = $dist.Year
    $count = [math]::Round($totalFiles * $dist.Weight)
    
    if ($currentIndex + $count -gt $totalFiles) {
        $count = $totalFiles - $currentIndex
    }
    
    $selectedFiles = $files[$currentIndex..($currentIndex + $count - 1)]
    
    foreach ($file in $selectedFiles) {
        $lines = Get-Content $file.FullName -Encoding UTF8
        
        for ($i = 0; $i -lt $lines.Length; $i++) {
            if ($lines[$i] -match '^\s*date:\s*\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}') {
                if ($year -eq 2026) {
                    $month = Get-Random -Minimum 1 -Maximum 8
                } else {
                    $month = Get-Random -Minimum 1 -Maximum 13
                }
                
                $daysInMonth = [DateTime]::DaysInMonth($year, $month)
                $day = Get-Random -Minimum 1 -Maximum ($daysInMonth + 1)
                
                $hour = Get-Random -Minimum 0 -Maximum 24
                $minute = Get-Random -Minimum 0 -Maximum 60
                
                $dateStr = "{0:0000}-{1:00}-{2:00}T{3:00}:{4:00}:00+08:00" -f $year, $month, $day, $hour, $minute
                
                $lines[$i] = "date: $dateStr"
                $lines[$i + 1] = "lastmod: $dateStr"
                break
            }
        }
        
        [System.IO.File]::WriteAllLines($file.FullName, $lines, [System.Text.Encoding]::UTF8)
        
        Write-Host "Updated: $($file.Name) -> $dateStr"
    }
    
    $currentIndex += $count
    
    if ($currentIndex -ge $totalFiles) {
        break
    }
}

Write-Host "Done! Updated $totalFiles files."