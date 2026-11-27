$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
# Kontrola przed edycja. Nie zmienia zadnych plikow.
# Stare wersje podrecznikow sa w historii Git (tag archiwum-przed-porzadkami), nie na dysku.
$main = @('Persona_5_RPG_Podrecznik_GM.docx', 'Persona_5_RPG_Podrecznik_Gracza.docx', 'Persona_5_RPG_Bestiariusz.docx')
$problem = $false
foreach ($name in $main) {
    Write-Host "`n$name"
    if (-not (Test-Path -LiteralPath $name)) {
        Write-Host 'BRAK PLIKU GLOWNEGO' -ForegroundColor Red
        $problem = $true
        continue
    }
    Get-Item -LiteralPath $name | Select-Object Name, LastWriteTime, Length | Format-Table
    Write-Host "SHA256: $((Get-FileHash -LiteralPath $name -Algorithm SHA256).Hash)"
}
# Kazdy inny Word podrecznika to kopia z innej rozmowy albo starsza wersja.
foreach ($file in Get-ChildItem -File -Filter 'Persona_5_RPG_*.docx') {
    if ($file.Name -notin $main) {
        Write-Host "DO POROWNANIA: $($file.Name) - porownaj z plikiem glownym, przenies zmiany i usun kopie." -ForegroundColor Yellow
        $problem = $true
    }
}
Write-Host "`nZmiany w Git:"
git status --short
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if ($problem) { exit 1 }
Write-Host 'Kontrola zakonczona. Przed edycja sprawdz rowniez zmiany plikow glownych w Git.'
