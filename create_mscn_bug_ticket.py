#!/usr/bin/env python3
"""Create Jira Bug issues in the WON China - MarketSmithChina project (MSCN)."""

import argparse
import json
import os
import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

try:
    import requests
except ImportError:
    sys.exit("请先安装依赖: pip install -r requirements.txt")


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"请先设置环境变量 {name}")
    return value


def parse_list(value: str):
    return [item.strip() for item in value.split(",") if item.strip()]


def build_description(description: str) -> dict:
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": description}
                ],
            }
        ],
    }


def get_epic_link_field_id(
    base_url: str,
    email: str,
    api_token: str,
    project_key: str,
    issuetype: str,
) -> str | None:
    url = (
        base_url.rstrip("/")
        + "/rest/api/3/issue/createmeta?projectKeys="
        + project_key
        + "&issuetypeNames="
        + issuetype
        + "&expand=projects.issuetypes.fields"
    )
    response = requests.get(
        url,
        auth=(email, api_token),
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    for project in data.get("projects", []):
        for issue_type in project.get("issuetypes", []):
            if issue_type.get("name") == issuetype:
                for field_id, field in issue_type.get("fields", {}).items():
                    if field.get("name") == "Epic Link":
                        return field_id
    return None


def create_issue(
    base_url: str,
    email: str,
    api_token: str,
    project_key: str,
    summary: str,
    description: str,
    issuetype: str,
    priority: str = None,
    assignee: str = None,
    labels: str = "",
    components: str = "",
    fix_versions: str = "",
    parent: str = "",
) -> dict:
    url = base_url.rstrip("/") + "/rest/api/3/issue"
    fields = {
        "project": {"key": project_key},
        "summary": summary,
        "description": build_description(description),
        "issuetype": {"name": issuetype},
    }
    if priority:
        fields["priority"] = {"name": priority}
    if assignee:
        fields["assignee"] = {"accountId": assignee}
    if labels:
        fields["labels"] = parse_list(labels)
    if components:
        fields["components"] = [{"name": name} for name in parse_list(components)]
    if fix_versions:
        fields["fixVersions"] = [{"name": name} for name in parse_list(fix_versions)]
    if parent:
        epic_field = get_epic_link_field_id(
            base_url=base_url,
            email=email,
            api_token=api_token,
            project_key=project_key,
            issuetype=issuetype,
        )
        if epic_field:
            fields[epic_field] = parent
        else:
            fields["customfield_10008"] = parent
    payload = {"fields": fields}
    print("DEBUG payload:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    response = requests.post(
        url,
        auth=(email, api_token),
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    if response.status_code not in (200, 201):
        raise SystemExit(
            f"创建 Jira issue 失败: {response.status_code}\n{response.text}"
        )
    return response.json()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="在 WON China - MarketSmithChina (MSCN) 下创建 Jira Bug ticket")
    parser.add_argument("--summary", required=True, help="Ticket 标题")
    parser.add_argument("--description", default="", help="Ticket 描述")
    parser.add_argument("--description-file", default="description.txt", help="Description file path，默认 description.txt")
    parser.add_argument("--type", default="Bug", help="Issue Type，默认 Bug")
    parser.add_argument(
        "--project", default="MSCN", help="Jira Project Key，默认 MSCN"
    )
    parser.add_argument(
        "--url",
        default="https://daicompanies.atlassian.net",
        help="Jira 基础 URL，默认 https://daicompanies.atlassian.net",
    )
    parser.add_argument("--priority", default=None, help="Priority, 如 Medium")
    parser.add_argument(
        "--assignee",
        default=None,
        help="Assignee accountId（Jira Cloud），例如 5b10a2844c20165700ede21g",
    )
    parser.add_argument(
        "--labels",
        default="",
        help="Comma-separated labels，例如 bug,backend",
    )
    parser.add_argument(
        "--components",
        default="",
        help="Comma-separated component names",
    )
    parser.add_argument(
        "--fix-versions",
        default="",
        help="Comma-separated fix version names",
    )
    parser.add_argument(
        "--parent",
        default="",
        help="Parent issue key（如 MSCN-123）",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    email = get_env("JIRA_EMAIL")
    api_token = get_env("JIRA_API_TOKEN")
    description = args.description
    if not description and args.description_file and os.path.exists(args.description_file):
        with open(args.description_file, "r", encoding="utf-8") as f:
            description = f.read()

    issue = create_issue(
        base_url=args.url,
        email=email,
        api_token=api_token,
        project_key=args.project,
        summary=args.summary,
        description=description,
        issuetype=args.type,
        priority=args.priority,
        assignee=args.assignee,
        labels=args.labels,
        components=args.components,
        fix_versions=args.fix_versions,
        parent=args.parent,
    )
    issue_key = issue.get("key")
    issue_url = f"{args.url.rstrip('/')}/browse/{issue_key}" if issue_key else None
    print("创建成功:")
    print(f"  Issue Key: {issue_key}")
    if issue_url:
        print(f"  URL: {issue_url}")


if __name__ == "__main__":
    main()
