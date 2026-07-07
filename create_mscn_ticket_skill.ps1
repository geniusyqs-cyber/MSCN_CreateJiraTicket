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
  --summary 'Fix Weekend Full Pattern Refresh Failure – Optimize Performance & Batch Submission Strategy' `
  --description "$desc" `
  --type "Story" `
  --project "MSCN" `
  --priority "High (migrated)" `
  --assignee "5a0131d993915e620920fe68" `
  --components "MSCN-DATA" `
  --parent "MSCN-2738" `
  --timeout 60 `
  --retries 3
