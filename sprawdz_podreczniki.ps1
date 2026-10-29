$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$manifest = Get-Content -LiteralPath 'podreczniki_start.json' -Raw -Encoding UTF8 | ConvertFrom-Json
$problem = $false
foreach ($item in $manifest) {
    Write-Host "`n$($item.glowny)"
    if (-not (Test-Path -LiteralPath $item.glowny)) {
        Write-Host 'BRAK PLIKU GLOWNEGO' -ForegroundColor Red
        $problem = $true
    } else {
        Get-Item -LiteralPath $item.glowny | Select-Object Name, LastWriteTime, Length | Format-Table
        Write-Host "SHA256: $((Get-FileHash -LiteralPath $item.glowny -Algorithm SHA256).Hash)"
    }
    $known = @($item.archiwum | ForEach-Object { $_.nazwa })
    foreach ($file in Get-ChildItem -File -Filter $item.wzorzec) {
        if ($file.Name -eq $item.glowny) { continue }
        $baseline = $item.archiwum | Where-Object { $_.nazwa -eq $file.Name }
        if ($file.Name -notin $known -or (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash -ne $baseline.sha256) {
            Write-Host "DO POROWNANIA: $($file.Name) - nowa lub zmieniona wersja historyczna." -ForegroundColor Yellow
            $problem = $true
        }
    }
}
git status --short
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if ($problem) { exit 1 }
Write-Host 'Kontrola zakonczona. Przed edycja sprawdz rowniez zmiany plikow glownych w Git.'
