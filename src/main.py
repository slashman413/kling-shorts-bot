"""
Main pipeline: orchestrates the daily Shorts generation workflow.
Generates 9:16 vertical videos, loops them to 12-15s, uploads to YouTube.
"""

import json
import os
import sys
import subprocess
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from kling_client import KlingClient
from video_looper import VideoLooper
from prompt_generator import PromptGenerator
from youtube_uploader import YouTubeUploader


class ShortsPipeline:
    """Daily pipeline for generating looping Shorts videos."""

    def __init__(self):
        self.prompt_gen = PromptGenerator()
        self.looper = VideoLooper(repeats=4)  # 4x loop = ~20s total
        self.config = self._load_config()
        self.videos_per_day = int(
            os.environ.get("VIDEOS_PER_DAY", 
            self.config.get("schedule", {}).get("videos_per_day", 10))
        )
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    def _load_config(self) -> dict:
        import yaml
        config_path = Path(__file__).parent.parent / "config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return {}

    def step1_generate_concepts(self) -> list[dict]:
        """Step 1: Generate viral concepts."""
        print(f"\n{'='*60}")
        print(f"📝 Step 1: Generating {self.videos_per_day} viral concepts...")
        print(f"{'='*60}")

        concepts = self.prompt_gen.generate_concepts(count=self.videos_per_day)

        for i, c in enumerate(concepts, 1):
            print(f"  [{i}] {c['hook_type']} → {c['title']}")

        with open(self.output_dir / "concepts_today.json", "w", encoding="utf-8") as f:
            json.dump(concepts, f, ensure_ascii=False, indent=2)

        return concepts

    def step2_generate_videos(self, concepts: list[dict]) -> list[dict]:
        """Step 2: Generate vertical (9:16) videos with Kling, then create loops."""
        print(f"\n{'='*60}")
        print(f"🎬 Step 2: Generating looping Shorts with Kling AI...")
        print(f"{'='*60}")

        try:
            kling = KlingClient()
        except ValueError as e:
            print(f"  ❌ {e}")
            print("  ⏩ Saving prompts only.")
            return [{"concept": c, "local_path": None, "status": "prompt_only"} for c in concepts]

        results = []
        for i, concept in enumerate(concepts, 1):
            print(f"\n  [{i}/{len(concepts)}] {concept['title']}")
            try:
                # Rate limiting: delay between requests (Kling: ~5-10 req/min)
                if i > 1:
                    delay = 15  # 15 seconds between each video request
                    print(f"    ⏱  Waiting {delay}s to respect rate limits...")
                    time.sleep(delay)
                # 1. Generate video with Kling (9:16, 5 seconds)
                response = kling.text_to_video(
                    prompt=concept["kling_prompt"],
                    duration=5,
                    aspect_ratio="9:16",
                )
                task_id = response.get("data", {}).get("task_id", "")
                print(f"    📤 Task: {task_id}")

                # 2. Wait for completion
                video_url = kling.wait_for_video(task_id, poll_interval=15, timeout=300)
                if not video_url:
                    results.append({"concept": concept, "local_path": None, "status": "failed"})
                    continue

                print(f"    ✅ Video URL received")

                # 3. Download the video
                local_path = self.output_dir / f"video_{i:02d}.mp4"
                self._download_video(video_url, local_path)
                print(f"    💾 Downloaded: {local_path}")

                # 4. Create loop (4x repeat = ~20s at 720x1280 HD)
                loop_path = self.output_dir / f"loop_{i:02d}.mp4"
                self.looper.create_loop(str(local_path), str(loop_path))
                print(f"    🔄 Loop created: {loop_path}")

                results.append({
                    "concept": concept,
                    "local_path": str(loop_path),
                    "original_url": video_url,
                    "task_id": task_id,
                    "status": "completed",
                })

            except Exception as e:
                print(f"    ❌ Error: {e}")
                results.append({"concept": concept, "local_path": None, "status": "error", "error": str(e)})

        return results

    def _download_video(self, url: str, path: Path):
        """Download video from URL using curl."""
        result = subprocess.run(
            ["curl", "-s", "-o", str(path), url],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            raise RuntimeError(f"Download failed: {result.stderr}")

    def step3_upload_videos(self, video_results: list[dict]) -> list[dict]:
        """Step 3: Upload looped Shorts to YouTube."""
        print(f"\n{'='*60}")
        print(f"📤 Step 3: Uploading looping Shorts to YouTube...")
        print(f"{'='*60}")

        try:
            yt = YouTubeUploader()
        except ValueError as e:
            print(f"  ❌ {e}")
            print("  ⏩ Skipping YouTube upload.")
            return []

        to_upload = [r for r in video_results if r.get("status") == "completed" and r.get("local_path")]

        if not to_upload:
            print("  No videos to upload.")
            return []

        uploads = []
        for i, result in enumerate(to_upload, 1):
            concept = result["concept"]
            print(f"\n  [{i}/{len(to_upload)}] {concept['title']}")

            try:
                vid = yt.upload_video(
                    video_path=result["local_path"],
                    title=concept["title"],
                    description=concept.get("description", ""),
                    tags=concept.get("tags", ["#Shorts"]),
                    privacy_status="public",
                )
                if vid:
                    # keep each video_id paired with its own concept (no index guessing later)
                    uploads.append({"video_id": vid, "concept": concept})
            except Exception as e:
                print(f"    ❌ Upload failed: {e}")

        return uploads

    def run(self):
        """Run the full pipeline."""
        print(f"\n{'='*60}")
        print(f"  🚀 KLING SHORTS BOT - 每日自動化 Shorts 生產線")
        print(f"  📐 9:16 720x1280 HD | 🔄 4x Loop ~20s | 📤 YouTube Auto-Upload")
        print(f"{'='*60}")

        concepts = self.step1_generate_concepts()
        if not concepts:
            print("❌ No concepts generated!")
            return

        video_results = self.step2_generate_videos(concepts)
        uploads = self.step3_upload_videos(video_results)

        # Build structured summary — each upload already carries its own concept
        upload_details = [{
            "video_id": u["video_id"],
            "url": f"https://youtube.com/watch?v={u['video_id']}",
            "title": u["concept"].get("title", "Untitled"),
            "hook_type": u["concept"].get("hook_type", "Unknown"),
        } for u in uploads]

        summary = {
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_concepts": len(concepts),
            "total_videos_completed": sum(1 for r in video_results if r.get("status") == "completed"),
            "total_uploaded": len(uploads),
            "channel_url": "https://youtube.com/@GentleSoul666",
            "uploads": upload_details,
        }

        # Save summary for GHA to read
        with open(self.output_dir / "summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"  📄 Summary saved: output/summary.json")

        # Print summary
        print(f"\n{'='*60}")
        print(f"  📊 DAY SUMMARY")
        print(f"{'='*60}")
        print(f"  Concepts generated: {len(concepts)}")
        print(f"  Videos + Looped:    {summary['total_videos_completed']}")
        print(f"  Uploaded to YouTube: {len(uploads)}")
        print(f"  Channel: https://youtube.com/@GentleSoul666")
        for detail in upload_details:
            print(f"    → {detail['title']}")
            print(f"      {detail['url']}")
        print(f"{'='*60}\n")

        # Print a JSON line that GHA can capture
        print(f"---SUMMARY_JSON_START---")
        print(json.dumps(summary, ensure_ascii=False))
        print(f"---SUMMARY_JSON_END---")


if __name__ == "__main__":
    pipeline = ShortsPipeline()
    pipeline.run()
