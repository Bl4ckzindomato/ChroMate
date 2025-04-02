# Modern Chromium Updater with Dark Mode (customtkinter)
# SHA256 validation, sync/nosync selection, embedded log viewer, scheduler support
# Developed by Fatih | Designed with customtkinter for a modern, user-friendly experience
# Requirements: pip install customtkinter requests pefile plyer

# Copyright (c) 2025 Fatih
# This tool is provided as-is under the MIT License.

import customtkinter as ctk
from tkinter import filedialog
import os, json, subprocess, sys, tempfile, threading, time, requests, pefile, hashlib, webbrowser
from datetime import datetime
from plyer import notification

# === CONFIG ===
CONFIG_FILE = "settings.json"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "chromium_updater.log")
ICON_FILE = os.path.join(SCRIPT_DIR, "chromium_updater_icon.ico")
TEMP_DIR = tempfile.gettempdir()
VERS_FILE = os.path.join(TEMP_DIR, "chromium_last_version.txt")
GITHUB_API = "https://api.github.com/repos/Hibbiki/chromium-win64/releases/latest"  # Uses Hibbiki's Chromium builds
VERSION = "1.0.0"

DEFAULT_CONFIG = {
    "install_path": "",
    "notifications": True,
    "check_interval": "manual",
    "enable_scheduler": False,
    "download_type": "sync"
}

# === CORE FUNCTIONS ===
def log(msg):
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{ts} {msg}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    if logbox:
        logbox.insert("end", line)
        logbox.see("end")

def clear_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("")
    if logbox:
        logbox.delete("0.0", "end")
    log("[✓] Log cleared")

def notify(title, msg, enabled=True):
    if enabled:
        try:
            icon_path = os.path.join(SCRIPT_DIR, "chromium_updater_icon.ico")
            notification.notify(
                title=title,
                message=msg,
                app_name="Chromium Updater",
                app_icon=icon_path,
                timeout=6
            )
        except Exception as e:
            log(f"[X] Notification error: {e}")

def version_tuple(v):
    import re
    m = re.match(r"(\d+)\.(\d+)\.(\d+)\.(\d+)", v.strip("v"))
    return tuple(map(int, m.groups())) if m else (0,0,0,0)

def get_chrome_version(path):
    try:
        pe = pefile.PE(path)
        for fileinfo in pe.FileInfo:
            for entry in fileinfo:
                if entry.Key == b'StringFileInfo':
                    for st in entry.StringTable:
                        return st.entries.get(b'ProductVersion', b'').decode()
    except:
        return ""

def sha256sum(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def download_with_progress(url, dest, cb=None):
    r = requests.get(url, stream=True)
    total = int(r.headers.get('content-length', 0))
    downloaded = 0
    start = time.time()
    with open(dest, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                elapsed = time.time() - start
                eta = int((total - downloaded) / (downloaded/elapsed)) if downloaded else 0
                if cb: cb(downloaded, total, eta)

def validate_sha256(download_path, hash_url):
    try:
        r = requests.get(hash_url)
        expected_hash = r.text.strip().split()[0]
        actual_hash = sha256sum(download_path)
        return expected_hash == actual_hash
    except:
        return False

def apply_scheduler(enabled, interval):
    task_name = "ChromiumUpdaterAutoCheck"
    exe_path = os.path.abspath(sys.argv[0])
    if enabled:
        interval_map = {
            "daily": "DAILY",
            "weekly": "WEEKLY",
            "monthly": "MONTHLY"
        }
        if interval in interval_map:
            subprocess.run([
                "schtasks", "/Create", "/SC", interval_map[interval], "/TN", task_name,
                "/TR", f'\"{exe_path}\"', "/ST", "10:00", "/F"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            log(f"[Scheduler] Task created: {interval_map[interval]}")
    else:
        subprocess.run(["schtasks", "/Delete", "/TN", task_name, "/F"], stderr=subprocess.DEVNULL)
        log("[Scheduler] Task removed")

# GUI bağlantısı: zamanlayıcı değiştiğinde hemen uygula

def scheduler_settings_updated():
    apply_scheduler(scheduler_var.get(), interval_var.get())


def auto_detect_chrome():
    candidates = [
        os.path.expandvars(r"%LocalAppData%\\Chromium\\Application\\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles%\\Chromium\\Application\\chrome.exe")
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return ""


def threaded_update():
    threading.Thread(target=check_for_update).start()

def check_for_update():
    chrome_path = path_var.get()
    dl_type = dl_type_var.get()
    notify_enabled = notify_var.get()

    if not os.path.exists(chrome_path):
        progress_label.set("Chromium not found. Please set path.")
        notify("Chromium Updater", "Chromium not found on this system.", notify_enabled)
        return

    progress_label.set("Checking for updates...")
    try:
        r = requests.get(GITHUB_API, timeout=10)
        release = r.json()
        latest = release["tag_name"]
    except Exception as e:
        log(f"[GitHub] Error: {e}")
        notify("GitHub Error", str(e), notify_enabled)
        progress_label.set("GitHub error.")
        return

    current = get_chrome_version(chrome_path)
    if version_tuple(current) >= version_tuple(latest):
        progress_label.set("Chromium is up-to-date.")
        notify("Chromium", "Already up-to-date", notify_enabled)
        return

    asset = next((a for a in release["assets"] if f".{dl_type}.exe" in a["name"]), None)
    hash_asset = next((a for a in release["assets"] if f".{dl_type}.exe.sha256sum" in a["name"]), None)
    if not asset or not hash_asset:
        progress_label.set("Installer or hash missing.")
        notify("Missing Asset", "Installer or checksum file missing", notify_enabled)
        return

    url = asset["browser_download_url"]
    hash_url = hash_asset["browser_download_url"]
    filename = os.path.join(TEMP_DIR, asset["name"])

    def update_bar(done, total, eta):
        percent = int((done / total) * 100)
        bar.set(percent)
        m, s = divmod(eta, 60)
        progress_label.set(f"Downloading... {percent}% | ETA: {m:02}:{s:02}")

    download_with_progress(url, filename, cb=update_bar)

    progress_label.set("Verifying file integrity...")
    if not validate_sha256(filename, hash_url):
        progress_label.set("SHA256 mismatch! Aborting.")
        notify("Security Warning", "Downloaded file failed hash check", notify_enabled)
        return

    subprocess.Popen([filename], shell=True)
    with open(VERS_FILE, 'w') as f:
        f.write(latest)
    progress_label.set("Installation started.")
    notify("Chromium Updated", f"{latest} installed.", notify_enabled)

# === GUI SETUP ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
root = ctk.CTk()
root.title("Chromium Updater")
root.geometry("600x680")

path_var = ctk.StringVar()
notify_var = ctk.BooleanVar(value=True)
dl_type_var = ctk.StringVar(value="sync")
progress_label = ctk.StringVar(value="Idle.")
scheduler_var = ctk.BooleanVar(value=False)
interval_var = ctk.StringVar(value="daily")
logbox = None

config = DEFAULT_CONFIG
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config.update(json.load(f))

if not config["install_path"]:
    detected = auto_detect_chrome()
    config["install_path"] = detected
    if detected:
        notify("Chromium Updater", f"Chromium detected at: {detected}")
    else:
        notify("Chromium Updater", "Chromium not detected.")

path_var.set(config["install_path"])
notify_var.set(config["notifications"])
dl_type_var.set(config.get("download_type", "sync"))
scheduler_var.set(config.get("enable_scheduler", False))
interval_var.set(config.get("check_interval", "daily"))

frame = ctk.CTkFrame(root, corner_radius=8)
frame.pack(padx=6, pady=6, fill="both", expand=True)

ctk.CTkLabel(frame, text="Chromium Executable Path:").pack(anchor="w")
row = ctk.CTkFrame(frame)
row.pack(fill="x")
ctk.CTkEntry(row, textvariable=path_var).pack(side="left", fill="x", expand=True)
ctk.CTkButton(row, text="Browse", command=lambda: path_var.set(filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")]))).pack(side="left", padx=5)

ctk.CTkLabel(frame, text="Download Type:").pack(anchor="w", pady=(10,0))
drop = ctk.CTkOptionMenu(frame, variable=dl_type_var, values=["sync", "nosync"])
drop.pack(fill="x")
ctk.CTkLabel(
    frame,
    text="\nSYNC VERSION:\n• Standard Chromium build with Google Sign-in & Sync functionality.\n\nNO SYNC VERSION:\n• Ungoogled Chromium – Privacy-enhanced version without Google services.",
    text_color="gray",
    justify="left",
    font=ctk.CTkFont(size=12)
).pack(anchor="w")

ctk.CTkLabel(frame, text="Schedule Auto-Update:").pack(anchor="w", pady=(10,0))
scheduler_frame = ctk.CTkFrame(frame)
scheduler_frame.pack(fill="x")
ctk.CTkCheckBox(scheduler_frame, text="Enable Scheduler", variable=scheduler_var, command=scheduler_settings_updated).pack(side="left")
interval_menu = ctk.CTkOptionMenu(scheduler_frame, variable=interval_var, values=["daily", "weekly", "monthly"], command=lambda _: scheduler_settings_updated())
interval_menu.pack(side="right")

ctk.CTkCheckBox(frame, text="Show Desktop Notifications", variable=notify_var).pack(anchor="w", pady=10)

ctk.CTkButton(frame, text="Check for Updates", command=threaded_update).pack(pady=10)

bar = ctk.CTkProgressBar(frame, width=400)
bar.set(0)
bar.pack(pady=5)
ctk.CTkLabel(frame, textvariable=progress_label).pack()

ctk.CTkLabel(frame, text="Update Log:").pack(anchor="w", pady=(10,0))
logbox = ctk.CTkTextbox(frame, height=160)
logbox.pack(fill="both", expand=True)
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logbox.insert("0.0", f.read())

# === LOG CLEAR BUTTON ===
ctk.CTkButton(frame, text="Clear Log", command=clear_log).pack(pady=5)

# Developer credit footer (clickable GitHub profile)
def open_github():
    webbrowser.open("https://github.com/fatih-gh")

footer_frame = ctk.CTkFrame(root, fg_color="transparent")
footer_frame.pack(pady=(0, 4), fill="x")

def open_repo():
    webbrowser.open("https://github.com/fatih-gh/ChroMate/tree/main")

def open_license():
    webbrowser.open("https://github.com/fatih-gh/ChroMate/blob/main/LICENSE")


ctk.CTkButton(
    footer_frame,
    text=f"Version {VERSION}",
    command=open_repo,
    width=1,
    height=1,
    fg_color="transparent",
    text_color="gray",
    font=ctk.CTkFont(size=11),
    hover=True
).pack(side="right", padx=10)

ctk.CTkButton(
    footer_frame,
    text="GPLv3 License",
    command=open_license,
    width=1,
    height=1,
    fg_color="transparent",
    text_color="gray",
    font=ctk.CTkFont(size=11),
    hover=True
).pack(side="right")


ctk.CTkButton(footer_frame, text="Developed by Fatih © 2025", text_color="gray", font=ctk.CTkFont(size=13, weight="bold"), fg_color="transparent", hover=False, command=open_github).pack(side="left", padx=10)

# Save config and apply scheduler on close
def on_exit():
    data = {
        "install_path": path_var.get(),
        "notifications": notify_var.get(),
        "check_interval": interval_var.get(),
        "enable_scheduler": scheduler_var.get(),
        "download_type": dl_type_var.get()
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)
    apply_scheduler(data["enable_scheduler"], data["check_interval"])
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_exit)
root.mainloop()