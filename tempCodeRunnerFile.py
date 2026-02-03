# Updated Chatbot GUI (fixed: guaranteed fast replies & robust backend handling)
# Keeps backend unchanged: imports handle_query from chatbot.py
# Place this file alongside chatbot.py, logic_layer.py, nlu.py

import customtkinter as ctk
from datetime import datetime
from chatbot import handle_query
import tkinter as tk

# Appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Color palette (compatible with Tk)
BG = "#2B0230"          # deep violet background
PANEL = "#3B0A3B"       # slightly lighter panel
ACCENT = "#D07BD0"      # pink/purple accent
BUBBLE_USER = "#673AB7" # user bubble (purple)
BUBBLE_BOT = "#F6EAF9"  # bot bubble (light)
TEXT_LIGHT = "white"
TEXT_DARK = "#222222"
TYPING_DOT = "#E6C1E6"

ANIM_STEP_MS = 12  # animation timer step


class ChatBotGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Support Chatbot — Customer Support")
        self.root.geometry("1200x760")
        self.root.minsize(920, 620)

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_header()
        self._build_chat_area()
        self._build_input_bar()
        self._init_state()

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------
    def _build_header(self):
        header = ctk.CTkFrame(self.root, height=90, fg_color=PANEL, corner_radius=12)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(12, 6))
        header.grid_columnconfigure(0, weight=1)

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=18, pady=12)

        title_label = ctk.CTkLabel(title_frame, text="Customer Support",
                                   font=ctk.CTkFont(size=26, weight="bold"),
                                   text_color=TEXT_LIGHT)
        title_label.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            title_frame,
            text="Intelligent support assistant — billing, orders, account help & more",
            font=ctk.CTkFont(size=12),
            text_color="#E8D2E8"
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(4, 0))

        ctrl_frame = ctk.CTkFrame(header, fg_color="transparent")
        ctrl_frame.grid(row=0, column=1, sticky="e", padx=18)

        self.theme_btn = ctk.CTkButton(ctrl_frame, text="🌙 Dark", width=120,
                                       command=self._toggle_theme)
        self.theme_btn.grid(row=0, column=0, padx=(0, 8))

        clear_btn = ctk.CTkButton(ctrl_frame, text="Clear Chat", fg_color="#E04E50",
                                  width=110, command=self.clear_chat)
        clear_btn.grid(row=0, column=1, padx=(0, 8))

        about_btn = ctk.CTkButton(ctrl_frame, text="ℹ️ About", width=110,
                                  command=self._show_about)
        about_btn.grid(row=0, column=2)

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.root, width=300, fg_color=PANEL, corner_radius=12)
        self.sidebar.grid(row=1, column=0, sticky="nsw", padx=(16, 8), pady=(6, 16))
        self.sidebar.grid_rowconfigure(2, weight=1)

        avatar_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        avatar_frame.grid(row=0, column=0, padx=12, pady=12, sticky="w")

        self.avatar_label = ctk.CTkLabel(avatar_frame, text="🤖",
                                         font=ctk.CTkFont(size=28))
        self.avatar_label.grid(row=0, column=0, sticky="w")

        name_label = ctk.CTkLabel(avatar_frame, text="Support Bot",
                                  font=ctk.CTkFont(size=18, weight="bold"))
        name_label.grid(row=0, column=1, padx=(8, 0))

        desc = (
            "Hi! I'm your virtual assistant. I can help with billing, orders, account security, "
            "password resets, refunds, integrations, and more. Use the chat to ask anything."
        )

        desc_label = ctk.CTkLabel(self.sidebar, text=desc, wraplength=240,
                                  justify="left", text_color="#EAD7EA")
        desc_label.grid(row=1, column=0, padx=12, pady=(6, 12), sticky="w")

        cap_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        cap_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=(6, 12))

        cap_title = ctk.CTkLabel(cap_frame, text="I can assist with:",
                                 font=ctk.CTkFont(size=14, weight="bold"))
        cap_title.pack(anchor="w", pady=(0, 6))

        caps = [
            "Billing & Invoices",
            "Refunds & Disputes",
            "Order tracking",
            "Password & Login help",
            "App crashes & Bug reports",
            "Account security & 2FA",
            "Data export requests",
            "Subscription changes",
            "Feature requests & Integrations"
        ]

        for item in caps:
            lbl = ctk.CTkLabel(cap_frame, text="•  " + item,
                               anchor="w", justify="left")
            lbl.pack(fill="x", pady=2)

        self.sidebar_toggle = ctk.CTkButton(self.sidebar, text="Hide",
                                            command=self._toggle_sidebar, width=80)
        self.sidebar_toggle.grid(row=3, column=0, pady=8, padx=12, sticky="w")

    # --------------------------------------------------------
    # CHAT AREA
    # --------------------------------------------------------
    def _build_chat_area(self):
        container = ctk.CTkFrame(self.root, fg_color=BG, corner_radius=12)
        container.grid(row=1, column=1, sticky="nsew",
                       padx=(8, 16), pady=(6, 16))
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.chat_frame = ctk.CTkScrollableFrame(
            container, fg_color=BG, corner_radius=0)
        self.chat_frame.grid(row=0, column=0, sticky="nsew",
                             padx=12, pady=12)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        intro = ctk.CTkFrame(self.chat_frame, fg_color=PANEL, corner_radius=12)
        intro.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        intro.grid_columnconfigure(1, weight=1)

        avatar = ctk.CTkLabel(intro, text="🤖", font=ctk.CTkFont(size=28))
        avatar.grid(row=0, column=0, padx=12, pady=12, sticky="n")

        intro_text = (
            "Hello! 👋 I am your support assistant. "
            "You can ask me about billing, orders, password resets, app issues, subscriptions, "
            "integrations, and more. I'll try to handle your request, but if I'm unsure "
            "I'll escalate to a human specialist."
        )

        intro_label = ctk.CTkLabel(intro, text=intro_text,
                                   wraplength=760, justify="left")
        intro_label.grid(row=0, column=1,
                         padx=(4, 12), pady=10, sticky="w")

        sep = ctk.CTkFrame(self.chat_frame, height=2, fg_color="#2F152F")
        sep.grid(row=1, column=0, sticky="ew", pady=(8, 10))

        self.messages_container = ctk.CTkFrame(self.chat_frame,
                                               fg_color="transparent")
        self.messages_container.grid(row=2, column=0, sticky="nsew")
        self.messages_container.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(container, text="Ready to help!",
                                         text_color="#CDB3CD")
        self.status_label.grid(row=1, column=0,
                               sticky="w", padx=18, pady=(4, 12))

    # --------------------------------------------------------
    # INPUT BAR
    # --------------------------------------------------------
    def _build_input_bar(self):
        footer = ctk.CTkFrame(self.root, height=110,
                              fg_color=PANEL, corner_radius=12)
        footer.grid(row=2, column=0, columnspan=2,
                    sticky="ew", padx=16, pady=(0, 16))
        footer.grid_columnconfigure(0, weight=1)

        self.input_text = ctk.CTkTextbox(
            footer, height=76, wrap="word", font=ctk.CTkFont(size=14))
        self.input_text.grid(row=0, column=0, padx=(16, 6),
                             pady=12, sticky="ew")
        self.input_text.bind("<Return>", self._on_return_pressed)
        self.input_text.bind("<Shift-Return>", lambda e: None)

        send_frame = ctk.CTkFrame(footer, fg_color="transparent")
        send_frame.grid(row=0, column=1, padx=(6, 16), pady=12)

        self.send_btn = ctk.CTkButton(send_frame, text="Send", width=120,
                                      height=56, fg_color="#5CF49B",
                                      command=self._on_send_click)
        self.send_btn.pack()

        qbtn_frame = ctk.CTkFrame(footer, fg_color="transparent")
        qbtn_frame.grid(row=1, column=0, columnspan=2,
                        padx=16, pady=(0, 12), sticky="ew")

        tips = ["Where is my order?", "Refund status",
                "Reset my password", "Cancel subscription"]

        for t in tips:
            b = ctk.CTkButton(qbtn_frame, text=t, width=160,
                              fg_color="#642A64",
                              command=lambda txt=t: self._quick_send(txt))
            b.pack(side="left", padx=8)

    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------
    def _init_state(self):
        self.sidebar_visible = True
        self.typing_anim_running = False
        self.typing_widget = None
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        self.input_text.focus()
        self.root.after(200, lambda: self._post_bot_message(
            "Hello! Ask me anything about billing, orders, account issues or technical problems."
        ))

    # --------------------------------------------------------
    # ACTIONS
    # --------------------------------------------------------
    def _toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.grid_remove()
            self.sidebar_visible = False
            self.sidebar_toggle.configure(text="Show")
        else:
            self.sidebar.grid()
            self.sidebar_visible = True
            self.sidebar_toggle.configure(text="Hide")

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("Light")
            self.theme_btn.configure(text="☀️ Light")
        else:
            ctk.set_appearance_mode("Dark")
            self.theme_btn.configure(text="🌙 Dark")

    # --------------------------------------------------------
    # FIXED ABOUT WINDOW (line 239 error was here)
    # --------------------------------------------------------
    def _show_about(self):
        about = ctk.CTkToplevel(self.root)
        about.title("About — Support Chatbot")
        about.geometry("480x320")
        about.transient(self.root)
        about.grab_set()

        frame = ctk.CTkFrame(about, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(frame, text="Support Chatbot",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(6, 8))

        ctk.CTkLabel(
            frame,
            text="Version 1.0\nPowered by pyDatalog logic and a regex+spaCy NLU.",
            justify="center"
        ).pack(pady=(4, 12))

        ctk.CTkLabel(
            frame,
            text="If I cannot handle your request, I will escalate it to a human specialist.",
            wraplength=420
        ).pack(pady=(6, 10))

        ctk.CTkButton(frame, text="Close", command=about.destroy,
                      width=120).pack(pady=14)

    # --------------------------------------------------------
    # INPUT EVENTS
    # --------------------------------------------------------
    def _quick_send(self, text):
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", text)
        self._on_send_click()

    def _on_return_pressed(self, event):
        if not event.state & 0x1:
            self._on_send_click()
            return "break"
        return None

    def _on_send_click(self):
        user_text = self.input_text.get("1.0", "end-1c").strip()
        if not user_text:
            return

        self.input_text.delete("1.0", "end")
        self._post_user_message(user_text)

        self._start_typing_animation()
        self.root.after(10, lambda: self._call_backend(user_text))

    # --------------------------------------------------------
    # MESSAGE RENDERING
    # --------------------------------------------------------
    def _post_user_message(self, message):
        bubble = ctk.CTkFrame(self.messages_container,
                              fg_color=BUBBLE_USER, corner_radius=14)
        bubble.grid(sticky="e", padx=(40, 8), pady=8)
        bubble.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(bubble, text=message, wraplength=520,
                           justify="left",
                           font=ctk.CTkFont(size=14), text_color=TEXT_LIGHT)
        lbl.grid(row=0, column=0, padx=12, pady=(10, 8))

        time_lbl = ctk.CTkLabel(bubble, text=datetime.now().strftime("%H:%M"),
                                text_color="#E9D6F0",
                                font=ctk.CTkFont(size=9))
        time_lbl.grid(row=1, column=0, sticky="e", padx=10, pady=(0, 8))

        self._scroll_to_bottom()

    def _post_bot_message(self, message):
        wrapper = tk.Frame(self.messages_container.master,
                           bg=self.messages_container.master["bg"])
        wrapper.pack(fill="x", pady=8)

        bubble = ctk.CTkFrame(wrapper, fg_color=BUBBLE_BOT, corner_radius=14)
        bubble.place(x=-1000, y=0)

        lbl = ctk.CTkLabel(bubble, text=message, wraplength=520, justify="left",
                           font=ctk.CTkFont(size=14), text_color=TEXT_DARK)
        lbl.pack(padx=12, pady=(12, 10))

        time_lbl = ctk.CTkLabel(bubble, text=datetime.now().strftime("%H:%M"),
                                text_color="#7B6B7B",
                                font=ctk.CTkFont(size=9))
        time_lbl.pack(anchor="e", padx=10, pady=(0, 8))

        wrapper.update_idletasks()

        target_x = 8
        start_x = -bubble.winfo_reqwidth() - 40

        bubble.place(x=start_x, y=0)
        self._animate_slide(bubble, start_x, target_x, duration=240)
        self._scroll_to_bottom()

    def _animate_slide(self, widget, start_x, end_x, duration=300):
        total_steps = max(int(duration / ANIM_STEP_MS), 4)
        dx = (end_x - start_x) / total_steps
        current_step = 0

        def step():
            nonlocal current_step
            current_step += 1
            x = start_x + dx * current_step
            widget.place(x=int(x))

            if current_step < total_steps:
                self.root.after(ANIM_STEP_MS, step)
            else:
                widget.place(x=end_x)

        step()

    def _scroll_to_bottom(self):
        self.root.after(40, lambda: self.chat_frame.master_canvas.yview_moveto(1.0))

    # --------------------------------------------------------
    # TYPING ANIMATION
    # --------------------------------------------------------
    def _start_typing_animation(self):
        if self.typing_anim_running:
            return

        self.typing_anim_running = True
        self.status_label.configure(text="Support Bot is typing...")

        self.typing_wrapper = tk.Frame(self.messages_container.master,
                                       bg=self.messages_container.master["bg"])
        self.typing_wrapper.pack(fill="x", pady=6)

        self.typing_bubble = ctk.CTkFrame(self.typing_wrapper,
                                          fg_color=BUBBLE_BOT,
                                          corner_radius=14)
        self.typing_bubble.place(x=8, y=0)

        self.dot_labels = [
            ctk.CTkLabel(self.typing_bubble, text="●",
                         font=ctk.CTkFont(size=14), text_color=TYPING_DOT)
            for _ in range(3)
        ]

        for i, d in enumerate(self.dot_labels):
            d.pack(side="left", padx=(8 if i == 0 else 6, 6), pady=10)

        self._typing_dot_state = 0
        self._typing_anim_step()
        self._scroll_to_bottom()

    def _typing_anim_step(self):
        if not self.typing_anim_running:
            return

        state = self._typing_dot_state % 6
        for i, d in enumerate(self.dot_labels):
            if i == (state // 2):
                d.configure(text_color=ACCENT)
            else:
                d.configure(text_color=TYPING_DOT)

        self._typing_dot_state += 1
        self.root.after(140, self._typing_anim_step)

    def _stop_typing_animation(self):
        if not self.typing_anim_running:
            return

        self.typing_anim_running = False
        self.status_label.configure(text="Ready to help!")

        try:
            self.typing_wrapper.destroy()
        except Exception:
            pass

    # --------------------------------------------------------
    # BACKEND CALL
    # --------------------------------------------------------
    def _call_backend(self, user_text):
        try:
            response_text = handle_query(user_text)
            if not response_text:
                response_text = (
                    "I'm here but couldn't find a direct answer. "
                    "I'll escalate this to a human specialist."
                )
        except Exception as e:
            response_text = f"Backend error: {e}"

        self._stop_typing_animation()
        self._post_bot_message(response_text)

    # --------------------------------------------------------
    # UTIL
    # --------------------------------------------------------
    def clear_chat(self):
        for w in self.messages_container.winfo_children():
            w.destroy()

        self._post_bot_message("Chat cleared! How can I help you today?")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ChatBotGUI()
    app.run()
