***

# 🐉 Legendary Adventure Generator

**A D&D 5e Adventure Generator for the Modern Dungeon Master.**

This Python script generates coherent, thematic, and exciting adventure prompts for Dungeons & Dragons 5th Edition. It outputs a beautifully styled HTML file that mimics the look and feel of the official *Player's Handbook* (PHB), ready to be used as a session handout or DM notes.

It goes beyond simple random tables by using **Contextual Themes** (e.g., Gothic Horror, High Fantasy, Underworld) to ensure that your Villain fits the Dungeon, and the Minions fit the Atmosphere.

<img src="https://raw.githubusercontent.com/lady-loredail/adventureDnD/refs/heads/main/images/example_en.png" style="width: 80vw;">

<img src="https://raw.githubusercontent.com/lady-loredail/adventureDnD/refs/heads/main/images/example_es.png" style="width: 80vw;">

## ✨ Features

*   **Thematic Consistency:** No more "Pirates in a Desert." The generator picks a theme (e.g., *Gothic Darkness*) and selects cities, dungeons, and enemies that fit together.
*   **Legendary HTML Output:** Generates a `.html` file with parchment textures, PHB-style fonts (`Cinzel`, `Merriweather`), and a responsive sidebar index.
*   **AI-Powered GM Toolkit (Optional):** Connects to **Ollama** to act as a co-DM. It doesn't write a novel; it generates **actionable GM tools** (sensory details, villain tactics, plot hooks) based on the generated random data.
*   **Multilingual Support:** Native support for English, Spanish, French, German, Italian, and Portuguese via JSON language packs.
*   **Fully Customizable:** Override any random table (names, hooks, twists) using simple CSV/Text files.
*   **Zero Dependencies:** The core script runs with standard Python 3 libraries. No `pip install` required unless you want to use the AI features (which require [Ollama](https://ollama.com/) installed externally).

---

## 🚀 Installation

1.  **Clone or Download** this repository.
2.  Ensure you have **Python 3.6+** installed.
3.  Ensure the `lang_*.json` files are in the same folder as the script.

### For AI Features (Optional)
1.  Install [Ollama](https://ollama.com/).
2.  Pull a model (e.g., Gemma 3, GPT OSS, Llama 3, Mistral):
    ```bash
    ollama pull gemma3:latest
    ```
3.  Start the Ollama server:
    ```bash
    ollama serve
    ```

---

## ⚔️ Usage

Run the script from your terminal:

```bash
python3 adventureDnD.py
```

This generates 1 adventure in English and opens the HTML file automatically.

### Command Line Arguments

| Flag             | Description                                              | Default             |
|:-----------------|:---------------------------------------------------------|:--------------------|
| `-n`, `--number` | Number of adventures to generate.                        | `1`                 |
| `--lang`         | Language code (`en`, `es`, `fr`, `de`, `it`, `pt`).      | `en`                |
| `--hue`          | Main accent color for the HTML (Hex code).               | `#58180D` (D&D Red) |
| `--csv`          | Override internal tables with a custom file (see below). | None                |
| `--ollama`       | Enable AI generation via Ollama.                         | Disabled            |
| `--model`        | Specific LLM model to use (requires `--ollama`).         | `gemma3:latest`     |
| `--host`         | Ollama API Host.                                         | `localhost`         |
| `--port`         | Ollama API Port.                                         | `11434`             |

### Examples

**Generate 5 adventures in Spanish:**
```bash
python3 adventureDnD.py -n 5 --lang es
```

**Generate a "Warlock" themed UI (Purple) in French:**
```bash
python3 adventureDnD.py --lang fr --hue "#4B0082"
```

**Activate the AI DM Assistant:**
```bash
python3 adventureDnD.py --ollama --model llama3
```

---

## 📝 Customization (`--csv`)

You can inject your own creativity into the generator by overriding the internal tables using simple text files.

* **Syntax:** `--csv keyword=filename.txt` or `--csv keyword=filename.csv`
* **Format:** The text file should have **one entry per line** in one column. No headers.

Example file `example/animals.txt`:

```txt
Lion
Elephant
Dolphin
Eagle
Tiger
Penguin
Kangaroo
Panda
Octopus
Wolf
Cow
Horse
Pig
Sheep
Chicken
Goat
Duck
Goose
Turkey
Donkey
```


### Available Keywords

You can overwrite the following tables. Note that **Theme data** (specific dungeons/monsters per theme) is currently handled in the JSON files, but the **Global Narrative** elements can be hot-swapped via CSV.

| Keyword     | Description                               | Example Content                                   |
|:------------|:------------------------------------------|:--------------------------------------------------|
| `patron`    | The NPC giving the quest.                 | `A retired adventurer with a limp`                |
| `hook`      | The inciting incident or motivation.      | `A letter arrives written in blood`               |
| `twist`     | A plot twist revealed at the climax.      | `The princess is a doppelganger`                  |
| `reward`    | What players get at the end.              | `A deed to a haunted manor`                       |
| `danger`    | Traps, puzzles, or environmental hazards. | `A room where gravity reverses`                   |
| `prefixes`  | First part of generated NPC names.        | `Thal`, `Mor`, `Xan`                              |
| `suffixes`  | Last part of generated NPC names.         | `ion`, `gard`, `us`                               |
| `surnames`  | NPC last names/titles.                    | `Stormrage`, `Blackwood`                          |
| `templates` | Logic for generating Adventure Titles.    | `The Curse of {villain}`, `Secrets of {location}` |

### Example Workflow

1.  Create a file named **`my_villains.txt`**:

    ```text
    The patron is actually a Lich
    The dungeon is inside a giant mimic
    The players have been dead all along
    ```

2.  Run the generator using this file to replace the default "Twists":

    ```bash
    python3 adventureDnD.py --csv twist=my_villains.txt
    ```

If you don't have a custom file, you can try this just for fun:
```bash
python3 adventureDnD.py --ollama --csv twist=example/animals.txt
```

You can also use a CSV file if you wish, but remember to use only one column without headers.

---

## 🤖 AI Integration (Ollama)

When you use the `--ollama` flag, the script performs a "Deep Dive" into the generated random data.

It sends the specific context (Theme, Villain, Dungeon, Twist) to the LLM and asks for **Game Master Tools**, not stories.

*   **Intro:** Provides actionable hook ideas to start the session.
*   **Journey:** Describes sensory details (smell, sound) and mechanics for the generated Trap/Puzzle.
*   **Climax:** Suggests combat tactics for the Villain and foreshadowing for the Twist.
*   **Resolution:** details the properties of the reward and future plot consequences.

*Note: The AI output language will match the selected `--lang`.*

---

## 🌍 Supported Languages

The project includes JSON language packs. Translations are generated automatically;
if you encounter an error or unnatural phrasing, please notify me so it can be fixed.
To add a new language, simply copy `lang_en.json` to `lang_XX.json` and translate the values.

*   🇺🇸 **English** (`en`)
*   🇪🇸 **Español** (`es`)
*   🇫🇷 **Français** (`fr`)
*   🇩🇪 **Deutsch** (`de`)
*   🇮🇹 **Italiano** (`it`)
*   🇵🇹 **Português** (`pt`)

---

## 📜 License

This project is open-source under a [MIT License](https://mit-license.org/). Feel free to modify, fork, and use it for your home games.

*Happy Adventuring!*
