#  Buddy — Python Chatbot using ChatterBot

A terminal-based conversational chatbot built with the [ChatterBot](https://github.com/gunthercox/ChatterBot) Python library. Buddy learns from example conversations and uses **string similarity matching** to find the best response to whatever the user types — no hardcoded if-else logic, no internet connection required.

> **Internship Project** | Built as a demonstration of retrieval-based chatbot design using Python.

---

##  Table of Contents

- [Demo](#-demo)
- [How It Works](#-how-it-works)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Setup & Installation](#-setup--installation)
- [Running the Chatbot](#-running-the-chatbot)
- [Training the Bot](#-training-the-bot)
- [Adding Your Own Training Data](#-adding-your-own-training-data)
- [Key Design Decisions](#-key-design-decisions)

---

##  Demo

```
Training on custom conversations...
Training on general-knowledge corpus...

Buddy: Hi! Type 'quit' or 'exit' to end the conversation.

You: Hi
Buddy: Hello! How can I help you today?

You: What is your name?
Buddy: My name is Buddy, a general-purpose chatbot.

You: How do you work?
Buddy: I use string similarity — specifically Levenshtein distance — to compare
your message against everything I was trained on. The closest match wins,
and I reply with whatever response followed that match during training.

You: Tell me a joke
Buddy: Why do programmers prefer dark mode? Because light attracts bugs!

You: wht iz ur naem
Buddy: My name is Buddy, a general-purpose chatbot.

You: exit
Buddy: Goodbye!
```

> Notice the last example — `"wht iz ur naem"` (with typos) still returns the correct answer. This is string similarity matching in action, not if-else.

---

##  How It Works

Buddy is a **retrieval-based chatbot**. It does not generate new text — instead it:

1. **Stores** all training examples in a local SQLite database.
2. **Tags** every statement by normalizing it to lowercase for indexing.
3. **Searches** the database using [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance) to find the closest match to the user's input.
4. **Returns** the response that was paired with the best matching statement during training, along with a **confidence score** between 0 and 1.
5. **Falls back** gracefully — if the confidence score is below 0.5, Buddy says it doesn't understand rather than returning an unrelated answer.

### Why this is NOT if-else

| Feature | If-Else Chatbot | Buddy (Similarity Matching) |
|---|---|---|
| Handles typos | ❌ No | ✅ Yes |
| Handles rephrasing | ❌ No | ✅ Yes |
| Confidence score | ❌ Only true/false | ✅ Decimal (e.g. 0.87) |
| Scales with more data | ❌ More conditions | ✅ More training examples |
| Learns from corpus | ❌ No | ✅ Yes (1000+ examples) |

---

##  Project Structure

```
chatbot/
├── chatbot.py           # Core bot logic — training + matching (used by both CLI and GUI)
├── gui.py               # Tkinter desktop GUI (reuses chatbot.py, no duplicated logic)
├── training_data.py     # All training conversations in one place
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── chatbot_database.sqlite3   # Auto-generated on first run (do not edit)
```

---

##  Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.10+ | Core language |
| [ChatterBot 1.2.13](https://pypi.org/project/ChatterBot/) | Chatbot engine (retrieval-based NLP) |
| [chatterbot-corpus 1.3.3](https://pypi.org/project/chatterbot-corpus/) | Pre-built training datasets (greetings, humor, science, etc.) |
| SQLite | Local database for storing training statements |
| PyYAML | Parsing the corpus `.yml` files |

---

##  Setup & Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/0ByteBuilder1/chatbot-BUDDY.git
cd chatbot-BUDDY
```

**2. (Recommended) Create a virtual environment**
```bash
# Using venv
python -m venv chatbot_env
chatbot_env\Scripts\activate      # Windows
source chatbot_env/bin/activate   # macOS / Linux

# OR using conda
conda create -n chatbot_env python=3.10
conda activate chatbot_env
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

---

##  Running the Chatbot

**Normal mode:**
```bash
python chatbot.py
```

**Debug mode** — prints the confidence score for every response (great for understanding how matching works):
```bash
python chatbot.py --debug
```

Example debug output:
```
You: How are you?
  [confidence: 0.92]
Buddy: I'm doing well, thanks for asking!
```

Type `exit` or `quit`, or press `Ctrl+C` to stop the bot.

---

##  GUI Version

A desktop chat window is also available, built with **Tkinter** (included with Python — no extra installation needed).

```bash
python gui.py
```

This opens a chat window with a message history, a text input box, and a Send button (Enter key also works). Check **"Show confidence"** in the top-right corner to display the match confidence score under each of Buddy's replies — useful for demonstrating how similarity matching works, and for showing a typo (e.g. "wht iz ur naem") still matches correctly, just with a lower score.

**Design note:** `gui.py` contains *zero* chatbot logic. It imports `build_bot()` and `get_reply()`/`CONFIDENCE_THRESHOLD` directly from `chatbot.py` and only handles the window/display. This keeps the interface and the matching logic fully decoupled — you could swap in a completely different GUI framework later without touching the bot's brain at all.

---

##  Training the Bot

The bot is trained from two sources:

### 1. Custom conversations (`training_data.py → CUSTOM_CONVERSATIONS`)
Hand-written question/answer pairs that give the bot its identity and guarantee key demo questions always work. Covers greetings, identity (name, creator), how-it-works explanations, jokes, and farewells.

### 2. ChatterBot corpus (`training_data.py → CORPUS_TOPICS`)
Pre-built `.yml` files shipped with `chatterbot-corpus`, covering:

| Topic | Topic | Topic |
|---|---|---|
| Greetings | Conversations | Humor |
| Trivia | Science | Literature |
| Movies | Food | History |
| Sports | AI | Bot Profile |

Combined, these give the bot over **1,000 example exchanges** to match against.

### Training order matters
Custom data is trained **before** the corpus intentionally. ChatterBot's tie-breaking rule favors whichever statement was learned first — so training custom data first ensures our specific answers always win over generic corpus ones when the same question appears in both.

---

##  Adding Your Own Training Data

Open `training_data.py` and add question/answer pairs to `CUSTOM_CONVERSATIONS`. The format is a flat list — each question is followed immediately by its reply:

```python
CUSTOM_CONVERSATIONS = [
    "What is machine learning?",
    "Machine learning is a branch of AI where systems learn from data.",

    "Give me an example of ML",
    "Email spam filters, Netflix recommendations, and voice assistants all use ML.",

    # add more pairs below...
]
```

After editing, **delete `chatbot_database.sqlite3`** and rerun — the bot must rebuild its database from scratch to pick up the changes:

```bash
# Windows
del chatbot_database.sqlite3
python chatbot.py

# macOS / Linux
rm chatbot_database.sqlite3
python chatbot.py
```

---

##  Key Design Decisions

**`LowercaseTagger` instead of the default `PosLemmaTagger`**
ChatterBot's default tagger uses spaCy for part-of-speech analysis, which requires downloading a separate language model. `LowercaseTagger` normalizes text by lowercasing only — no download needed, works immediately after `pip install`, and performs well for general conversation.

**Confidence threshold fallback**
ChatterBot always returns *something*, even for unrecognized input. A custom threshold check (set to `0.5`) was added so that low-confidence matches return `"I'm not sure I understand"` instead of an unrelated reply. This makes the bot's behavior predictable and honest.

**SQLite storage adapter**
Training data is persisted in a local SQLite file. This means the bot only needs to train once — subsequent runs load from the database instantly. Delete the `.sqlite3` file to force a full retrain.

---

##  License

This project is open-source and available under the [MIT License](LICENSE).
