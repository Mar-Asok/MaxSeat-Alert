from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sqlite3
# ---------------- DATABASE ----------------
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
""")
cursor.execute("SELECT * FROM users WHERE username='admin'")
if not cursor.fetchone():
    cursor.execute(
        "INSERT INTO users(username,password) VALUES(?,?)",
        ("admin", "1234")
    )
conn.commit()
# Base directory for resource files (images)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ---------------- WINDOW ----------------
root = Tk()
root.title("MAXSEAT ALERT")
# SCREEN SIZE
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
# RESPONSIVE SIZE
window_width = int(screen_width * 0.35)
window_height = int(screen_height * 0.75)
# MINIMUM SIZE
if window_width < 350:
    window_width = 350
if window_height < 600:
    window_height = 600
# CENTER WINDOW
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.resizable(True, True)
root.configure(bg="#d9f2ff")
root.attributes("-alpha", 0.0)
# ---------------- FADE IN ----------------
def fade_in():
    alpha = root.attributes("-alpha")
    if alpha < 1:
        alpha += 0.05
        root.attributes("-alpha", alpha)
        root.after(50, fade_in)
fade_in()
# ---------------- TABLE FUNCTION ----------------
def create_table(parent):
    table_container = Frame(parent, bg="white")
    table_container.pack(pady=10, fill="x")
    headers = ["Type", "Company", "Passenger", "Location", "Date and Time"]
    for i, h in enumerate(headers):
        Label(
            table_container,
            text=h,
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#333333"
        ).grid(row=0, column=i, padx=15, pady=10)
    data = [
        ("🚌", "Señor Pedro Lines", "14/22", "Bulua Terminal", "3/25/2026 - 11:31"),
        ("🚌", "Oro Transit", "23/22", "Agora Terminal", "3/25/2026 - 11:31"),
        ("🚌", "MisOr Express", "18/22", "Agora Terminal", "3/25/2026 - 11:31"),
        ("🚌", "CDEO Movers", "15/22", "Bulua Terminal", "3/25/2026 - 11:31"),
        ("🚌", "Bukidnon Trans", "22/22", "Agora Terminal", "3/25/2026 - 11:31"),
        ("🚌", "Bukidnon Express", "26/22", "Agora Terminal", "3/25/2026 - 11:31"),
    ]
    for i, row in enumerate(data, start=1):
        bg_color = "#f2f2f2" if i % 2 == 0 else "white"
        for j, val in enumerate(row):
            color = "red" if val in ["23/22", "22/22", "26/22"] else "black"
            Label(
                table_container,
                text=val,
                font=("Arial", 10),
                bg=bg_color,
                fg=color,
                padx=10,
                pady=5
            ).grid(row=i, column=j, sticky="nsew", padx=2, pady=2)
# ---------------- RECORDS WINDOW ----------------
def open_records():
    records = Toplevel(root)
    records.title("PUV Violators Records")
    records.geometry(f"{screen_width-100}x{screen_height-100}")
    records.configure(bg="#d9f2ff")
    try:
        records.state("zoomed")
    except:
        pass
    # MAIN FRAME
    main_frame = Frame(records, bg="#eaf6ff")
    main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
    # LEFT PANEL
    left_panel = Frame(main_frame, bg="#dff2ff", width=180)
    left_panel.pack(side=LEFT, fill=Y)
    # LOGO
    try:
        logo_img = Image.open(os.path.join(BASE_DIR, "logo.png"))
        logo_img = logo_img.resize((120, 80))
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = Label(left_panel, image=logo_photo, bg="#dff2ff")
        logo_label.image = logo_photo
        logo_label.pack(pady=20)
    except:
        Label(
            left_panel,
            text="MAXSEAT ALERT",
            font=("Arial", 16, "bold"),
            fg="red",
            bg="#dff2ff"
        ).pack(pady=20)
    # BACK BUTTON
    Button(
        left_panel,
        text="Go back to\nDashboard",
        font=("Arial", 12, "bold"),
        bg="black",
        fg="white",
        bd=0,
        cursor="hand2",
        command=records.destroy
    ).pack(pady=20, ipadx=10, ipady=10)
    # RIGHT CONTENT
    content = Frame(main_frame, bg="#eaf6ff")
    content.pack(side=RIGHT, fill=BOTH, expand=True, padx=20, pady=20)
    # TITLE 1
    Label(
        content,
        text="List of PUV violators",
        font=("Arial", 22, "bold"),
        bg="#eaf6ff",
        fg="#3d4c5a"
    ).pack(pady=10)
    create_table(content)
    # TITLE 2
    Label(
        content,
        text="List of intercepted PUV violators",
        font=("Arial", 22, "bold"),
        bg="#eaf6ff",
        fg="#3d4c5a"
    ).pack(pady=20)
    create_table(content)
# ---------------- DASHBOARD ----------------
def open_dashboard():
    dashboard = Toplevel(root)
    dashboard.title("MAXSEAT ALERT DASHBOARD")
    dashboard.geometry(f"{window_width}x{window_height}")
    dashboard.configure(bg="#cfefff")
    dashboard.resizable(True, True)
    # TITLE
    Label(
        dashboard,
        text="MAXSEAT ALERT",
        font=("Arial", 18, "bold"),
        bg="#cfefff",
        fg="red"
    ).pack(pady=10)
    # MAP FRAME
    map_frame = Frame(dashboard, bg="white")
    map_frame.pack(pady=10, fill="x", padx=15)
    try:
        map_img = Image.open(os.path.join(BASE_DIR, "map.png"))
        map_img = map_img.resize((350, 200))
        map_photo = ImageTk.PhotoImage(map_img)
        map_label = Label(map_frame, image=map_photo)
        map_label.image = map_photo
        map_label.pack(fill="both", expand=True)
    except:
        Label(
            map_frame,
            text="Map Placeholder",
            bg="white"
        ).pack(expand=True, pady=80)
    # LEGEND
    legend_frame = Frame(dashboard, bg="#cfefff")
    legend_frame.pack(pady=5)
    Label(
        legend_frame,
        text="● Moving (50)",
        fg="green",
        bg="#cfefff",
        font=("Arial", 10, "bold")
    ).pack(side=LEFT, padx=10)
    Label(
        legend_frame,
        text="● Stopped (12)",
        fg="red",
        bg="#cfefff",
        font=("Arial", 10, "bold")
    ).pack(side=LEFT, padx=10)
    # TABLE
    table_frame = Frame(dashboard, bg="white")
    table_frame.pack(
        pady=10,
        fill="both",
        expand=True,
        padx=15
    )
    headers = ["Company", "Passenger", "Location", "Time"]
    for i, h in enumerate(headers):
        Label(
            table_frame,
            text=h,
            font=("Arial", 10, "bold"),
            bg="white"
        ).grid(row=0, column=i, padx=5, pady=5)
    data = [
        ("Señor Pedro Lines", "14/22", "Bulua Terminal", "13:04"),
        ("Oro Transit", "23/22", "Agora Terminal", "13:04"),
        ("MisOr Express", "18/22", "Bulua Terminal", "13:04"),
        ("CDEO Movers", "15/22", "Bulua Terminal", "13:04"),
        ("Bukidnon Trans", "22/22", "Agora Terminal", "13:04"),
        ("Bukidnon Express", "26/22", "Agora Terminal", "13:04"),
    ]
    for i, row in enumerate(data, start=1):
        for j, val in enumerate(row):
            color = "red" if val in ["23/22", "22/22", "26/22"] else "black"
            Label(
                table_frame,
                text=val,
                fg=color,
                bg="white",
                font=("Arial", 9)
            ).grid(row=i, column=j, padx=5, pady=3)
    # BUTTON
    Button(
        dashboard,
        text="Go to Records",
        bg="black",
        fg="white",
        font=("Arial", 10, "bold"),
        bd=0,
        command=open_records
    ).pack(pady=10, ipadx=10, ipady=5)
# ---------------- LOGIN ----------------
def login():
    username = username_entry.get()
    password = password_entry.get()
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )
    user = cursor.fetchone()
    if user:
        open_dashboard()
    else:
        messagebox.showerror("Error", "Invalid Credentials")
# ---------------- PASSWORD TOGGLE ----------------
show_password = False
def toggle_password():
    global show_password
    if show_password:
        password_entry.config(show="*")
        eye_btn.config(text="👁")
        show_password = False
    else:
        password_entry.config(show="")
        eye_btn.config(text="🙈")
        show_password = True
# ---------------- LOGIN CARD ----------------
card_width = int(window_width * 0.7)
if card_width > 320:
    card_width = 320
card = Frame(root, bg="white")
card.place(
    relx=0.5,
    rely=0.5,
    anchor=CENTER,
    width=card_width,
    height=350
)
# ---------------- LOGO ----------------
try:
    img = Image.open(os.path.join(BASE_DIR, "logo.png"))
    img = img.resize((150, 95))
    logo = ImageTk.PhotoImage(img)
    Label(card, image=logo, bg="white").pack(pady=(20, 10))
except:
    Label(
        card,
        text="MAXSEAT ALERT",
        font=("Arial", 18, "bold"),
        bg="white",
        fg="red"
    ).pack(pady=30)
# ---------------- USERNAME ----------------
username_entry = Entry(
    card,
    font=("Arial", 11),
    bd=0,
    bg="#e8eef2"
)
username_entry.pack(
    fill="x",
    padx=25,
    ipady=8,
    pady=10
)
username_entry.insert(0, "admin")
# ---------------- PASSWORD FRAME ----------------
pass_frame = Frame(card, bg="#e8eef2")
pass_frame.pack(
    pady=10,
    fill="x",
    padx=25
)
pass_frame.columnconfigure(0, weight=1)
password_entry = Entry(
    pass_frame,
    font=("Arial", 11),
    bd=0,
    bg="#e8eef2",
    show="*"
)
password_entry.grid(
    row=0,
    column=0,
    sticky="ew",
    ipady=8,
    padx=(10, 0)
)
password_entry.insert(0, "1234")
eye_btn = Button(
    pass_frame,
    text="👁",
    bd=0,
    bg="#e8eef2",
    command=toggle_password,
    cursor="hand2"
)
eye_btn.grid(row=0, column=1, padx=5)
# ---------------- FORGOT PASSWORD ----------------
Label(
    card,
    text="Forgot password?",
    font=("Arial", 10),
    bg="white"
).pack(anchor="e", padx=30)
# ---------------- LOGIN BUTTON ----------------
Button(
    card,
    text="Login",
    bg="black",
    fg="white",
    font=("Arial", 12, "bold"),
    bd=0,
    command=login
).pack(
    fill="x",
    padx=25,
    pady=25,
    ipady=8
)
root.mainloop()
conn.close()