"""
Main pipeline: orchestrates the daily Shorts generation workflow.
"""

import json
import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from kling_client import KlingClient
from prompt_generator import PromptGenerator
from youtube_uploader import YouTubeUploader


class ShortsPipeline:
    """Daily pipeline for generating and uploading Shorts."""

    def __init__(self):
        self.prompt_gen = PromptGenerator()
        self.config = self._load_config()
        self.videos_per_day = int(os.environ.get("VIDEOS_PER_DAY", self.config.get("schedule", {}).get("videos_per_day", 10)))

    def _load_config(self) -> dict:
        import yaml
        config_path = Path(__file__).parent.parent / "config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return {}

    def step1_generate_concepts(self) -> list[dict]:
        """Step 1: Use LLM to generate viral concepts."""
        print(f"\n{'='*60}")
        print(f"📝 Step 1: Generating {self.videos_per_day} viral concepts...")
        print(f"{'='*60}")

        concepts = self.prompt_gen.generate_concepts(count=self.videos_per_day)

        for i, c in enumerate(concepts, 1):
            print(f"  [{i}] {c['hook_type']} → {c['title']}")

        # Save concepts for audit
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        with open(output_dir / "concepts_today.json", "w", encoding="utf-8") as f:
            json.dump(concepts, f, ensure_ascii=False, indent=2)

        return concepts

    def step2_generate_videos(self, concepts: list[dict]) -> list[dict]:
        """Step 2: Call Kling API to generate videos."""
        print(f"\n{'='*60}")
        print(f"🎬 Step 2: Generating videos with Kling AI...")
        print(f"{'='*60}")

        try:
            kling = KlingClient()
        except ValueError as e:
            print(f"  ❌ {e}")
            print("  ⏩ Skipping Kling generation, saving prompts only.")
            return [{"concept": c, "video_path": None, "status": "prompt_only"} for c in concepts]

        results = []
        for i, concept in enumerate(concepts, 1):
            print(f"\n  [{i}/{len(concepts)}] Generating: {concept['title']}")
            try:
                response = kling.text_to_video(
                    prompt=concept["kling_prompt"],
                    duration=5,
                )
                task_id = response.get("data", {}).get("task_id", "")
                print(f"    ✅ Task created: {task_id}")

                # Wait for video (async in batch mode)
                video_url = kling.wait_for_video(task_id, poll_interval=15, timeout=300)
                if video_url:
                    print(f"    ✅ Video ready: {video_url[:60]}...")
                    results.append({
                        "concept": concept,
                        "video_url": video_url,
                        "task_id": task_id,
                        "status": "completed",
                    })
                else:
                    results.append({
                        "concept": concept,
                        "video_url": None,
                        "task_id": task_id,
                        "status": "failed",
                    })
            except Exception as e:
                print(f"    ❌ Error: {e}")
                results.append({
                    "concept": concept,
                    "video_url": None,
                    "status": "error",
                    "error": str(e),
                })

        return results

    def step3_upload_videos(self, video_results: list[dict]) -> list[str]:
        """Step 3: Upload generated videos to YouTube."""
        print(f"\n{'='*60}")
        print(f"📤 Step 3: Uploading to YouTube...")
        print(f"{'='*60}")

        try:
            yt = YouTubeUploader()
        except ValueError as e:
            print(f"  ❌ {e}")
            print("  ⏩ Skipping YouTube upload.")
            return []

        # Filter only successful videos
        to_upload = [
            r for r in video_results
            if r.get("status") == "completed" and r.get("video_url")
        ]

        if not to_upload:
            print("  No videos to upload.")
            return []

        video_ids = []
        for i, result in enumerate(to_upload, 1):
            concept = result["concept"]
            print(f"\n  [{i}/{len(to_upload)}] Uploading: {concept['title']}")

            try:
                vid = yt.upload_video(
                    video_path=result["video_url"],  # Direct URL
                    title=concept["title"],
                    description=concept.get("description", ""),
                    tags=concept.get("tags", ["#Shorts"]),
                    privacy_status="public",
                )
                if vid:
                    video_ids.append(vid)
            except Exception as e:
                print(f"    ❌ Upload failed: {e}")

        return video_ids

    def run(self):
        """Run the full pipeline."""
        print(f"\n{'='*60}")
        print(f"  🚀 KLING SHORTS BOT - 每日自動化 Shorts 生產線")
        print(f"{'='*60}")

        # Step 1: Generate concepts
        concepts = self.step1_generate_concepts()

        if not concepts:
            print("❌ No concepts generated! Check your LLM config.")
            return

        # Step 2: Generate videos (or save prompts if no Kling API)
        video_results = self.step2_generate_videos(concepts)

        # Step 3: Upload to YouTube
        video_ids = self.step3_upload_videos(video_results)

        # Summary
        print(f"\n{'='*60}")
        print(f"  📊 DAY SUMMARY")
        print(f"{'='*60}")
        print(f"  Concepts generated: {len(concepts)}")
        print(f"  Videos generated:   {sum(1 for r in video_results if r.get('status') == 'completed')}")
        print(f"  Uploaded to YouTube: {len(video_ids)}")
        if video_ids:
            print(f"  Channel: https://youtube.com/@GentleSoul666")
            for vid in video_ids:
                print(f"    → https://youtube.com/watch?v={vid}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    pipeline = ShortsPipeline()
    pipeline.run()
