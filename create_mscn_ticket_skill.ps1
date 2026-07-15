param(
    [string]$DescriptionFile = ".\description.txt"
)

if (-not (Test-Path $DescriptionFile)) {
    Write-Error "Description file not found: $DescriptionFile"
    exit 1
}

if (-not $env:JIRA_API_TOKEN) {
    Write-Error "环境变量 JIRA_API_TOKEN 未设置。请先设置后再运行。"
    exit 1
}

if (-not $env:JIRA_EMAIL) {
    Write-Error "环境变量 JIRA_EMAIL 未设置。请先设置后再运行。"
    exit 1
}

$desc = Get-Content $DescriptionFile -Raw

python .\create_mscn_ticket.py `
  --summary 'Research: Improve Buy Range Stock Discovery Experience' `
  --description "$desc" `
  --type "Story" `
  --project "MSCN" `
  --priority "High (migrated)" `
  --assignee "712020:54f5668e-24e9-49c7-bbfd-ed91b447070d" `
  --components "MSCN" `
  --parent "MSCN-2738" `
  --timeout 60 `
  --retries 3
