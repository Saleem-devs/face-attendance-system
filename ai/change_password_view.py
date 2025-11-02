import tkinter as tk
from tkinter import messagebox
from auth import change_password
from theme import *


class ChangePasswordView:
    def __init__(self, parent, username):
        self.parent = parent
        self.username = username
        self.result = False

    def show(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Change Password")
        dialog.geometry("550x600")
        dialog.config(bg=BG_PRIMARY)
        dialog.resizable(True, True)
        dialog.minsize(550, 600)
        dialog.transient(self.parent)
        dialog.grab_set()

        dialog.update_idletasks()
        width = 550
        height = 600
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        main_container = tk.Frame(dialog, bg=BG_PRIMARY)
        main_container.pack(expand=True, fill="both", padx=50, pady=40)

        header_frame = tk.Frame(main_container, bg=BG_PRIMARY)
        header_frame.pack(fill="x", pady=(0, 30))

        title = tk.Label(
            header_frame,
            text="Change Password",
            font=FONT_HEADING,
            bg=BG_PRIMARY,
            fg=TEXT_PRIMARY,
        )
        title.pack()

        subtitle = tk.Label(
            header_frame,
            text=f"Changing password for: {self.username}",
            font=FONT_SUBTITLE,
            bg=BG_PRIMARY,
            fg=TEXT_MUTED,
        )
        subtitle.pack(pady=(10, 0))

        form_frame = tk.Frame(main_container, bg=BG_SECONDARY, relief="flat", bd=0)
        form_frame.pack(expand=True, fill="both")

        inner_form = tk.Frame(form_frame, bg=BG_SECONDARY)
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

        current_password_label = tk.Label(
            inner_form,
            text="Current Password *",
            font=FONT_LABEL,
            bg=BG_SECONDARY,
            fg=TEXT_SECONDARY,
            anchor="w",
        )
        current_password_label.pack(fill="x", pady=(0, 8))

        current_password_frame = tk.Frame(inner_form, bg=BG_SECONDARY)
        current_password_frame.pack(fill="x", pady=(0, 20))

        current_password_entry = tk.Entry(
            current_password_frame, show="*", **entry_style
        )
        current_password_entry.pack(side="left", fill="x", expand=True, ipady=10)

        current_password_show_var = tk.BooleanVar()
        current_password_show_btn = tk.Label(
            current_password_frame,
            text="Show",
            font=FONT_STATUS,
            bg=BG_SECONDARY,
            fg=ACCENT_BLUE,
            cursor="hand2",
            padx=10,
        )

        def toggle_current_password(event=None):
            if current_password_show_var.get():
                current_password_entry.config(show="")
                current_password_show_btn.config(text="Hide")
            else:
                current_password_entry.config(show="*")
                current_password_show_btn.config(text="Show")

        current_password_show_var.trace("w", lambda *args: toggle_current_password())
        current_password_show_btn.bind(
            "<Button-1>",
            lambda e: current_password_show_var.set(
                not current_password_show_var.get()
            ),
        )
        current_password_show_btn.pack(side="right", padx=(10, 0))

        new_password_label = tk.Label(
            inner_form,
            text="New Password *",
            font=FONT_LABEL,
            bg=BG_SECONDARY,
            fg=TEXT_SECONDARY,
            anchor="w",
        )
        new_password_label.pack(fill="x", pady=(0, 8))

        new_password_frame = tk.Frame(inner_form, bg=BG_SECONDARY)
        new_password_frame.pack(fill="x", pady=(0, 20))

        new_password_entry = tk.Entry(new_password_frame, show="*", **entry_style)
        new_password_entry.pack(side="left", fill="x", expand=True, ipady=10)

        new_password_show_var = tk.BooleanVar()
        new_password_show_btn = tk.Label(
            new_password_frame,
            text="Show",
            font=FONT_STATUS,
            bg=BG_SECONDARY,
            fg=ACCENT_BLUE,
            cursor="hand2",
            padx=10,
        )

        def toggle_new_password(event=None):
            if new_password_show_var.get():
                new_password_entry.config(show="")
                new_password_show_btn.config(text="Hide")
            else:
                new_password_entry.config(show="*")
                new_password_show_btn.config(text="Show")

        new_password_show_var.trace("w", lambda *args: toggle_new_password())
        new_password_show_btn.bind(
            "<Button-1>",
            lambda e: new_password_show_var.set(not new_password_show_var.get()),
        )
        new_password_show_btn.pack(side="right", padx=(10, 0))

        confirm_password_label = tk.Label(
            inner_form,
            text="Confirm New Password *",
            font=FONT_LABEL,
            bg=BG_SECONDARY,
            fg=TEXT_SECONDARY,
            anchor="w",
        )
        confirm_password_label.pack(fill="x", pady=(0, 8))

        confirm_password_frame = tk.Frame(inner_form, bg=BG_SECONDARY)
        confirm_password_frame.pack(fill="x", pady=(0, 30))

        confirm_password_entry = tk.Entry(
            confirm_password_frame, show="*", **entry_style
        )
        confirm_password_entry.pack(side="left", fill="x", expand=True, ipady=10)

        confirm_password_show_var = tk.BooleanVar()
        confirm_password_show_btn = tk.Label(
            confirm_password_frame,
            text="Show",
            font=FONT_STATUS,
            bg=BG_SECONDARY,
            fg=ACCENT_BLUE,
            cursor="hand2",
            padx=10,
        )

        def toggle_confirm_password(event=None):
            if confirm_password_show_var.get():
                confirm_password_entry.config(show="")
                confirm_password_show_btn.config(text="Hide")
            else:
                confirm_password_entry.config(show="*")
                confirm_password_show_btn.config(text="Show")

        confirm_password_show_var.trace("w", lambda *args: toggle_confirm_password())
        confirm_password_show_btn.bind(
            "<Button-1>",
            lambda e: confirm_password_show_var.set(
                not confirm_password_show_var.get()
            ),
        )
        confirm_password_show_btn.pack(side="right", padx=(10, 0))

        status_label = tk.Label(
            inner_form,
            text="",
            font=FONT_STATUS,
            bg=BG_SECONDARY,
            fg=TEXT_MUTED,
            wraplength=400,
            justify="center",
        )
        status_label.pack(pady=(0, 15))

        def on_change_password():
            current = current_password_entry.get().strip()
            new = new_password_entry.get().strip()
            confirm = confirm_password_entry.get().strip()

            if not current or not new or not confirm:
                status_label.config(text="Please fill in all fields", fg=ERROR_COLOR)
                return

            if new != confirm:
                status_label.config(text="New passwords do not match", fg=ERROR_COLOR)
                return

            if len(new) < 6:
                status_label.config(
                    text="New password must be at least 6 characters", fg=ERROR_COLOR
                )
                return

            status_label.config(text="Changing password...", fg=ACCENT_BLUE)
            dialog.update()

            success, message = change_password(self.username, current, new)

            if success:
                status_label.config(text=message, fg=SUCCESS_COLOR)
                messagebox.showinfo("Success", message)
                self.result = True
                dialog.after(500, dialog.destroy)
            else:
                status_label.config(text=message, fg=ERROR_COLOR)

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

        change_btn = create_button(
            inner_form, "Change Password", on_change_password, ACCENT_BLUE
        )
        change_btn.pack(pady=(10, 0))

        def on_cancel():
            dialog.destroy()

        cancel_btn = create_button(inner_form, "Cancel", on_cancel, TEXT_MUTED)
        cancel_btn.pack(pady=(15, 0))

        def on_enter_key(event):
            on_change_password()

        current_password_entry.bind("<Return>", on_enter_key)
        new_password_entry.bind("<Return>", on_enter_key)
        confirm_password_entry.bind("<Return>", on_enter_key)

        current_password_entry.focus()

        dialog.wait_window()
        return self.result
