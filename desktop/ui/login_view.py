import tkinter as tk
from tkinter import messagebox
from services.auth import authenticate
from ui.theme import *


class LoginView:
    def __init__(self, on_success_callback):
        self.on_success = on_success_callback
        self.root = None
        self.is_authenticated = False
        self.username = None

    def show(self):
        self.root = tk.Tk()
        self.root.title("Login - Face Attendance System")
        self.root.config(bg=BG_PRIMARY)
        self.root.resizable(True, True)
        self.root.minsize(500, 550)

        self.root.update_idletasks()

        main_container = tk.Frame(self.root, bg=BG_PRIMARY)
        main_container.pack(expand=True, fill="both", padx=50, pady=50)

        header_frame = tk.Frame(main_container, bg=BG_PRIMARY)
        header_frame.pack(fill="x", pady=(0, 40))

        title = tk.Label(
            header_frame,
            text="Face Attendance System",
            font=FONT_TITLE,
            bg=BG_PRIMARY,
            fg=TEXT_PRIMARY,
        )
        title.pack()

        subtitle = tk.Label(
            header_frame,
            text="Admin Login Required",
            font=FONT_SUBTITLE,
            bg=BG_PRIMARY,
            fg=TEXT_MUTED,
        )
        subtitle.pack(pady=(15, 0))

        login_frame = tk.Frame(main_container, bg=BG_SECONDARY, relief="flat", bd=0)
        login_frame.pack(expand=True, fill="both")

        inner_form = tk.Frame(login_frame, bg=BG_SECONDARY)
        inner_form.pack(expand=True, fill="both", padx=40, pady=40)

        entry_style = {
            "font": FONT_INPUT,
            "bg": BG_PRIMARY,
            "fg": TEXT_PRIMARY,
            "insertbackground": ACCENT_BLUE,
            "relief": "flat",
            "bd": 0,
            "highlightthickness": 1,
            "highlightbackground": BORDER_COLOR,
            "highlightcolor": ACCENT_BLUE,
        }

        username_label = tk.Label(
            inner_form,
            text="Username",
            font=FONT_LABEL,
            bg=BG_SECONDARY,
            fg=TEXT_SECONDARY,
            anchor="w",
        )
        username_label.pack(fill="x", pady=(0, 8))

        username_entry = tk.Entry(inner_form, **entry_style)
        username_entry.pack(fill="x", pady=(0, 20), ipady=10)

        password_label = tk.Label(
            inner_form,
            text="Password",
            font=FONT_LABEL,
            bg=BG_SECONDARY,
            fg=TEXT_SECONDARY,
            anchor="w",
        )
        password_label.pack(fill="x", pady=(0, 8))

        password_entry = tk.Entry(inner_form, show="*", **entry_style)
        password_entry.pack(fill="x", pady=(0, 30), ipady=10)

        status_label = tk.Label(
            inner_form,
            text="",
            font=FONT_STATUS,
            bg=BG_SECONDARY,
            fg=ERROR_COLOR,
            wraplength=300,
            justify="center",
        )
        status_label.pack(pady=(0, 15))

        def on_login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if not username or not password:
                status_label.config(
                    text="Please enter both username and password", fg=ERROR_COLOR
                )
                return

            status_label.config(text="Authenticating...", fg=ACCENT_BLUE)
            self.root.update()

            success, role = authenticate(username, password)

            if success:
                self.is_authenticated = True
                self.username = username
                status_label.config(text="Login successful!", fg=SUCCESS_COLOR)
                self.root.after(500, self.close)
            else:
                status_label.config(text="Invalid username or password", fg=ERROR_COLOR)
                password_entry.delete(0, tk.END)

        def create_button(parent, text, command, color=ACCENT_BLUE):
            btn_frame = tk.Frame(
                parent,
                bg=color,
                relief="flat",
                bd=0,
                cursor="hand2",
            )

            btn_label = tk.Label(
                btn_frame,
                text=text,
                font=FONT_BUTTON_LARGE,
                bg=color,
                fg="#FFFFFF",
                padx=30,
                pady=16,
                cursor="hand2",
            )
            btn_label.pack()

            def on_click(event):
                command()

            def on_enter(event):
                darker = (
                    ACCENT_BLUE_HOVER if color == ACCENT_BLUE else ACCENT_GREEN_HOVER
                )
                btn_frame.config(bg=darker)
                btn_label.config(bg=darker)

            def on_leave(event):
                btn_frame.config(bg=color)
                btn_label.config(bg=color)

            btn_frame.bind("<Button-1>", on_click)
            btn_label.bind("<Button-1>", on_click)
            btn_frame.bind("<Enter>", on_enter)
            btn_frame.bind("<Leave>", on_leave)
            btn_label.bind("<Enter>", on_enter)
            btn_label.bind("<Leave>", on_leave)

            return btn_frame

        login_btn = create_button(inner_form, "Login", on_login, ACCENT_BLUE)
        login_btn.pack(pady=(10, 0))

        def on_enter_key(event):
            on_login()

        username_entry.bind("<Return>", on_enter_key)
        password_entry.bind("<Return>", on_enter_key)

        username_entry.focus()

        default_info = tk.Label(
            inner_form,
            text="Default: admin / admin123",
            font=FONT_STATUS,
            bg=BG_SECONDARY,
            fg=TEXT_MUTED,
        )
        default_info.pack(pady=(20, 0))

        self.root.mainloop()

        return self.is_authenticated

    def close(self):
        if self.root:
            self.root.destroy()
