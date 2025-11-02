import cv2
import face_recognition
import numpy as np
import sqlite3
import os
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from theme import *

DB_DIR = "db"
DB_PATH = os.path.join(DB_DIR, "attendance.db")
DETECTION_MODEL = "hog"
TOLERANCE = 0.6

Path(DB_DIR).mkdir(parents=True, exist_ok=True)


def init_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            student_name TEXT NOT NULL,
            attendance_date TEXT NOT NULL,
            attendance_time TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        );
    """
    )
    conn.commit()
    conn.close()


def load_all_students():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT student_id, name, encoding_path FROM students
    """
    )
    rows = cur.fetchall()
    conn.close()

    students_data = []
    for student_id, name, encoding_path in rows:
        if encoding_path and os.path.exists(encoding_path):
            try:
                encodings = np.load(encoding_path)
                if encodings.ndim == 2:
                    mean_encoding = np.mean(encodings, axis=0)
                else:
                    mean_encoding = encodings
                students_data.append(
                    {
                        "student_id": student_id,
                        "name": name,
                        "encoding": mean_encoding,
                    }
                )
            except Exception as e:
                print(f"Error loading encoding for {student_id}: {e}")
                continue

    return students_data


def is_already_marked_today(student_id):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT COUNT(*) FROM attendance 
        WHERE student_id = ? AND attendance_date = ?
    """,
        (student_id, today),
    )
    count = cur.fetchone()[0]
    conn.close()
    return count > 0


def mark_attendance(student_id, student_name):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    timestamp_str = now.isoformat()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO attendance (student_id, student_name, attendance_date, attendance_time, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """,
        (student_id, student_name, date_str, time_str, timestamp_str),
    )
    conn.commit()
    conn.close()


def choose_camera_index():
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


def start_attendance_session():
    init_database()
    students_data = load_all_students()

    if len(students_data) == 0:
        return False, "No registered students found. Please register students first."

    cam_idx = choose_camera_index()
    if cam_idx < 0:
        return (
            False,
            "No working camera found. Check permissions or close apps using the camera.",
        )

    known_encodings = [student["encoding"] for student in students_data]
    known_ids = [student["student_id"] for student in students_data]
    known_names = [student["name"] for student in students_data]

    cap = cv2.VideoCapture(cam_idx, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        return False, "Could not open camera"

    marked_today = set()

    print("\n================= ATTENDANCE SESSION =================")
    print("• Look at the camera")
    print("• Attendance will be marked automatically when face is recognized")
    print("• Press ESC to stop the session")
    print("=====================================================\n")

    while True:
        ok, frame_bgr = cap.read()
        if not ok or frame_bgr is None:
            print("Failed to read from camera")
            break

        frame_bgr = cv2.flip(frame_bgr, 1)
        h, w = frame_bgr.shape[:2]

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(frame_rgb, model=DETECTION_MODEL)

        recognized = False
        recognized_student = None

        if len(boxes) > 0:
            encodings = face_recognition.face_encodings(frame_rgb, boxes)

            for encoding, (top, right, bottom, left) in zip(encodings, boxes):
                matches = face_recognition.compare_faces(
                    known_encodings, encoding, tolerance=TOLERANCE
                )
                face_distances = face_recognition.face_distance(
                    known_encodings, encoding
                )

                if True in matches:
                    best_match_idx = np.argmin(face_distances)
                    if matches[best_match_idx]:
                        recognized = True
                        student_id = known_ids[best_match_idx]
                        student_name = known_names[best_match_idx]
                        recognized_student = {
                            "student_id": student_id,
                            "name": student_name,
                        }

                        color = (0, 255, 0)
                        label = f"{student_name} ({student_id})"

                        if student_id in marked_today:
                            label += " - Already Marked"
                            color = (0, 165, 255)
                        else:
                            if not is_already_marked_today(student_id):
                                mark_attendance(student_id, student_name)
                                marked_today.add(student_id)
                                print(
                                    f"Attendance marked: {student_name} ({student_id})"
                                )
                                label += " - Marked!"
                            else:
                                marked_today.add(student_id)
                                label += " - Already Marked Today"
                                color = (0, 165, 255)
                    else:
                        color = (0, 0, 255)
                        label = "Unknown"
                else:
                    color = (0, 0, 255)
                    label = "Unrecognized"

                cv2.rectangle(frame_bgr, (left, top), (right, bottom), color, 2)
                cv2.rectangle(
                    frame_bgr,
                    (left, bottom - 35),
                    (right, bottom),
                    color,
                    cv2.FILLED,
                )
                cv2.putText(
                    frame_bgr,
                    label,
                    (left + 6, bottom - 6),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

        cv2.putText(
            frame_bgr,
            f"Students registered: {len(students_data)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame_bgr,
            f"Marked today: {len(marked_today)}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame_bgr,
            "Press ESC to stop",
            (10, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        if len(boxes) == 0:
            cv2.putText(
                frame_bgr,
                "No face detected",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )

        cv2.imshow("Attendance Session", frame_bgr)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    return True, f"Session ended. {len(marked_today)} students marked today."


def create_gui():
    root = tk.Tk()
    root.title("Mark Attendance")
    root.geometry("600x500")
    root.config(bg=BG_PRIMARY)
    root.resizable(False, False)

    main_container = tk.Frame(root, bg=BG_PRIMARY)
    main_container.pack(expand=True, fill="both", padx=50, pady=40)

    header_frame = tk.Frame(main_container, bg=BG_PRIMARY)
    header_frame.pack(fill="x", pady=(0, 40))

    title = tk.Label(
        header_frame,
        text="Mark Attendance",
        font=FONT_HEADING,
        bg=BG_PRIMARY,
        fg=TEXT_PRIMARY,
    )
    title.pack()

    subtitle = tk.Label(
        header_frame,
        text="Start attendance session to automatically mark student presence",
        font=FONT_SUBTITLE,
        bg=BG_PRIMARY,
        fg=TEXT_MUTED,
    )
    subtitle.pack(pady=(10, 0))

    content_frame = tk.Frame(main_container, bg=BG_SECONDARY, relief="flat", bd=0)
    content_frame.pack(expand=True, fill="both", pady=(0, 30))

    inner_content = tk.Frame(content_frame, bg=BG_SECONDARY)
    inner_content.pack(expand=True, fill="both", padx=40, pady=40)

    status_label = tk.Label(
        inner_content,
        text="",
        font=FONT_STATUS,
        bg=BG_SECONDARY,
        fg=TEXT_MUTED,
        wraplength=400,
        justify="center",
    )
    status_label.pack(pady=(0, 20))

    is_running = [False]

    def on_start_session():
        if is_running[0]:
            return

        is_running[0] = True
        status_label.config(text="Starting session...", fg=ACCENT_BLUE)
        start_btn_frame.config(bg=DISABLED_COLOR)
        start_btn_label.config(bg=DISABLED_COLOR)
        root.update()

        try:
            success, message = start_attendance_session()

            if success:
                status_label.config(text=message, fg=SUCCESS_COLOR)
                messagebox.showinfo("Session Ended", message)
            else:
                status_label.config(text=message, fg=ERROR_COLOR)
                messagebox.showerror("Error", message)
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}", fg=ERROR_COLOR)
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        finally:
            is_running[0] = False
            start_btn_frame.config(bg=ACCENT_GREEN)
            start_btn_label.config(bg=ACCENT_GREEN)
            status_label.config(text="Click 'Start Session' to begin", fg=TEXT_MUTED)

    def create_button(parent, text, command, color=ACCENT_GREEN):
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
            if not is_running[0]:
                command()

        def on_enter(event):
            if not is_running[0]:
                darker = (
                    ACCENT_BLUE_HOVER if color == ACCENT_BLUE else ACCENT_GREEN_HOVER
                )
                btn_frame.config(bg=darker)
                btn_label.config(bg=darker)

        def on_leave(event):
            if not is_running[0]:
                btn_frame.config(bg=color)
                btn_label.config(bg=color)

        btn_frame.bind("<Button-1>", on_click)
        btn_label.bind("<Button-1>", on_click)
        btn_frame.bind("<Enter>", on_enter)
        btn_frame.bind("<Leave>", on_leave)
        btn_label.bind("<Enter>", on_enter)
        btn_label.bind("<Leave>", on_leave)

        return btn_frame, btn_label

    start_btn_frame, start_btn_label = create_button(
        inner_content, "Start Session", on_start_session, ACCENT_GREEN
    )
    start_btn_frame.pack(pady=(20, 0))

    status_label.config(text="Click 'Start Session' to begin", fg=TEXT_MUTED)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
