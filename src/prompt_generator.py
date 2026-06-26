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
    # 破壞系列
    {
        "hook": "破壞慾滿足 - 液壓機壓碎",
        "template": "A {object} being slowly crushed by a massive hydraulic press, satisfying slow-motion destruction, fragments flying, dramatic cinematic lighting, vertical 9:16 video, macro close-up of cracking surface, hyper-realistic textures",
    },
    {
        "hook": "破壞慾滿足 - 重物墜落",
        "template": "A heavy {object} falling from above and smashing a {target} on impact, slow-motion explosion of pieces, dramatic smash, satisfying destruction, slow-mo, vertical video 9:16",
    },
    {
        "hook": "壓力釋放 - 氣球爆破",
        "template": "Close-up of a {color} balloon being slowly inflated until it suddenly POPS, tension building, satisfying release, slow-motion capture of the burst, vertical 9:16, macro detail of latex tearing",
    },
    {
        "hook": "強迫症治癒 - 完美排列",
        "template": "Perfectly organized {objects} being arranged in symmetrical pattern, satisfying ASMR movements, crisp and precise placement, clean minimal aesthetic, vertical 9:16, smooth transitions",
    },
    {
        "hook": "強迫症治癒 - 髒污清潔",
        "template": "Time-lapse of a {surface} being deep cleaned, satisfying transformation from dirty to spotless, foam and bubbles, satisfying scrub, before and after reveal, vertical 9:16",
    },
    {
        "hook": "視覺衝擊 - 巨大 vs 微小",
        "template": "Extreme macro close-up of a {small_object} next to a {big_object}, shocking scale contrast, tilt-shift miniature effect, dramatic depth of field, vertical 9:16",
    },
    {
        "hook": "好奇心鉤子 - 變色/變形",
        "template": "A {object} slowly transforming its color from {color1} to {color2}, mesmerizing gradient transition, smooth and continuous morphing, satisfying visual effect, vertical 9:16",
    },
    {
        "hook": "破壞慾滿足 - 切割/切開",
        "template": "A sharp blade slowly slicing through a {object}, clean cut revealing perfect cross-section, satisfying precision cutting, macro close-up, vertical 9:16",
    },
    {
        "hook": "時間壓縮 - 生長/綻放",
        "template": "Time-lapse of a {flower} blooming in slow motion, petals opening gracefully, beautiful natural process, vibrant colors, dreamy lighting, vertical 9:16",
    },
    {
        "hook": "ASMR 觸感 - 質地變化",
        "template": "Close-up of hands interacting with {texture}, satisfying tactile sensation, ASMR-style visual, soft focus, warm lighting, vertical 9:16, intimate macro shot",
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

        # Diverse parameter pools for templates
        template_data = [
            {"object": "colorful gummy bear", "target": "concrete floor"},
            {"object": "a heavy steel anvil", "target": "a ripe watermelon"},
            {"color": "red", "object": "balloon"},
            {"objects": "colorful gummy bears"},
            {"surface": "dirty kitchen stove top"},
            {"small_object": "tiny toy car", "big_object": "giant shoe"},
            {"object": "a fresh flower", "color1": "white", "color2": "bright red"},
            {"object": "a ripe avocado"},
            {"flower": "beautiful red rose"},
            {"texture": "soft velvet fabric"},
            {"object": "rainbow colored slime"},
            {"object": "shiny crystal ice cube"},
            {"color": "golden", "object": "helium balloon"},
            {"objects": "colorful domino blocks"},
            {"surface": "muddy car windshield"},
            {"small_object": "a single grain of rice", "big_object": "a human hand"},
            {"object": "colorful liquid", "color1": "blue", "color2": "purple"},
            {"object": "a soft fresh loaf of bread"},
            {"flower": "giant sunflower"},
            {"texture": "crunchy autumn leaves"},
        ]

        concepts = []
        for i in range(count):
            template = VIRAL_TEMPLATES[i % len(VIRAL_TEMPLATES)]
            data = template_data[i % len(template_data)]

            # Fill template placeholders
            prompt = template["template"]
            for key, value in data.items():
                prompt = prompt.replace(f"{{{key}}}", value)

            # Generate title based on hook type
            hook = template["hook"]
            if "壓碎" in hook or "切割" in hook:
                title = f"{data.get('object','Object').title()} gets DESTROYED! 😱 #Shorts"
            elif "爆破" in hook:
                title = f"Watch this {data.get('color','')} balloon POP! 💥 #Shorts"
            elif "排列" in hook:
                title = f"Satisfying {data.get('objects','objects')} arrangement! ✨ #Shorts"
            elif "清潔" in hook:
                title = f"Satisfying {data.get('surface','surface')} cleaning! 🧼 #Shorts"
            elif "巨大" in hook:
                title = f"Size comparison: {data.get('small_object','?')} vs {data.get('big_object','?')} 🤯 #Shorts"
            elif "時間" in hook:
                title = f"Mesmerizing {data.get('flower','flower')} blooming! 🌸 #Shorts"
            else:
                title = f"Satisfying {data.get('object','video')}! 🔥 #Shorts"

            concepts.append({
                "title": title[:95],
                "kling_prompt": prompt,
                "description": (
                    f"{title}\n\n"
                    f"Follow for more satisfying Shorts! 🔥\n"
                    f"@GentleSoul666\n\n"
                    f"#Shorts #Viral #Satisfying #OddlySatisfying #ASMR #Loop"
                ),
                "tags": ["#Shorts", "#Viral", "#Satisfying", "#OddlySatisfying", "#ASMR", "#Loop"],
                "hook_type": hook,
            })

        return concepts
