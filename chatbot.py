"""
Buddy: a chatbot built with ChatterBot.

ChatterBot learns from example conversations and, for each new message,
finds the most similar example it has seen before and replies with
whatever response followed it. Run this file directly to chat with the
bot in your terminal.

Usage:
    python chatbot.py            # normal chat
    python chatbot.py --debug    # also print the match confidence,
                                  # useful for explaining how matching
                                  # works during a demo/viva
"""

import sys

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from chatterbot.tagging import LowercaseTagger

from training_data import CORPUS_TOPICS, CUSTOM_CONVERSATIONS

# Below this confidence (0-1), the match is too weak to trust, so we
# show a fallback message instead of a random unrelated reply.
CONFIDENCE_THRESHOLD = 0.5


def build_bot():
    """Create and train the chatbot. Training data is stored in a local
    SQLite database, so the bot doesn't need to be retrained every run
    once trained once -- though re-running train() on the same data is
    harmless, it just skips duplicates."""

    bot = ChatBot(
        "Buddy",
        storage_adapter="chatterbot.storage.SQLStorageAdapter",
        database_uri="sqlite:///chatbot_database.sqlite3",
        # LowercaseTagger needs no extra downloads. Swap for the default
        # PosLemmaTagger (and run `python -m spacy download en_core_web_sm`
        # first) for slightly smarter, grammar-aware matching.
        tagger=LowercaseTagger,
    )

    # Custom pairs are trained FIRST. When the corpus below contains an
    # overlapping question (e.g. "How do you work?"), ChatterBot's tie
    # -breaking favors whichever statement was learned first -- so this
    # order guarantees our custom answers win over generic corpus ones.
    print("Training on custom conversations...")
    ListTrainer(bot).train(CUSTOM_CONVERSATIONS)

    print("Training on general-knowledge corpus...")
    ChatterBotCorpusTrainer(bot).train(*CORPUS_TOPICS)

    return bot


def get_reply(bot, user_input, debug=False):
    response = bot.get_response(user_input)

    if debug:
        print(f"  [confidence: {response.confidence:.2f}]")

    if response.confidence < CONFIDENCE_THRESHOLD:
        return "I'm not sure I understand. Could you rephrase that?"

    return str(response)


def main():
    debug = "--debug" in sys.argv

    bot = build_bot()

    print("\nBuddy: Hi! Type 'quit' or 'exit' to end the conversation.\n")

    while True:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nBuddy: Goodbye!")
            break

        if user_input.strip().lower() in {"quit", "exit"}:
            print("Buddy: Goodbye!")
            break

        if not user_input.strip():
            continue

        print(f"Buddy: {get_reply(bot, user_input, debug=debug)}")


if __name__ == "__main__":
    main()
