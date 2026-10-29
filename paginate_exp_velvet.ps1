param([switch]$GuidesOnly,[switch]$GMOnly)
$ErrorActionPreference='Stop'
$taskPairs=@(
 @('K:\Persona-5-rpg\Persona_5_RPG_Podrecznik_Gracza_0_2.docx','K:\Persona-5-rpg\qa_exp_velvet\player.pdf'),
 @('K:\Persona-5-rpg\Persona_5_RPG_Podrecznik_GM_0_5.docx','K:\Persona-5-rpg\qa_exp_velvet\gm.pdf'),
 @('K:\Persona-5-rpg\Persona_5_RPG_Bestiariusz_0_2.docx','K:\Persona-5-rpg\qa_exp_velvet\bestiary.pdf')
)
if($GuidesOnly) {$taskPairs=$taskPairs[0..1]}
if($GMOnly) {$taskPairs=,($taskPairs[1])}
New-Item -ItemType Directory -Path 'K:\Persona-5-rpg\qa_exp_velvet' -Force | Out-Null
$taskWord=$null;$taskDoc=$null;$taskSummaries=@()
try {
 $taskWord=New-Object -ComObject Word.Application
 $taskWord.Visible=$false;$taskWord.DisplayAlerts=0;$taskWord.AutomationSecurity=3
 foreach($taskPair in $taskPairs) {
  $taskDoc=$taskWord.Documents.Open($taskPair[0],$false,$false,$false)
  Write-Output ('Opened '+$taskPair[0])
  for($taskIndex=1;$taskIndex -le $taskDoc.TablesOfContents.Count;$taskIndex++) {$taskDoc.TablesOfContents.Item($taskIndex).Update()}
  $taskDoc.Repaginate();$null=$taskDoc.Fields.Update()
  for($taskIndex=1;$taskIndex -le $taskDoc.TablesOfContents.Count;$taskIndex++) {$taskDoc.TablesOfContents.Item($taskIndex).UpdatePageNumbers()}
  foreach($taskSection in $taskDoc.Sections) {foreach($taskFooter in $taskSection.Footers) {$null=$taskFooter.Range.Fields.Update()}}
  $taskDoc.Save();Write-Output ('Paginated '+$taskDoc.ComputeStatistics(2)+' pages')
  $taskDoc.ExportAsFixedFormat($taskPair[1],17,$false,0,0,1,1,0,$true,$true,1,$true,$true,$false)
  $taskSummaries += [ordered]@{docx=$taskPair[0];pages=$taskDoc.ComputeStatistics(2);tables=$taskDoc.Tables.Count;contents=$taskDoc.TablesOfContents.Count}
  $taskDoc.Close(0);[void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskDoc);$taskDoc=$null
 }
 $taskSummaries | ConvertTo-Json | Set-Content -LiteralPath 'K:\Persona-5-rpg\qa_exp_velvet\pagination.json' -Encoding utf8
 $taskSummaries | ConvertTo-Json
} finally {
 if($null -ne $taskDoc) {$taskDoc.Close(0);[void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskDoc)}
 if($null -ne $taskWord) {$taskWord.Quit();[void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskWord)}
}
