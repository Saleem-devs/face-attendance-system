import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
import webbrowser
from ui.theme import *
from ui.login_view import LoginView
from ui.change_password_view import ChangePasswordView
from services.backend_manager import BackendManager

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
    DESKTOP_DIR = os.path.join(BASE_DIR, "desktop")
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DESKTOP_DIR = os.path.dirname(os.path.abspath(__file__))

ICON_PATH = os.path.join(DESKTOP_DIR, "assets", "app_icon.png")

logged_in_username = None
backend_manager = BackendManager()


def run_register():
    try:
        from core.registration import create_gui

        create_gui(root)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start registration:\n{e}")


def run_attendance():
    try:
        from core.attendance import create_gui

        create_gui(root)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start attendance: \n{e}")


def open_dashboard():
    if not backend_manager.open_dashboard():
        messagebox.showerror(
            "Error",
            "Failed to start web dashboard. Please check if port 8000 is available.",
        )


def open_change_password():
    change_password_view = ChangePasswordView(root, logged_in_username)
    change_password_view.show()


def on_closing():
    backend_manager.stop()
    root.destroy()


login = LoginView(None)
if not login.show():
    sys.exit()

logged_in_username = login.username

root = tk.Tk()
root.title("Face Attendance System")
root.config(bg=BG_PRIMARY)
root.protocol("WM_DELETE_WINDOW", on_closing)

if os.path.exists(ICON_PATH):
    icon = tk.PhotoImage(file=ICON_PATH)
    root.iconphoto(False, icon)


main_container = tk.Frame(root, bg=BG_PRIMARY)
main_container.pack(expand=True, fill="both", padx=40, pady=40)

header_frame = tk.Frame(main_container, bg=BG_PRIMARY)
header_frame.pack(fill="x", pady=(0, 50))

title_container = tk.Frame(header_frame, bg=BG_PRIMARY)
title_container.pack()


title = tk.Label(
    title_container,
    text="Face Attendance System",
    font=FONT_TITLE,
    bg=BG_PRIMARY,
    fg=TEXT_PRIMARY,
)
title.pack(side="left")

subtitle = tk.Label(
    header_frame,
    text="AI-Powered Smart Attendance Tracking",
    font=FONT_SUBTITLE,
    bg=BG_PRIMARY,
    fg=TEXT_MUTED,
)
subtitle.pack(pady=(15, 0))

cards_container = tk.Frame(main_container, bg=BG_PRIMARY)
cards_container.pack(expand=True, fill="both")


def create_feature_card(
    parent, icon, title_text, description, button_text, command, accent_color
):
    card = tk.Frame(
        parent,
        bg=BG_SECONDARY,
        relief="flat",
        bd=0,
    )
    card.pack(side="left", expand=True, fill="both", padx=15)

    inner = tk.Frame(card, bg=BG_SECONDARY)
    inner.pack(expand=True, fill="both", padx=30, pady=30)

    icon_label = tk.Label(
        inner,
        text=icon,
        font=("Helvetica", 50),
        bg=BG_SECONDARY,
        fg=accent_color,
    )
    icon_label.pack(pady=(0, 20))

    card_title = tk.Label(
        inner,
        text=title_text,
        font=("Helvetica", 20, "bold"),
        bg=BG_SECONDARY,
        fg=TEXT_PRIMARY,
    )
    card_title.pack(pady=(0, 10))

    desc = tk.Label(
        inner,
        text=description,
        font=("Helvetica", 11),
        bg=BG_SECONDARY,
        fg=TEXT_SECONDARY,
        wraplength=280,
        justify="center",
    )
    desc.pack(pady=(0, 25))

    def create_action_button(parent_frame, text, cmd, color):
        btn_frame = tk.Frame(
            parent_frame,
            bg=color,
            relief="flat",
            bd=0,
            cursor="hand2",
        )

        btn_label = tk.Label(
            btn_frame,
            text=text,
            font=FONT_BUTTON,
            bg=color,
            fg="#FFFFFF",
            padx=25,
            pady=14,
            cursor="hand2",
        )
        btn_label.pack()

        def on_click(event):
            cmd()

        def on_enter(event):
            darker = ACCENT_BLUE_HOVER if color == ACCENT_BLUE else ACCENT_GREEN_HOVER
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

    button = create_action_button(inner, button_text, command, accent_color)
    button.pack()

    return card


register_card = create_feature_card(
    cards_container,
    "+",
    "Register Student",
    "Add new students to the system by capturing their facial features.",
    "Register New",
    run_register,
    ACCENT_BLUE,
)

attendance_card = create_feature_card(
    cards_container,
    "O",
    "Mark Attendance",
    "Start the attendance session to automatically detect and record student presence using face recognition.",
    "Start Session",
    run_attendance,
    ACCENT_GREEN,
)

dashboard_card = create_feature_card(
    cards_container,
    "◐",
    "Web Dashboard",
    "Open the web dashboard to view attendance reports, manage students, and export data.",
    "Open Web Dashboard",
    open_dashboard,
    ACCENT_BLUE,
)

footer_frame = tk.Frame(root, bg=BG_PRIMARY)
footer_frame.pack(side="bottom", fill="x", pady=(0, 20))

footer_content = tk.Frame(footer_frame, bg=BG_PRIMARY)
footer_content.pack()

footer_left = tk.Frame(footer_content, bg=BG_PRIMARY)
footer_left.pack(side="left", padx=20)

footer_right = tk.Frame(footer_content, bg=BG_PRIMARY)
footer_right.pack(side="right", padx=20)


def open_github(event):
    webbrowser.open("https://github.com/Saleem-devs")


def open_change_password_link(event):
    open_change_password()


footer_text_1 = tk.Label(
    footer_left,
    text="Developed by",
    font=FONT_FOOTER,
    bg=BG_PRIMARY,
    fg=TEXT_FOOTER,
)
footer_text_1.pack(side="left")

seleem_link = tk.Label(
    footer_left,
    text="Seleem",
    font=(FONT_FOOTER[0], FONT_FOOTER[1], "underline"),
    bg=BG_PRIMARY,
    fg=ACCENT_BLUE,
    cursor="hand2",
)
seleem_link.pack(side="left")
seleem_link.bind("<Button-1>", open_github)
seleem_link.bind("<Enter>", lambda e: seleem_link.config(fg="#93C5FD"))
seleem_link.bind("<Leave>", lambda e: seleem_link.config(fg=ACCENT_BLUE))

change_password_link = tk.Label(
    footer_right,
    text="Change Password",
    font=(FONT_FOOTER[0], FONT_FOOTER[1], "underline"),
    bg=BG_PRIMARY,
    fg=ACCENT_BLUE,
    cursor="hand2",
)
change_password_link.pack(side="left")
change_password_link.bind("<Button-1>", open_change_password_link)
change_password_link.bind(
    "<Enter>", lambda e: change_password_link.config(fg="#93C5FD")
)
change_password_link.bind(
    "<Leave>", lambda e: change_password_link.config(fg=ACCENT_BLUE)
)


root.mainloop()
