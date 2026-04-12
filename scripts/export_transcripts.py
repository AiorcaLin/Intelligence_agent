"""Export subagent JSONL transcripts to readable Markdown files."""

import json
import html
import sys
from pathlib import Path

AGENTS = [
    {
        "id": "0b7bfe46-b485-498b-9bcf-c2e5f76ed727",
        "name": "Agent1_Backend_FastAPI",
        "title": "Agent 1: 后端开发 — FastAPI + Models + Routers + Services",
    },
    {
        "id": "03fab152-4283-44d5-a9a2-d736dd87dc9c",
        "name": "Agent2_AgentEngine_GTRME",
        "title": "Agent 2: Agent引擎 — GTRME + LangGraph + 数据源工具",
    },
    {
        "id": "b9f0b7bb-7a72-4151-84b0-690007ae0f5d",
        "name": "Agent3_Frontend_NextJS",
        "title": "Agent 3: 前端开发 — Next.js + 所有页面 + 组件",
    },
    {
        "id": "d1a21e1a-5b1d-4532-b483-73ad8970a4f4",
        "name": "Agent4_Configs_Scripts",
        "title": "Agent 4: 配置/脚本 — 域配置 + 分发 + 媒体 + 脚本",
    },
]

TRANSCRIPT_BASE = Path(
    r"C:\Users\Lenovo\.cursor\projects\e-AI-Intelligence-agent"
    r"\agent-transcripts\c0053be0-7157-4541-800b-d5a5ff5d737e\subagents"
)

OUTPUT_DIR = Path(
    r"e:\AI\Intelligence_agent\docs\phased_documents"
    r"\cursor_claude_opus_4_dot_6_high"
)


def parse_jsonl(filepath: Path) -> list[dict]:
    entries = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def _truncate(text: str, max_len: int = 5000) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + f"\n\n... (truncated, total: {len(text)} chars)"


def _extract_content_blocks(entry: dict) -> list:
    """Extract content blocks from entry, handling nested message structure."""
    msg = entry.get("message", {})
    if isinstance(msg, dict):
        content = msg.get("content", [])
    else:
        content = entry.get("content", [])

    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return content
    return []


def format_transcript(agent_info: dict, entries: list[dict]) -> str:
    lines = [
        f"# {agent_info['title']}",
        "",
        f"**Subagent ID**: `{agent_info['id']}`  ",
        f"**Parent Session**: `c0053be0-7157-4541-800b-d5a5ff5d737e`  ",
        f"**总条目数**: {len(entries)}",
        "",
        "---",
        "",
    ]

    step = 0
    write_count = 0
    files_created = []

    for entry in entries:
        role = entry.get("role", "unknown")
        blocks = _extract_content_blocks(entry)

        if role == "user":
            step += 1
            lines.append(f"## Step {step}: User Prompt")
            lines.append("")
            for block in blocks:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = block.get("text", "")
                    lines.append("```")
                    lines.append(_truncate(text, 3000))
                    lines.append("```")
                    lines.append("")

        elif role == "assistant":
            step += 1
            has_text = False
            has_tools = False

            for block in blocks:
                if not isinstance(block, dict):
                    continue

                if block.get("type") == "text":
                    text = block.get("text", "").strip()
                    if text:
                        if not has_text:
                            lines.append(f"## Step {step}: Assistant")
                            lines.append("")
                            has_text = True
                        lines.append(_truncate(text))
                        lines.append("")

                elif block.get("type") == "tool_use":
                    has_tools = True
                    tool_name = block.get("name", "unknown")
                    tool_input = block.get("input", {})

                    if not has_text:
                        lines.append(f"## Step {step}: Assistant")
                        lines.append("")
                        has_text = True

                    if tool_name == "Write":
                        write_count += 1
                        fpath = tool_input.get("path", "")
                        content = tool_input.get("contents", "")
                        short_path = fpath.replace("e:\\AI\\Intelligence_agent\\", "")
                        files_created.append(short_path)
                        lines.append(f"### File Write #{write_count}: `{short_path}`")
                        lines.append("")
                        lines.append(f"**Size**: {len(content)} chars")
                        lines.append("")
                        lines.append("```")
                        lines.append(_truncate(content, 8000))
                        lines.append("```")
                        lines.append("")

                    elif tool_name == "Shell":
                        cmd = tool_input.get("command", "")
                        desc = tool_input.get("description", "")
                        lines.append(f"**Shell**: {desc}")
                        lines.append(f"```bash\n{_truncate(cmd, 500)}\n```")
                        lines.append("")

                    elif tool_name == "Read":
                        fpath = tool_input.get("path", "")
                        short_path = fpath.replace("e:\\AI\\Intelligence_agent\\", "")
                        lines.append(f"**Read**: `{short_path}`")
                        lines.append("")

                    elif tool_name == "StrReplace":
                        fpath = tool_input.get("path", "")
                        short_path = fpath.replace("e:\\AI\\Intelligence_agent\\", "")
                        old = tool_input.get("old_string", "")[:100]
                        lines.append(f"**StrReplace**: `{short_path}`")
                        lines.append(f"- Old: `{old}...`")
                        lines.append("")

                    elif tool_name == "TodoWrite":
                        todos = tool_input.get("todos", [])
                        todo_summary = ", ".join(
                            f"[{t.get('status', '?')}] {t.get('content', '')[:40]}"
                            for t in todos[:5]
                        )
                        lines.append(f"**TodoWrite**: {todo_summary}")
                        lines.append("")

                    else:
                        inp_preview = json.dumps(tool_input, ensure_ascii=False)[:300]
                        lines.append(f"**{tool_name}**: {inp_preview}")
                        lines.append("")

    # Summary section
    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total entries**: {len(entries)}")
    lines.append(f"- **Files written**: {write_count}")
    lines.append("")
    if files_created:
        lines.append("### Files Created")
        lines.append("")
        for f in files_created:
            lines.append(f"- `{f}`")
        lines.append("")

    return "\n".join(lines)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for agent in AGENTS:
        jsonl_path = TRANSCRIPT_BASE / f"{agent['id']}.jsonl"
        if not jsonl_path.exists():
            print(f"[SKIP] {agent['name']}: file not found")
            continue

        entries = parse_jsonl(jsonl_path)
        markdown = format_transcript(agent, entries)

        out_path = OUTPUT_DIR / f"{agent['name']}_transcript.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        size_kb = len(markdown.encode("utf-8")) / 1024
        print(f"[OK] {agent['name']}: {len(entries)} entries -> {out_path.name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
