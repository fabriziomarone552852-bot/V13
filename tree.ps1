# Rimuove file risultato precedente
$out = Join-Path -Path (Get-Location) -ChildPath "backend_bundle.txt"
if (Test-Path $out) { Remove-Item $out -Force }

# Trova i file desiderati (esclude .git, venv, node_modules)
Get-ChildItem -Path .\backend -Recurse -File |
  Where-Object {
    ($_.FullName -notmatch '\\.git\\') -and
    ($_.FullName -notmatch '\\node_modules\\') -and
    ($_.FullName -notmatch '\\venv\\') -and
    ($_.Extension -in '.py', '.md', '.txt')
  } |
  Sort-Object FullName |
  ForEach-Object {
    $header = "===== $($_.FullName) =====`r`n"
    Add-Content -Path $out -Value $header
    # Get-Content -Raw per prendere tutto il file come singola stringa
    $text = Get-Content -Path $_.FullName -Raw -ErrorAction Stop
    Add-Content -Path $out -Value $text
    Add-Content -Path $out -Value "`r`n"
  }

Write-Host "Bundle scritto in $out"