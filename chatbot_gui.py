# chatbot_gui.py
# Pink & purple themed chat GUI, canvas-based message area (PACK inside messages frame)
# Place beside chatbot.py, logic_layer.py, nlu.py

import tkinter as tk
import customtkinter as ctk
from datetime import datetime
from chatbot import handle_query

# -----------------------
# Appearance / theme
# -----------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")  # keeps CTk internal styling consistent

# Colors (pink + purple theme)
BG = "#1e0c1f"             # deep background
PANEL = "#2b1027"          # panel background
PRIMARY_PINK = "#ff4fa3"   # bright pink (send button, accents)
SECONDARY_PURPLE = "#7b3fb6"  # purple (bot bubble)
USER_PINK = "#ff6fbf"      # user bubble
BOT_LILAC = "#f3e6fb"      # bot bubble light
TEXT_WHITE = "#ffffff"
TEXT_DARK = "#222222"
STATUS_GRAY = "#cdb3cd"

# Timing
TYPING_INTERVAL_MS = 200
FAST_REPLY_DELAY_MS = 10    # tiny delay so typing bubble is drawn before backend runs

# -----------------------
# Chat GUI
# -----------------------
class ChatBotGUI:
    def __init__(self):
        # root window
        self.root = ctk.CTk()
        self.root.title("Support Chatbot — Pink & Purple")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.root.configure(fg_color=BG)

        # top-level grid layout: left sidebar, right chat area
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # state
        self.msg_count = 0
        self.typing_active = False
        self._typing_after_id = None

        # build UI
        self._build_header()
        self._build_sidebar()
        self._build_chat_area_canvas()
        self._build_input_bar()

        # focus and initial bot message
        self.input_text.focus_set()
        self.root.after(250, lambda: self.post_bot_message(
            "Hello! 👋 I'm your support assistant. Ask me about billing, orders, password resets, app issues, subscriptions and more."
        ))

    # -----------------------
    # header
    # -----------------------
    def _build_header(self):
        header = ctk.CTkFrame(self.root, height=88, fg_color=PANEL, corner_radius=10)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12,6))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(header, text="Support Chatbot", font=ctk.CTkFont(size=22, weight="bold"), text_color=TEXT_WHITE)
        title.grid(row=0, column=0, sticky="w", padx=16, pady=(10,0))

        subtitle = ctk.CTkLabel(header, text="Intelligent assistant — billing • orders • account help", font=ctk.CTkFont(size=11), text_color="#f0dff0")
        subtitle.grid(row=1, column=0, sticky="w", padx=16, pady=(0,10))

        # right controls
        ctrl = ctk.CTkFrame(header, fg_color="transparent")
        ctrl.grid(row=0, column=1, rowspan=2, sticky="e", padx=12)
        self.theme_btn = ctk.CTkButton(ctrl, text="🌙 Dark", width=110, command=self._toggle_theme)
        self.theme_btn.grid(row=0, column=0, padx=(6,6))
        clear_btn = ctk.CTkButton(ctrl, text="Clear", fg_color="#E04E50", width=90, command=self.clear_chat)
        clear_btn.grid(row=0, column=1, padx=(6,6))
        about_btn = ctk.CTkButton(ctrl, text="About", width=90, command=self._show_about)
        about_btn.grid(row=0, column=2, padx=(6,4))

    # -----------------------
    # sidebar (left)
    # -----------------------
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self.root, width=300, fg_color=PANEL, corner_radius=10)
        sidebar.grid(row=1, column=0, sticky="nsw", padx=(12,6), pady=(6,12))
        sidebar.grid_rowconfigure(6, weight=1)

        avatar = ctk.CTkLabel(sidebar, text="🤖", font=ctk.CTkFont(size=32))
        avatar.grid(row=0, column=0, sticky="w", padx=12, pady=(12,4))
        name = ctk.CTkLabel(sidebar, text="Support Bot", font=ctk.CTkFont(size=16, weight="bold"))
        name.grid(row=0, column=1, sticky="w", padx=6, pady=(12,4))

        desc = ("Hi! I'm your virtual assistant. I can help with billing, refunds, order tracking, password resets, "
                "app issues, subscriptions and integrations. Type your question below.")
        desc_lbl = ctk.CTkLabel(sidebar, text=desc, wraplength=240, justify="left")
        desc_lbl.grid(row=1, column=0, columnspan=2, sticky="w", padx=12, pady=(6,12))

        caps_title = ctk.CTkLabel(sidebar, text="I can assist with:", font=ctk.CTkFont(size=13, weight="bold"))
        caps_title.grid(row=2, column=0, columnspan=2, sticky="w", padx=12, pady=(6,4))

        caps = ["Billing & Invoices", "Refunds & Disputes", "Order tracking", "Password & Login help",
                "App crashes & Bug reports", "Account security & 2FA", "Data export requests", "Subscription changes"]
        for idx, c in enumerate(caps):
            lbl = ctk.CTkLabel(sidebar, text=f"•  {c}", anchor="w")
            lbl.grid(row=3+idx, column=0, columnspan=2, sticky="w", padx=12, pady=2)

    # -----------------------
    # chat area (canvas + messages_frame inside)
    # Using PACK inside messages_frame to stack messages vertically
    # -----------------------
    def _build_chat_area_canvas(self):
        container = ctk.CTkFrame(self.root, fg_color=BG, corner_radius=10)
        container.grid(row=1, column=1, sticky="nsew", padx=(6,12), pady=(6,12))
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Canvas for scrolling
        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=(8,0), pady=12)

        # Vertical scrollbar
        vsb = ctk.CTkScrollbar(container, orientation="vertical", command=self._on_scroll)
        vsb.grid(row=0, column=1, sticky="ns", pady=12, padx=(4,8))
        # Link canvas to scrollbar
        self.canvas.configure(yscrollcommand=vsb.set)

        # inner frame that will contain messages (we pack inside this)
        self.messages_frame = tk.Frame(self.canvas, bg=BG)
        # create window on canvas
        self.canvas_window = self.canvas.create_window((0,0), window=self.messages_frame, anchor="nw")

        # Bind sizing
        self.messages_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # status label below
        self.status_label = ctk.CTkLabel(container, text="Ready to help!", text_color=STATUS_GRAY)
        self.status_label.grid(row=1, column=0, sticky="w", padx=12, pady=(6,10))

    def _on_scroll(self, *args):
        # pass through to canvas yview
        try:
            self.canvas.yview(*args)
        except Exception:
            pass

    def _on_frame_configure(self, event=None):
        # update scroll region to match inner frame size
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # auto-scroll to bottom when new message added
        # (we don't automatically force-scroll during user manual scroll; user can scroll)
        # We'll keep it simple: always move to bottom after small delay
        self.root.after(40, lambda: self.canvas.yview_moveto(1.0))

    def _on_canvas_configure(self, event):
        # ensure inner frame width matches canvas width
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    # -----------------------
    # input bar
    # -----------------------
    def _build_input_bar(self):
        footer = ctk.CTkFrame(self.root, fg_color=PANEL, corner_radius=10, height=100)
        footer.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(0,12))
        footer.grid_columnconfigure(0, weight=1)

        self.input_text = ctk.CTkTextbox(footer, height=78, wrap="word", font=ctk.CTkFont(size=13))
        self.input_text.grid(row=0, column=0, padx=(12,8), pady=10, sticky="ew")
        self.input_text.bind("<Return>", self._on_enter_pressed)
        self.input_text.bind("<Shift-Return>", lambda e: None)  # allow Shift+Enter newline (no-op here)

        right = ctk.CTkFrame(footer, fg_color="transparent")
        right.grid(row=0, column=1, padx=(0,12), pady=10)

        self.send_btn = ctk.CTkButton(right, text="Send", fg_color=PRIMARY_PINK, hover_color="#ff77c6",
                                     width=110, height=78, command=self._on_send_clicked)
        self.send_btn.grid(row=0, column=0)

        # quick suggestion buttons
        qs = ctk.CTkFrame(footer, fg_color="transparent")
        qs.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(0,10))
        tips = ["Where is my order?", "Refund status", "Reset my password", "Cancel subscription"]
        for i, t in enumerate(tips):
            b = ctk.CTkButton(qs, text=t, fg_color="#371033", width=170, command=lambda txt=t: self._quick_send(txt))
            b.grid(row=0, column=i, padx=6)

    # -----------------------
    # message posting helpers (PACK inside messages_frame)
    # -----------------------
    def post_user_message(self, text: str):
        # wrapper fills width; inside it we place bubble anchored right
        wrapper = tk.Frame(self.messages_frame, bg=BG)
        wrapper.pack(fill="x", pady=6, padx=8)

        # bubble (CTkFrame for consistent styling)
        bubble = ctk.CTkFrame(wrapper, fg_color=USER_PINK, corner_radius=14)
        bubble.pack(anchor="e", padx=(40,8))
        msg_lbl = ctk.CTkLabel(bubble, text=text, wraplength=520, justify="left", text_color=TEXT_WHITE, font=ctk.CTkFont(size=13))
        msg_lbl.grid(row=0, column=0, padx=12, pady=(10,8))
        time_lbl = ctk.CTkLabel(bubble, text=datetime.now().strftime("%H:%M"), text_color="#ffd8ee", font=ctk.CTkFont(size=9))
        time_lbl.grid(row=1, column=0, sticky="e", padx=10, pady=(0,8))

        self.msg_count += 1
        self._maybe_scroll_to_bottom()

    def post_bot_message(self, text: str):
        wrapper = tk.Frame(self.messages_frame, bg=BG)
        wrapper.pack(fill="x", pady=6, padx=8)

        bubble = ctk.CTkFrame(wrapper, fg_color=BOT_LILAC, corner_radius=14)
        bubble.pack(anchor="w", padx=(8,40))
        msg_lbl = ctk.CTkLabel(bubble, text=text, wraplength=520, justify="left", text_color=TEXT_DARK, font=ctk.CTkFont(size=13))
        msg_lbl.grid(row=0, column=0, padx=12, pady=(10,8))
        time_lbl = ctk.CTkLabel(bubble, text=datetime.now().strftime("%H:%M"), text_color="#7B6B7B", font=ctk.CTkFont(size=9))
        time_lbl.grid(row=1, column=0, sticky="w", padx=10, pady=(0,8))

        self.msg_count += 1
        self._maybe_scroll_to_bottom()

    # -----------------------
    # typing animation (in same messages_frame)
    # -----------------------
    def _start_typing(self):
        if self.typing_active:
            return
        self.typing_active = True
        self.status_label.configure(text="Support Bot is typing...")
        # create typing bubble
        self.typing_wrapper = tk.Frame(self.messages_frame, bg=BG)
        self.typing_wrapper.pack(fill="x", pady=6, padx=8)

        self.typing_bubble = ctk.CTkFrame(self.typing_wrapper, fg_color=BOT_LILAC, corner_radius=14)
        self.typing_bubble.pack(anchor="w", padx=(8,40))
        self._typing_label = ctk.CTkLabel(self.typing_bubble, text="Typing", text_color="#9a8799", font=ctk.CTkFont(size=13))
        self._typing_label.grid(row=0, column=0, padx=12, pady=(10,8))
        self._typing_dot_state = 0
        self._animate_typing()

        # do not increment msg_count yet; when replaced by bot message msg_count increases
        self._maybe_scroll_to_bottom()

    def _animate_typing(self):
        if not self.typing_active:
            return
        states = ["Typing", "Typing.", "Typing..", "Typing..."]
        self._typing_label.configure(text=states[self._typing_dot_state % len(states)])
        self._typing_dot_state += 1
        self._typing_after_id = self.root.after(TYPING_INTERVAL_MS, self._animate_typing)

    def _stop_typing(self):
        if not self.typing_active:
            return
        self.typing_active = False
        self.status_label.configure(text="Ready to help!")
        if self._typing_after_id:
            try:
                self.root.after_cancel(self._typing_after_id)
            except Exception:
                pass 
            self._typing_after_id = None
        try:
            self.typing_wrapper.destroy()
        except Exception:
            pass

    # -----------------------
    # input events + backend call
    # -----------------------
    def _on_enter_pressed(self, event):
        if not event.state & 0x1:
            self._on_send_clicked()
            return "break"
        return None

    def _on_send_clicked(self):
        user_text = self.input_text.get("1.0", "end-1c").strip()
        if not user_text:
            return
        # clear input
        self.input_text.delete("1.0", "end")
        # show user message immediately
        self.post_user_message(user_text)
        # show typing, then call backend shortly after so typing shows up
        self._start_typing()
        self.root.after(FAST_REPLY_DELAY_MS, lambda: self._call_backend(user_text))

    def _quick_send(self, text):
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", text)
        self._on_send_clicked()

    def _call_backend(self, user_text):
        try:
            reply = handle_query(user_text)
            if not reply:
                reply = "I couldn't find a direct answer — escalating to a human specialist."
        except Exception as e:
            reply = f"Backend error: {e}"

        # replace typing bubble with actual bot message
        self._stop_typing()
        self.post_bot_message(reply)

    # -----------------------
    # scrolling helpers
    # -----------------------
    def _maybe_scroll_to_bottom(self):
        # small delay for layout to update then scroll
        self.root.after(20, lambda: self.canvas.yview_moveto(1.0))

    # -----------------------
    # utilities
    # -----------------------
    def clear_chat(self):
        for w in self.messages_frame.winfo_children():
            w.destroy()
        self.msg_count = 0
        self.post_bot_message("Chat cleared! How can I help you today?")

    def _toggle_theme(self):
        cur = ctk.get_appearance_mode()
        if cur == "Dark":
            ctk.set_appearance_mode("Light")
            self.theme_btn.configure(text="☀️ Light")
        else:
            ctk.set_appearance_mode("Dark")
            self.theme_btn.configure(text="🌙 Dark")

    def _show_about(self):
        top = ctk.CTkToplevel(self.root)
        top.title("About — Support Chatbot")
        top.geometry("420x260")
        top.transient(self.root)
        top.grab_set()
        f = ctk.CTkFrame(top, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=12, pady=12)
        ctk.CTkLabel(f, text="Support Chatbot", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(6,8))
        ctk.CTkLabel(f, text="Version 1.0\nPowered by pyDatalog logic and a regex+spaCy NLU.", justify="center").pack(pady=(6,8))
        ctk.CTkButton(f, text="Close", width=120, command=top.destroy).pack(pady=8)

    def run(self):
        self.root.mainloop()

# -----------------------
# Run
# -----------------------
if __name__ == "__main__":
    app = ChatBotGUI()
    app.run()
