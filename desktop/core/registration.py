import cv2
import face_recognition
import numpy as np
import sqlite3
import os
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.theme import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_DIR = os.path.join(BASE_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "attendance.db")
PHOTOS_DIR = os.path.join(BASE_DIR, "data", "photos")
ENCODINGS_DIR = os.path.join(BASE_DIR, "data", "encodings")
SAMPLES_PER_STUDENT = 5
DETECTION_MODEL = "hog"

Path(DB_DIR).mkdir(parents=True, exist_ok=True)
Path(PHOTOS_DIR).mkdir(parents=True, exist_ok=True)
Path(ENCODINGS_DIR).mkdir(parents=True, exist_ok=True)


def init_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_id TEXT UNIQUE NOT NULL,
            email TEXT,
            photo_path TEXT,
            encoding_path TEXT,
            date_registered TEXT NOT NULL
        );
    """
    )
    conn.commit()
    conn.close()


def student_exists(student_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM students WHERE student_id = ?", (student_id,))
    row = cur.fetchone()
    conn.close()
    return row is not None


def choose_camera_index() -> int:
    for idx in [0, 1, 2]:
        cap = cv2.VideoCapture(idx, cv2.CAP_AVFOUNDATION)
        if cap.isOpened():
            for _ in range(10):
                cap.read()
            ok, frame = cap.read()
            cap.release()
            if ok and frame is not None and frame.size > 0:
                return idx
    return -1


def capture_face_samples(camera_index: int, name: str, student_id: str):
    cap = cv2.VideoCapture(camera_index, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        print("Could not open camera")
        return None, None

    collected_encs = []
    last_good_frame = None

    print("\n================= FACE CAPTURE =================")
    print("• Look at the camera with good lighting")
    print("• Press SPACE to capture a sample")
    print("• Need:", SAMPLES_PER_STUDENT, "samples (slight head turns help)")
    print("• Press ESC to cancel")
    print("================================================\n")

    while True:
        ok, frame_bgr = cap.read()
        if not ok or frame_bgr is None:
            print("Failed to read from camera")
            break

        frame_bgr = cv2.flip(frame_bgr, 1)
        h, w = frame_bgr.shape[:2]

        cv2.putText(
            frame_bgr,
            f"Samples: {len(collected_encs)}/{SAMPLES_PER_STUDENT}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 200, 255),
            2,
        )

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(frame_rgb, model=DETECTION_MODEL)

        for top, right, bottom, left in boxes:
            color = (0, 255, 0) if len(boxes) == 1 else (0, 165, 255)
            cv2.rectangle(frame_bgr, (left, top), (right, bottom), color, 2)

        if len(boxes) == 0:
            cv2.putText(
                frame_bgr,
                "No face detected",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )
        elif len(boxes) > 1:
            cv2.putText(
                frame_bgr,
                "Multiple faces - only one allowed",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 165, 255),
                2,
            )
        else:
            cv2.putText(
                frame_bgr,
                "Press SPACE to capture",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

        cv2.putText(
            frame_bgr,
            f"Name: {name}",
            (10, h - 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame_bgr,
            f"Student ID: {student_id}",
            (10, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        cv2.imshow("Register: Capture face", frame_bgr)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:
            collected_encs = []
            break

        if key == 32 and len(boxes) == 1:
            encs = face_recognition.face_encodings(frame_rgb, boxes)
            if len(encs) == 0:
                print("Could not compute face encoding, try again.")
                continue
            collected_encs.append(encs[0])
            last_good_frame = frame_bgr.copy()
            print(f"Captured sample {len(collected_encs)}")

            if len(collected_encs) >= SAMPLES_PER_STUDENT:
                break

    cap.release()
    cv2.destroyAllWindows()

    if len(collected_encs) == 0:
        return None, None

    encs_arr = np.vstack(collected_encs)
    return last_good_frame, encs_arr


def save_student_record(name, student_id, email, photo_bgr, encs_arr):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    photo_path = os.path.join(PHOTOS_DIR, f"{student_id}_{ts}.jpg")
    enc_path = os.path.join(ENCODINGS_DIR, f"{student_id}_{ts}.npy")

    cv2.imwrite(photo_path, photo_bgr)
    np.save(enc_path, encs_arr)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO students (name, student_id, email, photo_path, encoding_path, date_registered)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (name, student_id, email, photo_path, enc_path, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

    return photo_path, enc_path


def register_student(name: str, student_id: str, email: str = ""):
    init_database()

    if not name or not student_id:
        return False, "Name and student ID are required."

    if student_exists(student_id):
        return False, f"Student with ID {student_id} already exists."

    cam_idx = choose_camera_index()
    if cam_idx < 0:
        return (
            False,
            "No working camera found. Check permissions or close apps using the camera.",
        )

    photo_bgr, encs_arr = capture_face_samples(cam_idx, name, student_id)

    if photo_bgr is None or encs_arr is None:
        return False, "Registration cancelled/failed (no samples collected)."

    photo_path, enc_path = save_student_record(
        name, student_id, email, photo_bgr, encs_arr
    )

    return True, f"Successfully registered {name} ({student_id})!"


def main():
    init_database()

    print("\n================ STUDENT REGISTRATION ================\n")
    name = input("Enter student name: ").strip()
    student_id = input("Enter student ID: ").strip().upper()
    email = input("Enter email (optional): ").strip()

    success, message = register_student(name, student_id, email)
    if success:
        print(f"\n{message}\n")
    else:
        print(f"\n❌ {message}\n")


def create_gui():
    root = tk.Tk()
    root.title("Register New Student")
    root.geometry("600x650")
    root.config(bg=BG_PRIMARY)
    root.resizable(False, False)

    main_container = tk.Frame(root, bg=BG_PRIMARY)
    main_container.pack(expand=True, fill="both", padx=50, pady=40)

    header_frame = tk.Frame(main_container, bg=BG_PRIMARY)
    header_frame.pack(fill="x", pady=(0, 40))

    title = tk.Label(
        header_frame,
        text="Register New Student",
        font=FONT_HEADING,
        bg=BG_PRIMARY,
        fg=TEXT_PRIMARY,
    )
    title.pack()

    subtitle = tk.Label(
        header_frame,
        text="Enter student information to begin registration",
        font=FONT_SUBTITLE,
        bg=BG_PRIMARY,
        fg=TEXT_MUTED,
    )
    subtitle.pack(pady=(10, 0))

    form_frame = tk.Frame(main_container, bg=BG_SECONDARY, relief="flat", bd=0)
    form_frame.pack(expand=True, fill="both", pady=(0, 30))

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

    name_label = tk.Label(
        inner_form,
        text="Full Name *",
        font=FONT_LABEL,
        bg=BG_SECONDARY,
        fg=TEXT_SECONDARY,
        anchor="w",
    )
    name_label.pack(fill="x", pady=(0, 8))

    name_entry = tk.Entry(inner_form, **entry_style)
    name_entry.pack(fill="x", pady=(0, 20), ipady=10)

    student_id_label = tk.Label(
        inner_form,
        text="Student ID *",
        font=FONT_LABEL,
        bg=BG_SECONDARY,
        fg=TEXT_SECONDARY,
        anchor="w",
    )
    student_id_label.pack(fill="x", pady=(0, 8))

    student_id_entry = tk.Entry(inner_form, **entry_style)
    student_id_entry.pack(fill="x", pady=(0, 20), ipady=10)

    email_label = tk.Label(
        inner_form,
        text="Email (Optional)",
        font=FONT_LABEL,
        bg=BG_SECONDARY,
        fg=TEXT_SECONDARY,
        anchor="w",
    )
    email_label.pack(fill="x", pady=(0, 8))

    email_entry = tk.Entry(inner_form, **entry_style)
    email_entry.pack(fill="x", pady=(0, 30), ipady=10)

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

    is_processing = [False]

    def on_take_photos():
        if is_processing[0]:
            return

        name = name_entry.get().strip()
        student_id = student_id_entry.get().strip().upper()
        email = email_entry.get().strip()

        if not name or not student_id:
            status_label.config(
                text="Please fill in all required fields", fg=ERROR_COLOR
            )
            return

        is_processing[0] = True
        status_label.config(text="Processing... Please wait", fg=ACCENT_BLUE)
        take_photos_btn_frame.config(bg=DISABLED_COLOR)
        take_photos_btn_label.config(bg=DISABLED_COLOR)
        root.update()

        try:
            success, message = register_student(name, student_id, email)

            if success:
                status_label.config(text=message, fg=SUCCESS_COLOR)
                name_entry.delete(0, tk.END)
                student_id_entry.delete(0, tk.END)
                email_entry.delete(0, tk.END)
                messagebox.showinfo("Success", message)
            else:
                status_label.config(text=f"{message}", fg=ERROR_COLOR)
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}", fg=ERROR_COLOR)
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        finally:
            is_processing[0] = False
            take_photos_btn_frame.config(bg=ACCENT_BLUE)
            take_photos_btn_label.config(bg=ACCENT_BLUE)

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
            if not is_processing[0]:
                command()

        def on_enter(event):
            if not is_processing[0]:
                darker = (
                    ACCENT_BLUE_HOVER if color == ACCENT_BLUE else ACCENT_GREEN_HOVER
                )
                btn_frame.config(bg=darker)
                btn_label.config(bg=darker)

        def on_leave(event):
            if not is_processing[0]:
                btn_frame.config(bg=color)
                btn_label.config(bg=color)

        btn_frame.bind("<Button-1>", on_click)
        btn_label.bind("<Button-1>", on_click)
        btn_frame.bind("<Enter>", on_enter)
        btn_frame.bind("<Leave>", on_leave)
        btn_label.bind("<Enter>", on_enter)
        btn_label.bind("<Leave>", on_leave)

        return btn_frame, btn_label

    take_photos_btn_frame, take_photos_btn_label = create_button(
        inner_form, "Start Face Capture", on_take_photos, ACCENT_BLUE
    )
    take_photos_btn_frame.pack(pady=(10, 0))

    def on_enter_key(event):
        on_take_photos()

    name_entry.bind("<Return>", on_enter_key)
    student_id_entry.bind("<Return>", on_enter_key)
    email_entry.bind("<Return>", on_enter_key)

    name_entry.focus()

    root.mainloop()


if __name__ == "__main__":
    create_gui()
