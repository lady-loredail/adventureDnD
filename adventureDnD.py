#!/usr/bin/env python3
import random
import os
import webbrowser
import argparse
import json
import urllib.request
import urllib.error
import sys
from datetime import datetime

# ==============================================================================
# 1. GLOBAL STATE & LOADING
# ==============================================================================

CURRENT_DATA = {}

def load_language_pack(lang_code):
    global CURRENT_DATA
    filename = f"lang_{lang_code}.json"

    if not os.path.exists(filename):
        print(f"❌ Critical Error: Language file '{filename}' not found.")
        sys.exit(1)

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            CURRENT_DATA = json.load(f)
        print(f"🌍 Language loaded: {lang_code.upper()} from '{filename}'")
    except Exception as e:
        print(f"❌ Error loading language: {e}")
        sys.exit(1)

def load_csv_override(key, filepath):
    if not os.path.exists(filepath):
        print(f"❌ Critical Error: CSS/TXT file '{filepath}' not found.")
        sys.exit(1)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        if lines:
            if key in CURRENT_DATA.get("global_tables", {}):
                CURRENT_DATA["global_tables"][key] = lines
            elif key in CURRENT_DATA.get("names", {}):
                CURRENT_DATA["names"][key] = lines
            elif key == "templates":
                CURRENT_DATA["templates"] = lines
    except Exception:
        print(f"❌ Critical Error: CSS/TXT file '{filepath}' cannot be parsed.")
        sys.exit(1)
        pass

def process_csv_arguments(csv_args):
    if not csv_args: return
    for item in csv_args:
        if "=" in item:
            key, path = item.split("=", 1)
            load_csv_override(key.lower(), path)

# ==============================================================================
# 2. GENERATORS
# ==============================================================================

def generate_name():
    names_db = CURRENT_DATA["names"]
    prefix = random.choice(names_db["prefixes"])
    suffix = random.choice(names_db["suffixes"])
    name = prefix + suffix
    if random.random() > 0.4:
        return f"{name} {random.choice(names_db['surnames'])}"
    return name

def generate_title(villain, location):
    templates = CURRENT_DATA.get("templates", ["{villain}'s Quest"])
    raw_template = random.choice(templates)
    return raw_template.replace("{villain}", villain).replace("{location}", location)

def clean_llm_response(text):
    return text.replace("```html", "").replace("```", "").strip()

def query_ollama(context_data, section, config):
    """
    Generates GM Tools/Ideas for a specific section.
    """
    instruction_lang = CURRENT_DATA["meta"]["llm_instruction"]
    model = config['model']

    # --- PROMPTS FOCUSED ON GM TOOLS (NOT NOVELS) ---

    prompts = {
        "intro": f"""
        Provide 2 or 3 specific plot hooks to introduce the adventurers to the Patron ({context_data['patron']}) in {context_data['city']}.
        Focus on how to motivate them using this Hook: "{context_data['hook']}".
        Do not write dialogue; describe opportunities for the GM to start the session. Use 500 approximately words.
        """,

        "journey": f"""
        Suggest sensory details (sounds, smells, visuals) to establish the {context_data['atmosphere']} atmosphere in the {context_data['dungeon']}.
        Then, explain how the Danger/Puzzle ("{context_data['danger']}" and "{context_data['enemies']}") works mechanically or narratively.
        Give the GM ideas on how to challenge the players without solving it for them. Use 500 approximately words.
        """,

        "climax": f"""
        Outline a strategy or tactics the Villain ({context_data['villain']}) might use during the confrontation.
        Then, provide subtle clues or events that can foreshadow the surprising unexpected Twist ("{context_data['twist']}") before it is fully revealed. Use 500 approximately words.
        """,

        "resolution": f"""
        Describe the mystical or political properties of the Reward ("{context_data['reward']}").
        Finally, suggest one future consequence or plot hook that arises from completing this adventure (e.g., an enemy made, a secret revealed). Use 500 approximately words.
        """
    }

    current_task = prompts.get(section, "Provide GM suggestions.")

    print(f"   🤖 designing '{section}' ({model})...")

    final_prompt = f"""
    You are an assistant for a D&D 5e Game Master (GM).
    Your job is to generate IDEAS and TOOLS for the GM, NOT to write a story or novel.

    LANGUAGE: {instruction_lang}.
    PERSPECTIVE: Always use Third Person (e.g., "The adventurers might find...").

    ADVENTURE CONTEXT:
    - Title: {context_data['title']}
    - Theme: {context_data['theme']}
    - Villain: {context_data['villain']} ({context_data['villain_desc']})
    - Twist: {context_data['twist']}

    YOUR TASK:
    {current_task}

    FORMATTING RULES:
    - Return ONLY HTML tags: <p>, <strong>, <em>, <ul>, <li>.
    - Use <ul> for lists of ideas.
    - Keep it concise (approx 100-120 words).
    - NO code blocks. NO <html> headers.
    """

    payload = json.dumps({
        "model": model,
        "prompt": final_prompt,
        "stream": False,
        "options": {"temperature": 0.7} # Slightly lower temp for more coherent instructions
    }).encode('utf-8')

    try:
        url = f"http://{config['host']}:{config['port']}/api/generate"
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as res:
            return clean_llm_response(json.loads(res.read().decode('utf-8')).get('response', ''))
    except Exception as e:
        return f"<p style='color:red'><em>Oracle Error ({section}): {e}</em></p>"

def generate_adventure(index, ollama_config=None):
    themes_db = CURRENT_DATA["themes"]
    theme_key = random.choice(list(themes_db.keys()))
    theme = themes_db[theme_key]
    global_tables = CURRENT_DATA["global_tables"]

    villain_name = generate_name()
    patron_name = generate_name()
    location = random.choice(theme["cities"])
    dungeon = random.choice(theme["dungeons"])
    dungeon_short = dungeon.split(" ")[0]
    title = generate_title(villain_name, dungeon_short)

    # Basic Data Structure
    adv = {
        "id": f"adv_{index}",
        "title": title,
        "icon": theme["icon"],
        "theme_name": theme_key.replace("_", " "),
        "theme_desc": theme["description"],
        "intro": {
            "city": location,
            "patron": f"{patron_name}, {random.choice(global_tables['patron']).lower()}",
            "hook": random.choice(global_tables['hook']),
            "encounter": f"{random.choice(theme['atmosphere']).capitalize()}."
        },
        "development": {
            "dungeon": dungeon,
            "atmosphere": random.choice(theme['atmosphere']),
            "enemies": random.choice(theme['minions']),
            "danger": random.choice(global_tables["danger"])
        },
        "climax": {
            "villain_name": villain_name,
            "villain_desc": random.choice(theme["enemies"]),
            "twist": random.choice(global_tables["twist"])
        },
        "resolution": {
            "reward": random.choice(global_tables["reward"])
        },
        "ai": {
            "intro": None,
            "journey": None,
            "climax": None,
            "resolution": None
        }
    }

    # If AI is enabled, generate content for each section
    if ollama_config:
        context_data = {
            "title": adv['title'],
            "theme": adv['theme_desc'],
            "city": adv['intro']['city'],
            "patron": adv['intro']['patron'],
            "hook": adv['intro']['hook'],
            "dungeon": adv['development']['dungeon'],
            "enemies": adv['development']['enemies'],
            "atmosphere": adv['development']['atmosphere'],
            "danger": adv['development']['danger'],
            "villain": adv['climax']['villain_name'],
            "villain_desc": adv['climax']['villain_desc'],
            "twist": adv['climax']['twist'],
            "reward": adv['resolution']['reward']
        }

        adv['ai']['intro'] = query_ollama(context_data, "intro", ollama_config)
        adv['ai']['journey'] = query_ollama(context_data, "journey", ollama_config)
        adv['ai']['climax'] = query_ollama(context_data, "climax", ollama_config)
        adv['ai']['resolution'] = query_ollama(context_data, "resolution", ollama_config)

    return adv

# ==============================================================================
# 3. HTML GENERATION
# ==============================================================================

def create_html(adventures, hue):
    ui = CURRENT_DATA["ui"]
    css = f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Merriweather:ital,wght@0,300;0,400;0,700;1,400&display=swap');
        :root {{ --main-hue: {hue}; --parchment: #fdf1dc; --text: #1c1c1c; --sidebar-w: 300px; }}
        body {{ background-color: var(--parchment); background-image: url("https://www.transparenttextures.com/patterns/cream-paper.png"); color: var(--text); font-family: 'Merriweather', serif; margin: 0; display: flex; min-height: 100vh; }}
        .sidebar {{ width: var(--sidebar-w); background: #222; border-right: 5px solid var(--main-hue); padding: 20px; position: fixed; height: 100%; overflow-y: auto; color: #eee; }}
        .sidebar h2 {{ font-family: 'Cinzel', serif; color: var(--parchment); text-align: center; border-bottom: 2px solid var(--main-hue); padding-bottom: 15px; }}
        .index-list {{ list-style: none; padding: 0; }}
        .index-link {{ display: block; color: #aaa; text-decoration: none; padding: 8px; border-radius: 4px; transition: 0.2s; }}
        .index-link:hover {{ color: white; background: var(--main-hue); }}
        .main-content {{ margin-left: var(--sidebar-w); padding: 60px; flex-grow: 1; max-width: 900px; }}
        h1 {{ font-family: 'Cinzel', serif; color: var(--main-hue); font-size: 3.5em; border-bottom: 3px double var(--main-hue); margin-bottom: 40px; }}
        details {{ margin-bottom: 40px; background: rgba(255, 255, 255, 0.5); border: 1px solid #d4c4a0; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
        summary {{ padding: 15px; cursor: pointer; list-style: none; background: rgba(0,0,0,0.03); transition: 0.3s; }}
        summary:hover {{ background: rgba(0,0,0,0.08); }}
        .adv-title {{ font-family: 'Cinzel', serif; color: var(--main-hue); font-size: 1.8em; margin: 0; }}
        .adv-meta {{ font-size: 0.75em; text-transform: uppercase; color: #666; margin-top: 5px; }}
        .adv-body {{ padding: 30px; line-height: 1.6; }}
        h3 {{ font-family: 'Cinzel', serif; color: #111; font-size: 1.4em; border-bottom: 1px solid #c9ad6a; margin-top: 30px; }}
        .box {{ background-color: #f7f2e6; padding: 15px; border: 1px solid #c9ad6a; margin: 15px 0; font-style: italic; }}

        /* AI Box Style */
        .llm-box {{
            padding: 15px;
            border-left: 4px solid var(--main-hue);
            background: rgba(0,0,0,0.03);
            margin-bottom: 20px;
            font-family: 'Merriweather', serif;
            font-size: 0.95em;
            color: #333;
        }}
        .llm-box::before {{
            content: "✦ GM TOOLKIT";
            display: block;
            font-family: 'Cinzel', serif;
            font-size: 0.75em;
            font-weight: bold;
            color: var(--main-hue);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 1px solid rgba(0,0,0,0.1);
            padding-bottom: 4px;
        }}
        .llm-box ul {{ margin: 0; padding-left: 20px; }}
        .llm-box li {{ margin-bottom: 5px; }}

        strong {{ color: var(--main-hue); }}
        ::-webkit-scrollbar {{ width: 10px; }}
        ::-webkit-scrollbar-track {{ background: #222; }}
        ::-webkit-scrollbar-thumb {{ background: var(--main-hue); }}
        </style>
        <script>
        function openAdventure(id) {{
            const target = document.getElementById(id);
            if(target) {{ target.setAttribute("open", "true"); setTimeout(() => {{ target.scrollIntoView({{ behavior: "smooth", block: "start" }}); }}, 100); }}
        }}
        </script>"""

    idx_html = "".join([f'<li><a href="#{adv["id"]}" class="index-link" onclick="openAdventure(\'{adv["id"]}\')">{adv["icon"]} {adv["title"]}</a></li>' for adv in adventures])

    content_html = ""
    for adv in adventures:
        def get_ai(key):
            return f'<div class="llm-box">{adv["ai"][key]}</div>' if adv["ai"][key] else ""

        content_html += f"""
        <details id="{adv['id']}">
            <summary><div class="adv-header"><h2 class="adv-title">{adv['title']}</h2><div class="adv-meta">{adv['theme_name']} | {adv['theme_desc']}</div></div></summary>
            <div class="adv-body">

                <h3>{ui['adv_start']}</h3>
                {get_ai('intro')}
                <p><strong>{ui['adv_location']}:</strong> {adv['intro']['city']}</p>
                <div class="box">"{adv['intro']['encounter']}"</div>
                <p><strong>{ui['adv_patron']}:</strong> {adv['intro']['patron']}</p>
                <p><strong>{ui['adv_mission']}:</strong> {adv['intro']['hook']}</p>

                <h3>{ui['adv_development']}</h3>
                {get_ai('journey')}
                <p><strong>{ui['adv_travel']}:</strong> {adv['development']['dungeon']}</p>
                <ul>
                    <li>{ui['adv_atmosphere']}: {adv['development']['atmosphere']}</li>
                    <li>{ui['adv_enemies']}: {adv['development']['enemies']}</li>
                    <li>{ui['adv_danger']}: {adv['development']['danger']}</li>
                </ul>

                <h3>{ui['adv_climax']}</h3>
                {get_ai('climax')}
                <p><strong>{ui['adv_villain']}:</strong> {adv['climax']['villain_name']} ({adv['climax']['villain_desc']})</p>
                <div class="box"><strong>{ui['adv_twist']}:</strong> {adv['climax']['twist']}</div>

                <h3>{ui['adv_reward']}</h3>
                {get_ai('resolution')}
                <p>{adv['resolution']['reward']}</p>
            </div>
        </details>"""

    full_html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{ui['main_title']}</title>{css}</head><body>
    <div class="sidebar"><h2>{ui['sidebar_title']}</h2><ul class="index-list">{idx_html}</ul></div>
    <div class="main-content"><h1>{ui['main_title']}</h1>{content_html}
    <div style="text-align:center;margin-top:50px;color:#888;font-size:0.8em;">{ui['generated_on']} {datetime.now().strftime("%d/%m/%Y")}</div></div></body></html>"""

    filename = "legendary_adventures.html"
    with open(filename, "w", encoding="utf-8") as f: f.write(full_html)
    return filename

def main():
    parser = argparse.ArgumentParser(description='D&D Legendary Adventure Generator')
    parser.add_argument('-n', '--number', type=int, default=1)
    parser.add_argument('--hue', type=str, default='#58180D')
    parser.add_argument('--lang', type=str, default='en')
    parser.add_argument('--csv', action='append', help='Override: key=file.csv')
    parser.add_argument('--ollama', action='store_true')
    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--port', type=str, default='11434')
    parser.add_argument('--model', type=str, default='gemma3:latest')
    args = parser.parse_args()

    load_language_pack(args.lang)
    process_csv_arguments(args.csv)

    ollama_config = {"host": args.host, "port": args.port, "model": args.model} if args.ollama else None
    print(f"🎲 Generating {args.number} adventures ({args.lang.upper()})...")

    adventures_list = [generate_adventure(i, ollama_config) for i in range(args.number)]
    output_file = create_html(adventures_list, args.hue)

    print(f"✨ Done! Opening {output_file}...")
    try: webbrowser.open('file://' + os.path.realpath(output_file))
    except: pass

if __name__ == "__main__":
    main()
