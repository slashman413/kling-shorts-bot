"""
Discord webhook notification script.
Reads output/summary.json and sends an embed to Discord.
Uses urllib only — no external dependencies.
"""
import json
import os
import urllib.request
from pathlib import Path


def build_success_embed(summary: dict) -> dict:
    """Build a success embed with each Short's info."""
    uploads = summary.get("uploads", [])
    count = len(uploads)
    fields = []

    for i, u in enumerate(uploads):
        title_clean = u["title"].replace("#Shorts", "").strip()
        fields.append({
            "name": f"🎬 #{i+1}",
            "value": f"[{title_clean[:40]}]({u['url']})\n`{u['hook_type'][:20]}`",
            "inline": True,
        })

    return {
        "title": "🎬 Shorts 每日生產報告",
        "description": f"✅ 成功上傳 **{count}** 支 Shorts 到 YouTube！",
        "color": 0x00FF88,
        "fields": fields[:24],
        "footer": {
            "text": f"📅 {summary['date']} | 📊 {summary['total_videos_completed']} generated",
        },
        "url": summary.get("channel_url", ""),
    }


def build_failure_embed(status: str) -> dict:
    """Build a failure alert embed."""
    return {
        "title": "❌ Shorts 生產失敗",
        "description": f"Pipeline 狀態: **{status}**\n請檢查 GitHub Actions logs。",
        "color": 0xFF4444,
        "footer": {"text": "🚨 需要手動介入"},
    }


def send_webhook(webhook_url: str, payload: dict) -> bool:
    """Send a JSON payload to a Discord webhook URL."""
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Hermes-ShortsBot/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"[Discord] ✅ Sent ({resp.status})")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        print(f"[Discord] ❌ HTTP {e.code}: {body}")
        # Fallback: try curl
        return _send_with_curl(webhook_url, payload)
    except Exception as e:
        print(f"[Discord] ❌ {e}")
        return _send_with_curl(webhook_url, payload)


def _send_with_curl(webhook_url: str, payload: dict) -> bool:
    """Fallback: send webhook via curl (works on more environments)."""
    import subprocess, tempfile
    tmp = Path(tempfile.mktemp(suffix=".json"))
    try:
        tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        result = subprocess.run(
            ["curl", "-s", "-H", "Content-Type: application/json",
             "-d", f"@{tmp}", webhook_url],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            print("[Discord] ✅ Sent (via curl)")
            return True
        print(f"[Discord] ❌ curl failed: {result.stderr[:200]}")
        return False
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-summary", action="store_true",
                        help="Print pipeline summary from output/summary.json")
    args = parser.parse_args()

    if args.print_summary:
        summary_file = Path("output/summary.json")
        if summary_file.exists():
            summary = json.loads(summary_file.read_text(encoding="utf-8"))
            print(f"Uploaded: {summary['total_uploaded']} / {summary['total_videos_completed']} completed")
            for u in summary.get("uploads", []):
                print(f"  → {u['title'][:50]}")
        return

    summary_file = Path("output/summary.json")
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "")
    status = os.environ.get("PIPELINE_STATUS", "success")

    if not webhook_url:
        print("[Discord] No DISCORD_WEBHOOK_URL set. Skipping.")
        return

    # Build embed
    if status == "success" and summary_file.exists():
        summary = json.loads(summary_file.read_text(encoding="utf-8"))
        if summary.get("total_uploaded", 0) > 0:
            embed = build_success_embed(summary)
        else:
            embed = build_failure_embed("no_videos")
    else:
        embed = build_failure_embed(status)

    payload = {"embeds": [embed]}
    send_webhook(webhook_url, payload)


if __name__ == "__main__":
    main()
