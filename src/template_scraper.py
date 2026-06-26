"""
YouTube Shorts Trend Scraper & Template Updater
================================================
Fetches trending Shorts via yt-dlp, analyzes viral hooks,
and dynamically weights/updates the prompt template library.

Runs weekly via GitHub Actions to keep templates aligned
with what's actually trending on YouTube Shorts.
"""

import json
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime
from collections import Counter

# ═══════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════
DATA_DIR = Path(__file__).parent.parent / "data"
ANALYSIS_FILE = DATA_DIR / "trending_analysis.json"

# Search queries targeting individual viral Shorts
SEARCH_QUERIES = [
    "#shorts satisfying",
    "#shorts crushing",
    "#shorts oddly satisfying",
    "#shorts ASMR",
    "#shorts food",
    "#shorts destruction",
    "#shorts satisfying video",
    "#shorts cutting",
    "#shorts relaxing",
    "#shorts ice crushing",
    "#shorts kinetic sand",
    "#shorts melting",
    "#shorts pouring",
    "#shorts viral satisfying",
]

# Keywords → template boost mapping
# When a keyword appears frequently in trending titles,
# the corresponding template categories get higher weight
TREND_KEYWORDS = {
    "crush": "破壞慾滿足",
    "crunch": "破壞慾滿足",
    "smash": "破壞慾滿足",
    "destroy": "破壞慾滿足",
    "hydraulic": "破壞慾滿足",
    "press": "破壞慾滿足",
    "pop": "壓力釋放",
    "burst": "壓力釋放",
    "satisfying": "強迫症治癒",
    "clean": "強迫症治癒",
    "organize": "強迫症治癒",
    "arrange": "強迫症治癒",
    "cut": "強迫症治癒",
    "slice": "強迫症治癒",
    "sand": "強迫症治癒",
    "soap": "強迫症治癒",
    "ice": "ASMR破壞",
    "melt": "食物ASMR",
    "cheese": "食物ASMR",
    "chocolate": "食物ASMR",
    "food": "食物ASMR",
    "cook": "食物ASMR",
    "sizzle": "食物ASMR",
    "pour": "食物ASMR",
    "paint": "視覺治癒",
    "color": "視覺治癒",
    "water": "視覺治癒",
    "droplet": "視覺治癒",
    "splash": "視覺治癒",
    "fire": "視覺衝擊",
    "flame": "視覺衝擊",
    "transform": "好奇心鉤子",
    "change": "好奇心鉤子",
    "bloom": "時間壓縮",
    "flower": "時間壓縮",
    "grow": "時間壓縮",
    "stretch": "張力釋放",
    "elastic": "張力釋放",
    "bubble": "壓力釋放",
    "magnetic": "視覺衝擊",
}


class TrendScraper:
    """Fetch and analyze trending YouTube Shorts patterns."""

    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def fetch_trending(self, max_per_query: int = 15) -> list[dict]:
        """
        Fetch trending Shorts metadata using yt-dlp.
        Searches multiple queries for broad coverage.
        """
        all_videos = []
        seen_ids = set()

        for query in SEARCH_QUERIES:
            try:
                result = subprocess.run(
                    [
                        "yt-dlp",
                        "--flat-playlist",
                        "--print",
                        "%(id)s\t%(title)s\t%(view_count)s\t%(channel)s\t%(duration)s",
                        "--no-warnings",
                        "--no-check-certificates",
                        f"ytsearch{max_per_query}:{query}",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=45,
                )
                for line in result.stdout.strip().split("\n"):
                    if not line or "\t" not in line:
                        continue
                    parts = line.split("\t")
                    if len(parts) < 5:
                        continue

                    vid_id = parts[0]
                    if vid_id in seen_ids:
                        continue
                    seen_ids.add(vid_id)

                    # Parse view count
                    views_str = parts[2].replace(",", "").strip()
                    try:
                        views = int(views_str) if views_str not in ("NA", "N/A", "") else 0
                    except ValueError:
                        views = 0

                    # Parse duration
                    dur_str = parts[4].strip()
                    try:
                        duration = int(float(dur_str)) if dur_str not in ("NA", "") else 0
                    except ValueError:
                        duration = 0

                    all_videos.append({
                        "id": vid_id,
                        "title": parts[1].strip(),
                        "views": views,
                        "channel": parts[3].strip(),
                        "duration": duration,
                        "query_source": query,
                    })

            except subprocess.TimeoutExpired:
                print(f"  ⏰ Query timeout: {query}")
            except Exception as e:
                print(f"  ❌ Query error ({query}): {e}")

        # Filter for Shorts: ≤ 60 seconds, min 100K views
        shorts = [v for v in all_videos if 0 < v["duration"] <= 60 or v["duration"] == 0]
        viral = [v for v in shorts if v["views"] >= 100_000]

        # Deduplicate by title similarity
        unique = []
        seen_titles = set()
        for v in sorted(viral, key=lambda x: x["views"], reverse=True):
            title_lower = v["title"].lower()[:60]
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique.append(v)

        print(f"  📊 Fetched {len(all_videos)} total, {len(shorts)} Shorts, {len(unique)} viral (100K+)")
        return unique[:100]  # Keep top 100

    def analyze_hooks(self, videos: list[dict]) -> dict:
        """
        Analyze viral titles to extract trending hook patterns.
        Returns scoring data for template weighting.
        """
        title_keywords = Counter()
        hook_scores = Counter()
        top_titles = []

        for v in videos:
            title = v.get("title", "")
            title_lower = title.lower()
            top_titles.append(title)

            # Check trend keywords
            for keyword, hook_type in TREND_KEYWORDS.items():
                if keyword in title_lower:
                    hook_scores[hook_type] += 1
                    title_keywords[keyword] += 1

            # Check for emoji-based hooks (strong engagement signal)
            emoji_pattern = re.compile(r'[\U0001F300-\U0001FFFF]')
            emojis = emoji_pattern.findall(title)
            for emoji in emojis:
                title_keywords[f"emoji:{emoji}"] += 1

        # Calculate top trending hook categories
        total = sum(hook_scores.values()) or 1
        trending_hooks = {
            hook: {
                "count": count,
                "weight": round(count / total, 3),
                "percentage": round(count / total * 100, 1),
            }
            for hook, count in hook_scores.most_common()
        }

        # Top 10 viral titles for reference
        sample_titles = [
            {"title": v["title"], "views": v["views"], "channel": v["channel"]}
            for v in videos[:10]
        ]

        # Detect hot new themes not in our existing templates
        all_keywords = [k for k, _ in title_keywords.most_common(30)]
        known_themes = set(TREND_KEYWORDS.keys())
        new_themes = [k for k in all_keywords if k not in known_themes][:10]

        print(f"  🔥 Top hooks: {[h for h, _ in hook_scores.most_common(5)]}")
        print(f"  💡 New themes detected: {new_themes[:5]}")

        return {
            "scraped_at": datetime.now().isoformat(),
            "total_viral_analyzed": len(videos),
            "trending_hooks": trending_hooks,
            "total_hook_mentions": total,
            "sample_viral_titles": sample_titles,
            "top_keywords": title_keywords.most_common(20),
            "new_themes_detected": new_themes,
            "trend_direction": self._determine_trend_direction(trending_hooks),
        }

    def _determine_trend_direction(self, hook_scores: dict) -> str:
        """Summarize what's trending this week."""
        if not hook_scores:
            return "no data"

        top = sorted(hook_scores.items(), key=lambda x: x[1]["count"], reverse=True)
        top_hooks = [h for h, _ in top[:3]]

        if "破壞慾滿足" in top_hooks[:2]:
            return "destruction"
        elif "強迫症治癒" in top_hooks[:2]:
            return "satisfying"
        elif "食物ASMR" in top_hooks[:2]:
            return "food"
        elif "視覺治癒" in top_hooks[:2]:
            return "visual"
        else:
            return top_hooks[0] if top_hooks else "unknown"

    def _get_category_weights(self, analysis: dict) -> dict:
        """Convert trend analysis to template category weights (0.5x - 3x)."""
        weights = {}
        trending = analysis.get("trending_hooks", {})

        # Categories that exist in our templates
        categories = [
            "破壞慾滿足", "壓力釋放", "強迫症治癒", "視覺衝擊",
            "好奇心鉤子", "時間壓縮", "ASMR 觸感", "食物ASMR",
            "視覺治癒", "ASMR破壞", "張力釋放",
        ]

        # Calculate weights: trending hooks get boosted
        max_count = max((h["count"] for h in trending.values()), default=1)
        for cat in categories:
            if cat in trending:
                ratio = trending[cat]["count"] / max_count
                weights[cat] = round(0.8 + ratio * 2.2, 2)  # 0.8x to 3.0x
            else:
                weights[cat] = 0.5  # Not trending, lower chance

        return weights

    def run(self, save: bool = True) -> dict:
        """Run the full scrape + analysis pipeline."""
        print(f"\n{'='*55}")
        print(f"  📊 YouTube Shorts Trend Scraper")
        print(f"  🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*55}")

        # Step 1: Fetch trending Shorts
        print("\n📡 Fetching trending Shorts...")
        videos = self.fetch_trending()
        if not videos:
            print("⚠️  No trending Shorts found. Check yt-dlp installation.")
            return {}

        # Step 2: Analyze hooks
        print(f"\n🔍 Analyzing {len(videos)} viral Shorts...")
        analysis = self.analyze_hooks(videos)

        # Step 3: Calculate weights
        weights = self._get_category_weights(analysis)
        analysis["category_weights"] = weights

        # Step 4: Generate new template suggestions
        if "OPENAI_API_KEY" in os.environ:
            analysis["new_templates"] = self._generate_templates_with_llm(analysis)
        else:
            analysis["new_templates"] = []
            print("  ℹ️  Set OPENAI_API_KEY for AI-powered template generation")

        # Step 5: Save
        if save:
            with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Saved: {ANALYSIS_FILE}")

        # Summary
        print(f"\n{'='*55}")
        print(f"  📈 TREND SUMMARY")
        print(f"{'='*55}")
        print(f"  Viral Shorts analyzed: {len(videos)}")
        print(f"  Trend direction:      {analysis['trend_direction']}")
        print(f"  Top hooks:")
        for hook, info in sorted(
            analysis["trending_hooks"].items(),
            key=lambda x: x[1]["count"], reverse=True
        )[:5]:
            bar = "█" * int(info["percentage"] / 5) + "░" * (20 - int(info["percentage"] / 5))
            print(f"    {info['percentage']:5.1f}% {bar} {hook}")
        print(f"  Category weights updated for template selection")

        return analysis

    def _generate_templates_with_llm(self, analysis: dict) -> list:
        """Generate new template entries using LLM (requires OPENAI_API_KEY)."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

            prompt = f"""Based on these currently trending YouTube Shorts titles, 
            generate 5 new Kling AI video prompt templates that would be viral:

            Top viral titles right now:
            {json.dumps([v['title'] for v in analysis.get('sample_viral_titles', [])], indent=2)}

            Trending categories: {list(analysis['trending_hooks'].keys())}
            Trend direction: {analysis['trend_direction']}

            For each template, provide:
            1. hook_type: Category name
            2. template: Kling AI video prompt (50-80 words, vertical 9:16)
            3. title_format: Title template

            Output JSON array only."""

            response = client.chat.completions.create(
                model=os.environ.get("LLM_MODEL", "gpt-4o"),
                messages=[
                    {"role": "system", "content": "You generate viral Shorts video templates."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.8,
            )
            data = json.loads(response.choices[0].message.content)
            print(f"  🤖 Generated {len(data.get('templates', data.get('concepts', [])))} LLM templates")
            return data.get("templates", data.get("concepts", []))

        except Exception as e:
            print(f"  ⚠️  LLM template generation failed: {e}")
            return []


if __name__ == "__main__":
    scraper = TrendScraper()
    scraper.run()
