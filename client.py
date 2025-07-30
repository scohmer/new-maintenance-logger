import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime
from ldap3 import Server, Connection, ALL, SIMPLE
from dotenv import load_dotenv
import os

# ───────────── Load Environment Variables ─────────────
load_dotenv()

# API server config
SERVER_IP = os.getenv("API_SERVER_IP")
SERVER_PORT = os.getenv("API_SERVER_PORT")
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}/log"

# LDAP connection config
LDAP_SERVER = os.getenv("LDAP_SERVER")
LDAP_USER = os.getenv("LDAP_USER")
LDAP_PASSWORD = os.getenv("LDAP_PASSWORD")
LDAP_BASE_DN = os.getenv("LDAP_BASE_DN")

# ───────────── Validate Environment ─────────────
missing_vars = [var for var in ["LDAP_SERVER", "LDAP_USER", "LDAP_PASSWORD", "LDAP_BASE_DN"] if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# ───────────── Functions ─────────────

def get_current_user():
    try:
        domain = os.environ.get("USERDOMAIN", "")
        user = os.environ.get("USERNAME", "")
        return f"{domain}\\{user}" if domain else user
    except Exception:
        return "unknown"

def get_systems_from_ldap():
    try:
        server = Server(LDAP_SERVER, get_info=ALL)
        conn = Connection(
            server,
            user=LDAP_USER,
            password=LDAP_PASSWORD,
            authentication=SIMPLE,
            auto_bind=True
        )
        conn.search(LDAP_BASE_DN, '(objectClass=computer)', attributes=['name'])
        systems = sorted(
            entry['attributes']['name']
            for entry in conn.response
            if 'attributes' in entry and 'name' in entry['attributes']
        )
        conn.unbind()
        return systems
    except Exception as e:
        print("LDAP error:", e)
        return []

def submit_log():
    manual_input = manual_system.get().strip()
    system = manual_input if manual_input else selected_system.get().strip()
    action = text_action.get("1.0", tk.END).strip()
    user = current_user

    if not system:
        messagebox.showerror("Missing Info", "System name is required.")
        return

    if not action:
        messagebox.showerror("Missing Info", "Action field cannot be blank.")
        text_action.focus_set()
        text_action.config(highlightbackground="red", highlightcolor="red", highlightthickness=2)
        return
    else:
        text_action.config(highlightthickness=0)

    payload = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "user": user,
        "action": action,
        "system": system
    }

    try:
        response = requests.post(SERVER_URL, json=payload)
        if response.status_code == 200:
            messagebox.showinfo("Success", "✅ Log submitted successfully.")
            text_action.delete("1.0", tk.END)
            manual_system.set("")
            text_action.focus_set()
            text_action.config(highlightthickness=0)
        else:
            messagebox.showerror("Error", f"❌ Server error:\n{response.text}")
    except Exception as e:
        messagebox.showerror("Connection Failed", f"❌ Could not connect to server:\n{e}")

# ───────────── GUI Setup ─────────────

root = tk.Tk()
root.title("Maintenance Log Entry")
root.geometry("460x440")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", padding=6, font=("Segoe UI", 10))
style.configure("TLabel", font=("Segoe UI", 10))
style.configure("TEntry", font=("Segoe UI", 10))

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

current_user = get_current_user()
ttk.Label(frame, text=f"User: {current_user}").pack(anchor="w", pady=(0, 10))

ttk.Label(frame, text="Select System:").pack(anchor="w")

system_list = get_systems_from_ldap()
selected_system = tk.StringVar()
manual_system = tk.StringVar()

if system_list:
    selected_system.set(system_list[0])
    dropdown = ttk.OptionMenu(frame, selected_system, system_list[0], *system_list)
    dropdown.pack(fill="x", pady=(0, 10))
else:
    selected_system.set("Unavailable")
    ttk.Label(frame, text="⚠️ No systems found in LDAP.").pack()

ttk.Label(frame, text="(or enter a system name manually):").pack(anchor="w")
entry = ttk.Entry(frame, textvariable=manual_system)
entry.pack(fill="x", pady=(0, 15))

ttk.Label(frame, text="Action:").pack(anchor="w")
text_action = tk.Text(frame, height=6, font=("Segoe UI", 10), wrap="word", highlightthickness=0, relief="solid")
text_action.pack(fill="both", pady=(0, 15))

# Allow Ctrl+Enter to submit from Action box
def on_ctrl_enter(event):
    submit_log()
    return "break"

text_action.bind("<Control-Return>", on_ctrl_enter)

# Button area
button_frame = ttk.Frame(frame)
button_frame.pack(pady=5)

submit_btn = ttk.Button(button_frame, text="Submit", command=submit_log)
submit_btn.pack(side="left", padx=(0, 10))

exit_btn = ttk.Button(button_frame, text="Exit", command=root.destroy)
exit_btn.pack(side="left")

entry.focus_set()

root.mainloop()
