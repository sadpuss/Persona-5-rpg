$ErrorActionPreference = 'Stop'
$taskDocxPath = 'K:\Persona-5-rpg\Persona_5_RPG_Podrecznik_GM_0_3.docx'
$taskPdfPath = 'K:\Persona-5-rpg\qa_gm_0_3\guide.pdf'
$taskReportPath = 'K:\Persona-5-rpg\qa_gm_0_3\word_pagination.json'
New-Item -ItemType Directory -Path 'K:\Persona-5-rpg\qa_gm_0_3' -Force | Out-Null
$taskWord = $null
$taskDocument = $null
try {
    $taskWord = New-Object -ComObject Word.Application
    $taskWord.Visible = $false
    $taskWord.DisplayAlerts = 0
    $taskWord.AutomationSecurity = 3
    $taskDocument = $taskWord.Documents.Open($taskDocxPath, $false, $false, $false)
    Write-Output 'Opened new guide in background Word'
    $taskReplacements = @(
        @('opisuje rozdziały 8 i 9', 'opisują rozdziały 8 i 9'),
        @('rozdział Rozwój cech społecznych', 'sekcja 8.5 Pięć cech społecznych'),
        @('rozdziale Warianty relacji z bohaterami graczy', 'sekcji 9.6 Warianty relacji z bohaterami graczy'),
        @('Nie nadaliśmy mu jeszcze ceny ani zasad dostępności.', 'W katalogu odpowiada mu Chewing Soul. Cenę i dostępność ustala GM dla przygody.'),
        @('Wartości i ograniczenia homebrew w tym rozdziale są autorską propozycją.', 'Wartości i ograniczenia homebrew w podręczniku są autorską adaptacją.')
    )
    foreach ($taskPair in $taskReplacements) {
        $taskRange = $taskDocument.Content
        $taskFind = $taskRange.Find
        $taskFind.ClearFormatting()
        $taskFind.Replacement.ClearFormatting()
        $null = $taskFind.Execute($taskPair[0], $false, $false, $false, $false, $false, $true, 1, $false, $taskPair[1], 2)
    }
    for ($taskIndex = 1; $taskIndex -le $taskDocument.TablesOfContents.Count; $taskIndex++) {
        $taskDocument.TablesOfContents.Item($taskIndex).Update()
    }
    $taskDocument.Repaginate()
    $null = $taskDocument.Fields.Update()
    for ($taskIndex = 1; $taskIndex -le $taskDocument.TablesOfContents.Count; $taskIndex++) {
        $taskDocument.TablesOfContents.Item($taskIndex).UpdatePageNumbers()
    }
    foreach ($taskSection in $taskDocument.Sections) {
        foreach ($taskFooter in $taskSection.Footers) { $null = $taskFooter.Range.Fields.Update() }
    }
    $taskDocument.Save()
    Write-Output 'Updated table of contents and page numbers'
    $taskDocument.ExportAsFixedFormat($taskPdfPath, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
    $taskSummary = [ordered]@{
        pages = $taskDocument.ComputeStatistics(2)
        tables = $taskDocument.Tables.Count
        contents = $taskDocument.TablesOfContents.Count
        bookmarks = $taskDocument.Bookmarks.Count
        words = $taskDocument.ComputeStatistics(0)
        docx = $taskDocxPath
        qaPdf = $taskPdfPath
    }
    $taskSummary | ConvertTo-Json | Set-Content -LiteralPath $taskReportPath -Encoding utf8
    $taskSummary | ConvertTo-Json
} finally {
    if ($null -ne $taskDocument) { $taskDocument.Close(0); [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskDocument) }
    if ($null -ne $taskWord) { $taskWord.Quit(); [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskWord) }
}
