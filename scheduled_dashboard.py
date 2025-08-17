"""
Scheduled Job Status Dashboard Automation Tool

Purpose:
    Connects to a MySQL database to retrieve and display scheduled job status logs
    in a live-updating Tkinter GUI dashboard.

    Displays:
        - Running jobs started today without subsequent success/failure
        - Failed jobs within the last 7 days
        - Successful jobs within the last 7 days

Requirements:
    - Python 3.12+
    - pandas
    - mysql-connector-python
    - zoneinfo (standard in Python 3.9+)
    - tzlocal
    - tkinter (standard)
"""

import pandas as pd
import mysql.connector
from zoneinfo import ZoneInfo
from tzlocal import get_localzone_name
from datetime import datetime
from tkinter import Tk, Frame, Label


# Example argument class for config; replace with argparse or your own logic if needed
class Args:
    TEST = False


MY_ARGS = Args()

REFRESH_INTERVAL = 15000  # milliseconds for Tkinter after()

# ------------- DATABASE CONFIGURATION -------------
DB_CONFIG = {
    "host": "your_db_host_here",
    "user": "your_db_user_here",
    "password": "your_db_password_here",
    "database": "your_db_name_here_test" if MY_ARGS.TEST else "your_db_name_here",
}


# ------------- FETCH DATA FUNCTION -------------
def fetch_status_data():
    """Fetch scheduled job logs from database and process running, success, fail sets."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM tbl_schedlog
            ORDER BY friendlyName, entry_time
        """)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)

        # Map scheduled column from 1/0 to Yes/No
        df["scheduled"] = df["scheduled"].map({1: "Yes", 0: "No"})
        df["entry_time"] = pd.to_datetime(df["entry_time"])
        df.sort_values(["friendlyName", "entry_time"], inplace=True)

        today = pd.Timestamp.now().normalize()

        # Identify running jobs started today without later success/fail
        running_jobs = df[(df["statusName"] == "START") & (df["entry_time"] >= today)]
        for name in running_jobs["friendlyName"].unique():
            later_outcomes = df[
                (df["friendlyName"] == name)
                & (df["statusName"].isin(["SUCCESS", "FAIL"]))
            ]
            if not later_outcomes[
                later_outcomes["entry_time"]
                > running_jobs[running_jobs["friendlyName"] == name]["entry_time"].max()
            ].empty:
                running_jobs = running_jobs[running_jobs["friendlyName"] != name]

        now = pd.Timestamp.now()
        recent_success = df[
            (df["statusName"] == "SUCCESS")
            & (df["entry_time"] >= now - pd.Timedelta(days=7))
        ].sort_values("entry_time", ascending=False)

        recent_fail = df[
            (df["statusName"] == "FAIL")
            & (df["entry_time"] >= now - pd.Timedelta(days=7))
        ].sort_values("entry_time", ascending=False)

        def format_time(df):
            if "entry_time" in df.columns:
                df = df.copy()
                df["entry_time"] = df["entry_time"].dt.tz_localize(
                    "UTC", nonexistent="NaT", ambiguous="NaT"
                )
                local_tz = ZoneInfo(get_localzone_name())
                df["entry_time"] = df["entry_time"].dt.tz_convert(local_tz)
                df["entry_time"] = df["entry_time"].dt.strftime("%d %b %Y @ %H:%M")
            return df

        running_jobs = format_time(running_jobs)
        recent_success = format_time(recent_success)
        recent_fail = format_time(recent_fail)

        return running_jobs, recent_success, recent_fail, True

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        empty_df = pd.DataFrame()
        return empty_df, empty_df, empty_df, False


# ------------- GUI SETUP AND REFRESH -------------
def create_table(frame, title, color, df):
    from tkinter import ttk

    Label(frame, text=title, fg=color, font=("Segoe UI", 14, "bold")).pack(
        anchor="w", pady=(10, 2)
    )
    if df.empty:
        Label(frame, text="No entries found.", fg="gray").pack(anchor="w")
        return

    columns = list(df.columns)

    style = ttk.Style()
    style.theme_use("default")

    style.configure(
        "Custom.Treeview.Heading",
        background="#557c9f",
        foreground="white",
        font=("Segoe UI", 10, "bold"),
        padding=(8, 6),
        relief="flat",
        borderwidth=0,
    )

    style.configure(
        "Custom.Treeview",
        background="white",
        foreground="black",
        rowheight=25,
        fieldbackground="white",
    )

    style.map("Custom.Treeview", background=[("selected", "#cce5ff")])

    tree_frame = ttk.Frame(frame, borderwidth=1, relief="solid")
    tree_frame.pack(fill="x", padx=5, pady=(5, 10))

    tree = ttk.Treeview(
        tree_frame,
        columns=columns,
        show="headings",
        height=len(df),
        style="Custom.Treeview",
    )

    column_widths = {
        "id": 35,
        "entry_time": 130,
        "user": 115,
        "friendlyName": 160,
        "statusName": 90,
        "statusMessage": 1300,
        "scheduled": 80,
    }

    for col in columns:
        tree.heading(col, text=col, anchor="w")
        width = column_widths.get(col, 120)
        tree.column(col, anchor="w", width=width, stretch=(col not in column_widths))

    for i, (_, row) in enumerate(df.iterrows()):
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        tree.insert("", "end", values=list(row), tags=(tag,))

    tree.tag_configure("oddrow", background="white")
    tree.tag_configure("evenrow", background="#e6ecf1")

    tree.pack(fill="x", expand=True)


def refresh_dashboard():
    for widget in dashboard_frame.winfo_children():
        widget.destroy()

    running, success, fail, connected = fetch_status_data()
    create_table(dashboard_frame, "🔄 Running Jobs", "orange", running)
    create_table(dashboard_frame, "❌ Failed (last 7 days)", "red", fail)
    create_table(dashboard_frame, "✅ Recent Success (last 7 days)", "green", success)

    now_str = datetime.now().strftime("%H:%M:%S")
    if connected:
        status_label.config(
            text=f"🟢 Server Connected | Last refresh at {now_str}", fg="green"
        )
    else:
        status_label.config(
            text=f"🔴 Server unavailable | Last refresh at {now_str}", fg="red"
        )

    root.after(REFRESH_INTERVAL, refresh_dashboard)


# ------------- MAIN GUI -------------
root = Tk()
root.title("Scheduled Job Status Dashboard" + (" - TEST" if MY_ARGS.TEST else ""))
root.state("zoomed")

Label(
    root,
    text="Scheduled Job Status Dashboard",
    fg="#557c9f",
    font=("Segoe UI", 18, "bold"),
).pack(pady=10)

dashboard_frame = Frame(root)
dashboard_frame.pack(fill="both", expand=True)

status_label = Label(root, text="🟢 Server connected", font=("Segoe UI", 12))
status_label.pack(side="bottom", anchor="e", padx=10, pady=5)

refresh_dashboard()

if __name__ == "__main__":
    root.mainloop()
