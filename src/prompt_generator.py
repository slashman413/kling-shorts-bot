"""
Creative prompt generator with 25 viral YouTube Shorts templates.
Covers the top-performing Shorts categories for maximum viral potential.
"""

import json
import os
import random
from typing import Optional

from openai import OpenAI


# ═══════════════════════════════════════════════════════════════
# 25 Viral Shorts Prompt Templates
# Covers the TOP Shorts categories proven to get millions of views
# ═══════════════════════════════════════════════════════════════
VIRAL_TEMPLATES = [
    # === 破壞系列 (Destruction) ===
    {
        "hook": "破壞慾滿足 - 液壓機壓碎 🔨",
        "template": "A {object} being slowly crushed by a massive hydraulic press, satisfying slow-motion destruction, fragments flying, dramatic cinematic lighting, vertical 9:16 video, macro close-up of cracking surface, hyper-realistic textures",
    },
    {
        "hook": "破壞慾滿足 - 重物墜落 💥",
        "template": "A heavy {object} falling from above and smashing a {target} on impact, slow-motion explosion of pieces, dramatic smash, satisfying destruction, slow-mo, vertical video 9:16",
    },
    {
        "hook": "壓力釋放 - 氣球爆破 🎈",
        "template": "Close-up of a {color} balloon being slowly inflated until it suddenly POPS, tension building, satisfying release, slow-motion capture of the burst, vertical 9:16, macro detail of latex tearing",
    },
    # === 強迫症/治癒系列 (OCD Satisfying) ===
    {
        "hook": "強迫症治癒 - 完美排列 ✨",
        "template": "Perfectly organized {objects} being arranged in symmetrical pattern, satisfying ASMR movements, crisp and precise placement, clean minimal aesthetic, vertical 9:16, smooth transitions",
    },
    {
        "hook": "強迫症治癒 - 髒污清潔 🧼",
        "template": "Time-lapse of a {surface} being deep cleaned, satisfying transformation from dirty to spotless, foam and bubbles, satisfying scrub, before and after reveal, vertical 9:16",
    },
    # === 反差系列 (Scale/Contrast) ===
    {
        "hook": "視覺衝擊 - 巨大 vs 微小 🤯",
        "template": "Extreme macro close-up of a {small_object} next to a {big_object}, shocking scale contrast, tilt-shift miniature effect, dramatic depth of field, vertical 9:16",
    },
    # === 變形/變色系列 (Transformation) ===
    {
        "hook": "好奇心鉤子 - 變色/變形 🌈",
        "template": "A {object} slowly transforming its color from {color1} to {color2}, mesmerizing gradient transition, smooth and continuous morphing, satisfying visual effect, vertical 9:16",
    },
    {
        "hook": "破壞慾滿足 - 切割/切開 🔪",
        "template": "A sharp blade slowly slicing through a {object}, clean cut revealing perfect cross-section, satisfying precision cutting, macro close-up, vertical 9:16",
    },
    # === 自然/生長系列 (Nature/Growth) ===
    {
        "hook": "時間壓縮 - 綻放 🌸",
        "template": "Time-lapse of a {flower} blooming in slow motion, petals opening gracefully, beautiful natural process, vibrant colors, dreamy lighting, vertical 9:16",
    },
    # === ASMR 觸感系列 ===
    {
        "hook": "ASMR 觸感 - 質感變化 🤲",
        "template": "Close-up of hands interacting with {texture}, satisfying tactile sensation, ASMR-style visual, soft focus, warm lighting, vertical 9:16, intimate macro shot",
    },
    # ═══════════════════════════════════════════════════════════
    # NEW VIRAL TEMPLATES — YouTube Shorts 爆款類別
    # ═══════════════════════════════════════════════════════════
    # === 🧼 肥皂切割/軟糖切割（Shorts #1 爆款類別）===
    {
        "hook": "強迫症治癒 - 肥皂切割 🧼",
        "template": "Satisfying close-up of a sharp knife slicing through a bar of {soap_color} soap, clean cuts revealing smooth layers, satisfying texture, slow motion, vertical 9:16, macro detail of the blade gliding through, ASMR feel",
    },
    # === 🍫 食物ASMR - 融化起司/巧克力（超級爆款）===
    {
        "hook": "食物ASMR - 融化牽絲 🧀",
        "template": "Extreme close-up of gooey melted {food} being pulled apart, stretchy cheese pull or chocolate drip, warm golden lighting, slow motion, satisfying strings of melted goodness, steam rising, vertical 9:16, mouth-watering macro shot",
    },
    # === 🌪️ 顏料混合 - 流體藝術（高互動）===
    {
        "hook": "視覺治癒 - 顏料混合 🎨",
        "template": "Mesmerizing slow-motion of vibrant {color1} and {color2} paint swirling together, fluid art, marble-like patterns forming, glossy wet texture, satisfying color blending, vertical 9:16, macro close-up of the paint mixing",
    },
    # === 🧊 冰塊碎裂 - 清脆感（ASMR爆款）===
    {
        "hook": "ASMR破壞 - 冰塊碎裂 🧊",
        "template": "Slow motion close-up of crystal clear ice cubes being crushed, satisfying shattering sound implied visually, fragments flying, cold blue tones, macro detail of cracks spreading through the ice, sparkling light refraction, vertical 9:16",
    },
    # === 🏖️ 動力沙切割（Oddly Satisfying 經典）===
    {
        "hook": "強迫症治癒 - 沙雕切割 🏖️",
        "template": "Sharp blade cutting through layers of kinetic sand, satisfying clean separation, layered colors revealed in cross-section, smooth and precise movements, vertical 9:16, macro close-up of the sand texture",
    },
    # === 💧 水滴慢動作（Mesmerizing 爆款）===
    {
        "hook": "視覺治癒 - 水滴慢動作 💧",
        "template": "Ultra slow-motion of a single water droplet falling into a pool of {color} liquid, crown splash forming in perfect symmetry, ripples spreading outward, dreamy lighting, vertical 9:16, macro detail of the splash, liquid dynamics",
    },
    # === 🧪 磁流體/鐵磁流體（高觀看率）===
    {
        "hook": "視覺衝擊 - 磁流體 🧪",
        "template": "Close-up of ferrofluid reacting to a magnet, spiky black liquid forming alien-like shapes, mesmerizing movement, liquid metal texture, dark background with dramatic side lighting, smooth organic motion, vertical 9:16",
    },
    # === 🧈 奶油刀/刮痧（ASMR 爆款）===
    {
        "hook": "ASMR 觸感 - 奶油刮抹 🧈",
        "template": "Satisfying close-up of a butter knife spreading creamy {food} on a surface, smooth even application, soft texture, warm golden lighting, ASMR visual, creamy and satisfying, vertical 9:16",
    },
    # === 🫧 泡泡紙爆破（永不過時的經典）===
    {
        "hook": "壓力釋放 - 泡泡爆破 🫧",
        "template": "Close-up slow-motion of bubble wrap being popped one by one, satisfying burst of each bubble, plastic texture deforming and snapping, satisfying release, vertical 9:16, macro detail of the popping moment",
    },
    # === 🍦 冰淇淋/奶昔製作（食物爆款）===
    {
        "hook": "食物ASMR - 醬料淋下 🍨",
        "template": "Slow motion of thick {sauce} being poured over {food}, glossy smooth flow, satisfying drip, golden/brown rich color, steam and condensation, decadent macro close-up, vertical 9:16, mouth-watering texture",
    },
    # === 🔥 火/熔岩視覺（震撼系爆款）===
    {
        "hook": "視覺衝擊 - 火焰/熔岩 🔥",
        "template": "Slow motion close-up of {material} burning and turning to glowing embers, mesmerizing flame dance, orange and red dynamic colors, sparks flying, heat shimmer, dramatic dark background, vertical 9:16",
    },
    # === 🪢 橡皮筋/彈力物體（張力釋放）===
    {
        "hook": "張力釋放 - 彈力爆發 🪢",
        "template": "Close-up of {object} being stretched to maximum tension and snapping back, elastic energy release, dramatic whip motion, slow-motion capture of the rebound, satisfying physics, vertical 9:16",
    },
    # === 🧽 海綿吸水（Oddly Satisfying）===
    {
        "hook": "視覺治癒 - 吸水膨脹 🧽",
        "template": "Time-lapse close-up of a compressed sponge expanding as it absorbs {color} water, satisfying growth, texture unfolding, water being absorbed into porous material, mesmerizing transformation, vertical 9:16",
    },
    # === 🐚 珍珠/亮片（閃亮系爆款）===
    {
        "hook": "視覺治癒 - 珍珠流動 🐚",
        "template": "Close-up macro shot of shimmering pearls or beads cascading and flowing, satisfying clinking sounds implied visually, glossy reflections, smooth movement, organic flow, warm soft lighting, vertical 9:16",
    },
    # === 🍳 煎蛋/食物烹飪（Shorts 長青爆款）===
    {
        "hook": "食物ASMR - 滋滋作響 🍳",
        "template": "Close-up of {food} sizzling on a hot pan, oil bubbling, steam rising, golden brown crust forming, satisfying cooking sounds implied, warm kitchen lighting, mouth-watering textures, vertical 9:16",
    },
    # ═══════════════════════════════════════════════════════════
]

# Diverse parameter pools for template placeholders
TEMPLATE_DATA = [
    {"object": "colorful gummy bear", "target": "concrete floor"},
    {"object": "a heavy steel anvil", "target": "a ripe watermelon"},
    {"color": "red", "object": "balloon", "target": "table"},
    {"objects": "colorful gummy bears"},
    {"surface": "dirty kitchen stove top"},
    {"small_object": "tiny toy car", "big_object": "giant shoe"},
    {"object": "a fresh flower", "color1": "white", "color2": "bright red"},
    {"object": "a ripe avocado"},
    {"flower": "beautiful red rose"},
    {"texture": "soft velvet fabric"},
    # 新增資料 — 對應新模板
    {"soap_color": "pastel pink"},
    {"food": "melted mozzarella cheese"},
    {"color1": "vibrant blue", "color2": "electric magenta"},
    {"object": "crystal clear ice cubes"},
    {"object": "layered kinetic sand"},
    {"color": "vibrant turquoise"},
    {"object": "black ferrofluid liquid"},
    {"food": "whipped butter"},
    {"object": "transparent bubble wrap"},
    {"sauce": "warm caramel sauce", "food": "vanilla ice cream"},
    {"material": "dry wooden log"},
    {"object": "thick rubber band"},
    {"color": "bright blue"},
    {"object": "shimmering golden pearls"},
    {"food": "bacon strips"},
    # 備用資料
    {"object": "rainbow colored slime", "target": "metal surface"},
    {"soap_color": "ocean blue"},
    {"food": "dark chocolate fondue"},
    {"color1": "neon green", "color2": "hot pink"},
    {"object": "shiny crystal ice ball", "target": "marble surface"},
    {"object": "colorful kinetic sand", "target": "wood table"},
    {"color": "deep purple"},
    {"small_object": "single grain of rice", "big_object": "giant red apple"},
    {"object": "thick red paint", "color1": "crimson", "color2": "gold"},
    {"object": "silver liquid mercury", "color": "silver"},
    {"flower": "giant sunflower", "color": "yellow"},
    {"sauce": "melted chocolate", "food": "fresh strawberries"},
    {"material": "colorful paper sheet"},
    {"object": "stretchy slime putty"},
    {"color": "emerald green"},
    {"object": "shiny glass marbles"},
    {"food": "Japanese wagyu beef"},
    {"object": "colorful stress ball", "target": "solid concrete"},
    {"surface": "muddy car windshield"},
    {"object": "colorful liquid", "color1": "cyan", "color2": "magenta"},
    {"food": "freshly baked croissant"},
]


class PromptGenerator:
    """Generate viral Shorts prompts using 25 templates or LLM."""

    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            self.use_llm = False
            print(f"[PromptGen] Templates loaded: {len(VIRAL_TEMPLATES)} viral hooks")
            return

        self.client = OpenAI(api_key=api_key)
        self.model = os.environ.get("LLM_MODEL", "gpt-4o")
        self.use_llm = True

    def generate_concepts(self, count: int = 10) -> list[dict]:
        """
        Generate 10 viral Shorts concepts, randomly selected from the 25 templates.

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
        """
        Randomly select `count` templates from the 25-template pool.
        Ensures no duplicate hooks in a single batch.
        """
        import re
        available = list(enumerate(VIRAL_TEMPLATES))
        random.shuffle(available)

        # Pick `count` templates, ensuring hook diversity
        selected = []
        used_hooks = set()
        for idx, template in available:
            if len(selected) >= count:
                break
            # Avoid same hook type in one batch if possible
            hook_base = template["hook"].split(" - ")[0]
            if hook_base not in used_hooks:
                selected.append((idx, template))
                used_hooks.add(hook_base)

        # If we need more and ran out of unique hooks, just add remaining
        if len(selected) < count:
            for idx, template in available:
                if len(selected) >= count:
                    break
                if (idx, template) not in selected:
                    selected.append((idx, template))

        concepts = []
        for i, (template_idx, template) in enumerate(selected):
            # Find template placeholders like {object}, {color}, etc.
            placeholders = set(re.findall(r'\{(\w+)\}', template["template"]))
            if not placeholders:
                placeholders = {"_dummy"}

            # Pick data that has ALL required keys
            best_data = None
            for data in TEMPLATE_DATA:
                data_keys = set(data.keys())
                # Must have all needed keys
                if placeholders.issubset(data_keys):
                    best_data = data
                    break

            # Fallback: pick any data and fill what we can
            if best_data is None:
                best_data = TEMPLATE_DATA[i % len(TEMPLATE_DATA)]

            # Also fill any extra placeholders with generic values
            filled_data = dict(best_data)
            for ph in placeholders:
                if ph not in filled_data:
                    filled_data[ph] = f"beautiful {ph}"

            # Fill template placeholders
            prompt = template["template"]
            for key, value in filled_data.items():
                prompt = prompt.replace(f"{{{key}}}", str(value))

            # Generate title based on hook type
            hook = template["hook"]
            title = self._generate_title(hook, data)

            # All prompts get vertical Shorts emphasis
            if "vertical 9:16" not in prompt:
                prompt += ", vertical 9:16 video, cinematic quality"

            concepts.append({
                "title": title[:95],
                "kling_prompt": prompt,
                "description": (
                    f"{title}\n\n"
                    f"Follow for more satisfying Shorts! 🔥\n"
                    f"@GentleSoul666\n\n"
                    f"#Shorts #Viral #Satisfying #OddlySatisfying #ASMR #Loop #Trending"
                ),
                "tags": [
                    "#Shorts", "#Viral", "#Satisfying", "#OddlySatisfying",
                    "#ASMR", "#Loop", "#Trending"
                ],
                "hook_type": hook,
            })

        print(f"[PromptGen] Selected {len(concepts)} diverse hooks from {len(VIRAL_TEMPLATES)} templates")
        return concepts

    def _generate_title(self, hook: str, data: dict) -> str:
        """Generate a catchy title based on hook type and data."""
        if "壓碎" in hook:
            obj = data.get('object', 'Object').title()
            return f"{obj} gets CRUSHED! 😱 #Shorts"
        elif "墜落" in hook:
            obj = data.get('object', 'Something').title()
            target = data.get('target', 'the ground')
            return f"{obj} vs {target}! 💥 #Shorts"
        elif "爆破" in hook or "泡泡" in hook:
            return f"Satisfying POP! 🎈 #Shorts"
        elif "排列" in hook:
            return f"Satisfying {data.get('objects','Arrangement').title()}! ✨ #Shorts"
        elif "清潔" in hook:
            return f"Satisfying Clean! 🧼 #Shorts"
        elif "巨大" in hook or "微小" in hook:
            small = str(data.get('small_object', 'mini')).title()
            big = str(data.get('big_object', 'giant')).title()
            return f"{small} vs {big} 🤯 #Shorts"
        elif "變色" in hook or "變形" in hook:
            obj = str(data.get('object', 'Something')).title()
            # Remove leading "A " or "An " for cleaner titles
            for prefix in ["A ", "An ", "The "]:
                if obj.startswith(prefix):
                    obj = obj[len(prefix):]
                    break
            return f"Mesmerizing {obj} Transformation! 🌈 #Shorts"
        elif "切割" in hook:
            obj = str(data.get('object', 'Something')).title()
            return f"Satisfying {obj} Slice! 🔪 #Shorts"
        elif "綻放" in hook or "生長" in hook:
            flower = str(data.get('flower', 'Flower')).title()
            return f"Beautiful {flower} Blooming! 🌸 #Shorts"
        elif "觸感" in hook or "刮抹" in hook or "奶油" in hook:
            return f"Oddly Satisfying Texture! 🤲 #Shorts"
        elif "肥皂" in hook:
            return f"Satisfying Soap Cutting! 🧼 #Shorts"
        elif "融化" in hook or "牽絲" in hook:
            food = str(data.get('food', 'Cheese'))
            return f"Epic {food} Pull! 🧀 #Shorts"
        elif "顏料" in hook or "混合" in hook:
            return f"Mesmerizing Paint Mixing! 🎨 #Shorts"
        elif "冰塊" in hook:
            return f"Satisfying Ice Crushing! 🧊 #Shorts"
        elif "沙" in hook:
            return f"Satisfying Sand Cutting! 🏖️ #Shorts"
        elif "水滴" in hook:
            return f"Perfect Water Drop! 💧 #Shorts"
        elif "磁" in hook:
            return f"Mesmerizing Ferrofluid! 🧪 #Shorts"
        elif "火" in hook or "熔岩" in hook or "火焰" in hook:
            return f"Mesmerizing Fire! 🔥 #Shorts"
        elif "彈力" in hook:
            return f"Epic Snap Back! 🪢 #Shorts"
        elif "吸水" in hook:
            return f"Satisfying Water Absorption! 🧽 #Shorts"
        elif "珍珠" in hook:
            return f"Mesmerizing Pearl Cascade! 🐚 #Shorts"
        elif "滋滋" in hook or "烹飪" in hook:
            food = str(data.get('food', 'Food'))
            return f"Sizzling {food}! 🍳 #Shorts"
        elif "醬料" in hook or "淋下" in hook:
            sauce = str(data.get('sauce', 'Sauce')).title()
            food = str(data.get('food', 'Dessert')).title()
            return f"{sauce} on {food}! 🍨 #Shorts"
        else:
            obj = str(data.get('object', 'Something')).title()
            return f"Satisfying {obj}! 🔥 #Shorts"
