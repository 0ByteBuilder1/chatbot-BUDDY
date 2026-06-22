"""
GUI for Buddy the chatbot, built with Tkinter (included with Python --
no extra installation needed).

Run with:
    python gui.py
"""

import threading
import tkinter as tk
from tkinter import scrolledtext, font

from chatbot import build_bot, get_reply, CONFIDENCE_THRESHOLD

BOT_NAME = "Buddy"

# --- Colors & fonts -------------------------------------------------
BG_COLOR = "#1e1e2f"
PANEL_COLOR = "#262640"
USER_BUBBLE = "#4f7cff"
BOT_BUBBLE = "#33334d"
TEXT_COLOR = "#f0f0f5"
MUTED_COLOR = "#9090a8"
ENTRY_BG = "#2d2d45"


class ChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{BOT_NAME} — Chatbot")
        self.root.geometry("520x640")
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(420, 480)

        self.bot = None  # filled in once training finishes
        self.debug_mode = tk.BooleanVar(value=False)

        self._build_layout()
        self._show_status("Training Buddy, please wait...")

        # Train on a background thread so the window doesn't freeze
        # while ChatterBot loads the corpus + custom data.
        threading.Thread(target=self._train_bot, daemon=True).start()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_layout(self):
        header = tk.Frame(self.root, bg=PANEL_COLOR, height=56)
        header.pack(fill="x", side="top")

        title_font = font.Font(family="Segoe UI", size=13, weight="bold")
        tk.Label(
            header, text=f"🤖 {BOT_NAME}", bg=PANEL_COLOR, fg=TEXT_COLOR,
            font=title_font, padx=16, pady=12,
        ).pack(side="left")

        tk.Checkbutton(
            header, text="Show confidence", variable=self.debug_mode,
            bg=PANEL_COLOR, fg=MUTED_COLOR, selectcolor=PANEL_COLOR,
            activebackground=PANEL_COLOR, activeforeground=TEXT_COLOR,
            font=("Segoe UI", 9),
        ).pack(side="right", padx=12)

        # --- Chat history ---
        self.chat_area = scrolledtext.ScrolledText(
            self.root, wrap="word", bg=BG_COLOR, fg=TEXT_COLOR,
            font=("Segoe UI", 10), borderwidth=0, padx=12, pady=12,
            state="disabled", cursor="arrow",
        )
        self.chat_area.pack(fill="both", expand=True, padx=8, pady=(8, 0))

        # Tags used to style each side of the conversation differently.
        self.chat_area.tag_configure("user", justify="right", foreground=USER_BUBBLE,
                                      font=("Segoe UI", 10, "bold"), spacing3=2)
        self.chat_area.tag_configure("user_text", justify="right", foreground=TEXT_COLOR,
                                      spacing3=10)
        self.chat_area.tag_configure("bot", justify="left", foreground="#7fd97f",
                                      font=("Segoe UI", 10, "bold"), spacing3=2)
        self.chat_area.tag_configure("bot_text", justify="left", foreground=TEXT_COLOR,
                                      spacing3=10)
        self.chat_area.tag_configure("meta", justify="left", foreground=MUTED_COLOR,
                                      font=("Segoe UI", 8, "italic"), spacing3=14)
        self.chat_area.tag_configure("status", justify="center", foreground=MUTED_COLOR,
                                      font=("Segoe UI", 9, "italic"))

        # --- Input row ---
        input_row = tk.Frame(self.root, bg=BG_COLOR)
        input_row.pack(fill="x", padx=8, pady=8)

        self.entry = tk.Entry(
            input_row, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
            font=("Segoe UI", 11), relief="flat",
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.entry.bind("<Return>", lambda event: self._on_send())
        self.entry.configure(state="disabled")  # enabled once training finishes

        self.send_button = tk.Button(
            input_row, text="Send", command=self._on_send,
            bg=USER_BUBBLE, fg="white", activebackground="#3a63d6",
            relief="flat", font=("Segoe UI", 10, "bold"), padx=18,
            state="disabled",
        )
        self.send_button.pack(side="right")

    # ------------------------------------------------------------------
    # Bot training (background thread)
    # ------------------------------------------------------------------
    def _train_bot(self):
        self.bot = build_bot()
        self.root.after(0, self._on_training_done)

    def _on_training_done(self):
        self._show_status(None)
        self._append_bot_message(
            "Hi! I'm Buddy. Ask me anything, or try 'who created you?' or 'tell me a joke'."
        )
        self.entry.configure(state="normal")
        self.send_button.configure(state="normal")
        self.entry.focus_set()

    # ------------------------------------------------------------------
    # Sending / receiving messages
    # ------------------------------------------------------------------
    def _on_send(self):
        text = self.entry.get().strip()
        if not text or self.bot is None:
            return

        self.entry.delete(0, tk.END)
        self._append_user_message(text)

        # Run matching on a background thread too, in case a future
        # swap to a heavier tagger makes lookups slower -- keeps the
        # window responsive either way.
        threading.Thread(target=self._get_and_show_reply, args=(text,), daemon=True).start()

    def _get_and_show_reply(self, text):
        response = self.bot.get_response(text)
        reply = str(response)
        confidence = response.confidence

        if confidence < CONFIDENCE_THRESHOLD:
            reply = "I'm not sure I understand. Could you rephrase that?"

        self.root.after(0, lambda: self._append_bot_message(reply, confidence))

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    def _append_user_message(self, text):
        self._enable_edit()
        self.chat_area.insert(tk.END, "You\n", "user")
        self.chat_area.insert(tk.END, f"{text}\n", "user_text")
        self._disable_edit_and_scroll()

    def _append_bot_message(self, text, confidence=None):
        self._enable_edit()
        self.chat_area.insert(tk.END, f"{BOT_NAME}\n", "bot")
        self.chat_area.insert(tk.END, f"{text}\n", "bot_text")
        if self.debug_mode.get() and confidence is not None:
            self.chat_area.insert(tk.END, f"confidence: {confidence:.2f}\n", "meta")
        self._disable_edit_and_scroll()

    def _show_status(self, text):
        self._enable_edit()
        # Clear any previous status line by just appending; for a demo
        # app this simple approach is fine since status only appears
        # once at startup.
        if text:
            self.chat_area.insert(tk.END, f"{text}\n", "status")
        self._disable_edit_and_scroll()

    def _enable_edit(self):
        self.chat_area.configure(state="normal")

    def _disable_edit_and_scroll(self):
        self.chat_area.configure(state="disabled")
        self.chat_area.see(tk.END)


def main():
    root = tk.Tk()
    ChatGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
