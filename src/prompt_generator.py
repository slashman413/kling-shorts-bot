"""
Creative prompt generator using LLM (OpenAI-compatible API).
Generates viral Shorts concepts based on trending hooks.
"""

import json
import os
from typing import Optional

from openai import OpenAI


# Viral Shorts prompt templates library
VIRAL_TEMPLATES = [
    {
        "hook": "破壞慾滿足 - 東西被壓碎",
        "template": "A {object} being slowly crushed by a massive {crusher}, cinematic slow-motion, satisfying destruction, macro close-up, dramatic lighting",
        "example": "A glowing neon smartphone being slowly crushed by a massive hydraulic press"
    },
    {
        "hook": "壓力釋放 - 等待的張力",
        "template": "A {subject} about to {action}, tension building, anticipation, slow build-up then sudden release, satisfying moment",
    },
    {
        "hook": "強迫症治癒 - 完美對稱/排列",
        "template": "Perfectly organized {objects} being arranged in satisfying symmetry, ASMR-style, crisp movements, clean aesthetic",
    },
    {
        "hook": "時間壓縮 - 快速變化",
        "template": "Time-lapse of {subject} transforming, smooth transition, mesmerizing change, before and after reveal",
    },
    {
        "hook": "巨大 vs 微小 - 視覺衝擊",
        "template": "Extreme scale contrast between {big_subject} and {small_subject}, dramatic perspective, awe-inspiring shot",
    },
    {
        "hook": "好奇心鉤子 - 你不知道的",
        "template": "Close-up revealing hidden detail of {subject}, surprising discovery, macro exploration, mind-blowing reveal",
    },
]


class PromptGenerator:
    """Generate viral Shorts prompts using AI."""

    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            # Fall back to local templates if no API key
            self.use_llm = False
            print("[PromptGen] No OPENAI_API_KEY set, using template library")
            return

        self.client = OpenAI(api_key=api_key)
        self.model = os.environ.get("LLM_MODEL", "gpt-4o")
        self.use_llm = True

    def generate_concepts(self, count: int = 10) -> list[dict]:
        """
        Generate viral Shorts concepts.

        Returns list of dicts with keys:
          - title: Short title
          - kling_prompt: Kling text-to-video prompt
          - description: YouTube description
          - tags: List of hashtags
          - hook_type: Type of psychological hook
        """
        if self.use_llm:
            return self._generate_with_llm(count)
        else:
            return self._generate_from_templates(count)

    def _generate_with_llm(self, count: int) -> list[dict]:
        """Use GPT-4o to generate viral concepts based on the hydraulic press hook."""
        system_prompt = """You are an expert YouTube Shorts content strategist specializing in 
        viral AI-generated videos. Your specialty is the "satisfying destruction" genre 
        (hydraulic press, crushing, destroying things) which gets 100M+ views.

        For each video concept, provide a JSON object with:
        - title: Catchy Shorts title (under 60 chars)
        - kling_prompt: Detailed English prompt for Kling AI text-to-video (50-100 words, describe the scene, lighting, camera movement, textures)
        - description: YouTube description with hook text (2-3 lines)
        - tags: List of 8-10 relevant hashtags
        - hook_type: The psychological hook (e.g., "破壞慾滿足", "壓力釋放", "強迫症治癒")

        Rules:
        - Each concept must have a UNIQUE visual premise
        - Focus on destruction, crushing, satisfying mechanics
        - Include specific details: lighting, textures, camera angles
        - Keep videos under 10 seconds (5 is ideal)
        - Output ONLY valid JSON array, no markdown"""

        user_prompt = f"""Generate {count} viral YouTube Shorts video concepts based on the 
        hydraulic press/destruction/satisfying genre. Each should be a unique visual concept 
        that would trend on Shorts.

        Follow this format exactly:
        [
          {{
            "title": "...",
            "kling_prompt": "...",
            "description": "...",
            "tags": ["#shorts", "#viral", "..."],
            "hook_type": "..."
          }}
        ]"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.9,
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        # Handle both array and {concepts: [...]} formats
        if isinstance(data, dict):
            for key in ["concepts", "videos", "ideas"]:
                if key in data:
                    return data[key]
        return data if isinstance(data, list) else []

    def _generate_from_templates(self, count: int) -> list[dict]:
        """Use template library when no LLM available."""
        import random

        objects = [
            ("colorful gummy bear", "giant hydraulic press"),
            ("ripe watermelon", "industrial compressor"),
            ("porcelain doll", "steam roller"),
            ("glass bottle", "hydraulic crusher"),
            ("smartphone", "metal press"),
            ("rubber duck", "garbage truck"),
            ("pumpkin", "car tire"),
            ("ice sculpture", "heated blade"),
            ("clay pot", "hydraulic hammer"),
            ("tennis ball", "vice grip"),
        ]

        concepts = []
        for i in range(min(count, len(objects))):
            obj, crusher = objects[i % len(objects)]
            concepts.append({
                "title": f"Satisfying {obj} gets CRUSHED! 😱",
                "kling_prompt": (
                    f"Close-up cinematic shot of a {obj} being slowly crushed by a {crusher}, "
                    f"macro detail of the object deforming and cracking under pressure, "
                    f"splinters and fragments flying, dramatic slow-motion, "
                    f"cinematic lighting with harsh shadows, photorealistic textures, "
                    f"industrial background, 8K quality, satisfying destruction"
                ),
                "description": f"Watch this {obj} get completely destroyed! 🔥\n\nMost satisfying crush ever!\n\n#Shorts #Viral #Satisfying",
                "tags": ["#Shorts", "#Viral", "#Satisfying", "#Destruction", "#Crush", "#OddlySatisfying", "#ASMR"],
                "hook_type": "破壞慾滿足",
            })

        return concepts
