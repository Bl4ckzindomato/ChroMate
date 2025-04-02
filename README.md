# 🌐 ChroMate

[![Latest Release](https://img.shields.io/github/v/release/fatih-gh/ChroMate?style=flat-square)](https://github.com/fatih-gh/ChroMate/releases/latest) [![Download EXE](https://img.shields.io/badge/Download-EXE-blue?style=flat-square)](https://github.com/fatih-gh/ChroMate/releases/latest/download/ChroMate.exe)

> Your daily dose of Chromium freshness – automatic updates, dark mode, and sync options bundled into one sleek GUI.

---

**ChroMate** is a modern, sleek, and powerful updater for Chromium on Windows. Built with a dark-themed interface using `customtkinter`, it makes staying updated as effortless as clicking a button.

---

## ✨ Features

- ✅ **Sync / No-Sync Build Selection**
- 🌙 **Dark Mode UI** (customtkinter powered)
- 🔄 **Automatic Update Check with Scheduler Support**
- 📦 **SHA256 File Integrity Validation**
- 📥 **Progress Bar with ETA** for downloads
- 🔔 **Native Desktop Notifications** (via `plyer`)
- 📜 **Integrated Log Viewer** + Clear Logs Button
- ⚙️ **Windows Task Scheduler Integration**
- 🧠 **Smart Chromium Detection** (auto finds installation path)

---

## 📸 Screenshots

<p align="center">
  <img src="https://github.com/user-attachments/assets/255c67e0-6e6d-48c3-8d80-cb598503b3f2" width="700"/>
</p>

---

## 🛠 Installation

```bash
pip install customtkinter requests pefile plyer
```

> ⚠️ Requires **Python 3.9+** on Windows

---

## 🚀 Usage

### Option 1: Run from source
```bash
python main_gui.py
```

### Option 2: Download the prebuilt executable
➡️ Visit the [Releases](https://github.com/fatih-gh/ChroMate/releases) section to download the latest `.exe` build — no Python needed!

### Option 3: Build manually using PyInstaller
```bash
pyinstaller --noconfirm --onefile --windowed \
  --icon=chromium_updater_icon.ico \
  --add-data "chromium_updater_icon.ico;." \
  main_gui.py
```

---

## 🔍 Sync vs No-Sync?

- **Sync** = Standard Chromium build with Google Sign-in and sync functionality.
- **No-Sync** = Ungoogled Chromium – privacy-enhanced, stripped from Google services.

You're free to choose the flavor that fits your needs 😎

---

## 🧠 Developer Note

This project uses [Hibbiki](https://github.com/Hibbiki/chromium-win64)'s Chromium builds. Make sure to star their repo too!

---

## 📄 License

GPLv3 License © 2025 Fatih

This project is licensed under the terms of the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Developed by [Fatih](https://github.com/fatih-gh)**  
Say hi or report an issue — contributions and ideas are welcome!

