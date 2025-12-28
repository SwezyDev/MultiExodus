<h1 align="center">
  <a href="https://multiexodus.vercel.app" target="_blank" style="text-decoration: none; color: inherit;">
    💰 Multi Exodus 💰
  </a>
</h1>
<p align="center">
  <img width="128" height="128" alt="176387141287116210" src="https://github.com/user-attachments/assets/c103b405-12a6-4172-8d82-803166d23356" />
</p>
<p align="center">
  <a href="https://www.python.org" target="_blank"><img src="https://img.shields.io/badge/Language-Python-blue?style=for-the-badge&logo=python" /></a>
  <a href="https://t.me/swezy" target="_blank"><img src="https://img.shields.io/badge/Telegram-@Swezy-blue?style=for-the-badge&logo=telegram" /></a>
  <br>
  <code>Leave a ⭐ if you like this Repository</code>
</p>

---

## 🚩 Project overview

**MultiExodus** is a Python-based utility designed to **manage multiple Exodus wallets**. It allows users to import, backup, edit, and switch wallets through a clean and intuitive **graphical interface** built with CustomTkinter.

The application provides a comprehensive set of features including **wallet detection**, **seed phrase recovery automation**, **image and note customization**, **wallet tags and search**, **layout toggle (grid/list view)**, **Discord RPC**, **system tray integration**, and **custom sorting**. It enables **one-click wallet loading into Exodus** with each wallet stored in a dedicated folder for safe backups and easy organization. The program also implements **confirmation dialogs and automated restoration triggers** to ensure safe wallet operations.

MultiExodus leverages **PIL for image handling**, **OS-level commands for wallet management**, **real-time search functionality**, and **scrollable, sortable, grid-based or list-based UI frames** for efficient display and interaction with multiple wallets.

---

## 🤝 Trust & Security
> [!IMPORTANT]
> **Why should you trust MultiExodus with something as sensitive as your wallets?**
> 
> It's very good that you ask yourself this question, please read the [`SAFETY.md`](https://github.com/SwezyDev/MultiExodus/blob/main/SAFETY.md) file



---

## ✨ Features

* 💼 **Multi-Wallet Management** — Detect, search, star, add, edit, and delete multiple Exodus wallets in a single interface.
* 🔄 **Seamless Wallet Switching** — Load any wallet into Exodus instantly with one click, without manual file handling.
* 🔐 **Encryption/Decryption** — You wallet data is protected with military grade encryption (AES 256), makes it impossible for an attacker to steal your Data (Optional).
* 🗂️ **Backup & Recovery Automation** — Automatically trigger Exodus recovery mode, backup existing wallets, and restore seed phrases safely.
* 🖼️ **Custom Wallet Notes & Images** — Assign personalized names, notes, tags, and images to each wallet for easy identification.
* 🏷️ **Wallet Tags & Search** — Organize wallets with custom tags (up to 5 per wallet) and quickly search by wallet name or tag.
* 🔔 **Toast Notifications** — Instant, non-intrusive alerts for everything in MultiExodus, and background tasks—always keeping you informed without interruptions.
* 📊 **Organized UI** — Scrollable, grid-based or list layout with clean, sortable, interactive frames built using CustomTkinter.
* 🔀 **Layout Toggle** — Switch between grid view and list view instantly with a single click or keyboard shortcut (ALT_L).
* 📋 **Multiple Sort Options** — Sort wallets by creation date (Oldest/Newest First) or alphabetically (A-Z/Z-A).
* 💫 **System Tray Integration** — Minimize to tray with full context menu for quick access to all features without opening the main window.
* 🎯 **Single Instance Check** — Prevents multiple instances from running and automatically focuses existing window if launched again.
* 🖱️ **Tooltips** — Hover over any wallet to see detailed information including creation date, notes, tags, and file paths.
* 🎨 **Customizable Window Title** — Personalize the window title with dynamic variables like wallet count, time, date, username, computer name, Exodus version, and message of the day.
* ✅ **Safety Prompts** — Confirmation dialogs for sensitive actions like deleting or overwriting wallets to prevent accidental loss.
* ⭐ **Auto-Updater** — Automatically checks for new versions, verifies integrity with SHA-256, downloads updates securely, and installs them with one click.
* 🖥 **Discord RPC** — Show your friends that you're using MultiExodus.

---

## 🕒 Todo (Planned Features)
* 🎉 Add **Color** Customization — Maybe next Update
* 🌐 Create a modern **Web-App** (Upgrade the GUI) — Unknown
> 💡 View the [`TODO`](https://github.com/SwezyDev/MultiExodus/blob/main/TODO) file in this repository.

---

## 🎹 Keybinds
* ❌ **ESC** — Close Windows
* 🗑️ **DEL** — Delete all Wallets
* 📱 **ALT_L** — Switch Wallet Layout
* ℹ️ **F1** — Show Information Box
* ⚙️ **F2** — Show Settings Menu
* 📂 **F3** — Show Data Folder
* 🛜 **F4** — Check for Updates
* 🔁 **F5** — Reload Wallets
* 👋 **M** — Show Message of Today
* 🔒 **P** — Encrypt Wallet Data
* ➕ **+** — Add a Wallet
* ➖ **-** — Delete the First Wallet
* 📥 * — Load First Wallet

---

## 📥 Easy Installation
1. Download the [Installer](https://github.com/SwezyDev/MultiExodus/releases/download/2.0.0/Multi.Exodus.Installer.exe)
2. Follow the Installer Instructions
3. Run Multi Exodus

---

## 🧭 How It Works

1. Run the application (`python main.py`).
   MultiExodus will create or use your existing MultiExodus directory. The app checks for updates automatically (unless bypassed in settings) and ensures only one instance runs at a time.
2. Browse your wallets in the scrollable grid or list UI.
   Each wallet appears with its name, image, note, tags, and action buttons. Use the search bar to filter wallets by name or tags.
3. Choose an action:
   * ➕ **Add Wallet** — Triggers Exodus' built‑in recovery mode, lets you enter your seed phrase, and then saves the restored wallet under a custom name.
   * 📥 **Load Wallet** — Copies the selected wallet into the official Exodus directory and starts Exodus automatically.
   * 📂 **Open Wallet Location** — Open the Location where your wallet is saved.
   * ⭐ **Star Wallet** — Display your Favorite wallet at the first place.
   * 🏷️ **Add/Edit Tags** — Click on the tags area to add or edit wallet tags (up to 5 tags per wallet).
   * 🔀 **Toggle Layout** — Switch between grid and list view using the button or ALT_L key.
4. Changes are applied instantly, and the UI rebuilds itself to reflect your updated wallet list.
   * ✏️ **Edit Wallet** — Click on the wallet name, note, or image to rename it, change its description, or assign a custom PNG preview.
   * 🗑️ **Delete Wallet** — Removes the wallet folder after confirmation.
   * 🖱️ **Hover for Info** — Hover over any wallet to see detailed information in a tooltip.
5. Access quick actions via the System Tray icon when the window is minimized.
   * Right-click the tray icon for a full menu with all major features.

> ✅ Wallets are stored as separate folders inside your MultiExodus directory. Loading a wallet replaces the active Exodus wallet files — always make backups when needed.

---

## 🧰 Requirements

* 🐍 Python **3.9+**
* 📦 Dependencies:

  ```bash
  pip install customtkinter CTkToolTip Pillow psutil pypresence pystray requests
  ```
* 💻 [Exodus](https://www.exodus.com/download) installed and working.
* 💾 Access to your Exodus installation directory and multi-wallet folder (ensure the app has permission to read/write files).
* 🖼️ Optional: PNG images for custom wallet previews. (Recommended size: 130x130)

---

## 🔑 Notes on Safety & Usage

* Only run MultiExodus on machines you own or where you have explicit permission.
* Always backup your wallets before adding, loading, or deleting them. MultiExodus will overwrite the active Exodus wallet when loading another.
* Carefully follow prompts during seed phrase recovery — entering incorrect data can corrupt a wallet.
* PNG images and notes are stored locally; deleting or renaming files outside the app may break wallet previews.

---

## 📝 Repository structure 

```/
├─ assets/ ➔ Files that are required to run the Application
│ ├─ app.ico ➔ MultiExodus Icon
│ ├─ info.txt ➔ Information about MultiExodus
│ ├─ motd.txt ➔ Message of today text
│ ├─ preview.png ➔ A screenshot of the Program running
│ └─ title.png ➔ Standard wallet preview picture
├─ multi_exodus/ ➔ Scripts that are required to run the Application
│ ├─ __init__.py ➔ Exposes main
│ ├─ app.py ➔ Main app window and event loop
│ ├─ constants.py ➔ Defines wallet and Exodus directory paths
│ ├─ dialogs.py ➔ Custom input dialog for user prompts
│ ├─ info.py ➔ Custom Information box
│ ├─ motd.py ➔ Custom Message of the Day box
│ ├─ protection.py ➔ Encryption/Decryption Functions to protect Wallet Data
│ ├─ rpc.py ➔ Discord RPC handling
│ ├─ settings.py ➔ Custom Settings box to configure MultiExodus
│ ├─ toast.py ➔ Windows Toast Notification handle
│ ├─ tray.py ➔ Tray Icon on Taskbar to control MultiExodus
│ ├─ ui.py ➔ Builds the scrollable wallet interface and handles UI interactions
│ ├─ update.py ➔ Auto-Update Helper Functions for MultiExodus
│ └─ wallet_manager.py ➔ Manage, edit, and load Exodus wallets with backup support
├─ .gitignore ➔ Specifies files and directories Git should ignore
├─ LICENSE ➔ License file
├─ MultiExodus.sha256 ➔ SHA256 file for Auto-Updater
├─ README.md ➔ Read me file
├─ main.py ➔ Start the Application
├─ requirements.txt ➔ Packages that are required to run the Application
└─ TODO ➔ Planned Features & Improvements
```

---

## 🖼️ Preview

<p align="center">
  <img src="https://img.shields.io/badge/CustomTkinter-%20GUI-blueviolet?style=for-the-badge"/>
  <br><br>
  <img src="https://github.com/SwezyDev/MultiExodus/blob/main/assets/preview.png?raw=true" alt="Program preview">
</p>

---

## 🧠 Recovery Mode Trigger

How i found the trigger to enter the Recovery Mode:

<img width="753" height="652" alt="Screenshot 2025-11-23 045631" src="https://github.com/user-attachments/assets/b6677ffe-091b-4d31-a41a-316303f1d9b9" />

You can see that a file was created by Exodus called `restore-mnemonic` in the `%appdata%\Exodus` directory.

---

## ⚙️ Technical Details

* Detects wallets by scanning `MULTI_WALLET_DIR` and sorting by creation time, alphabetically, or by starred status.
* Allows adding, renaming, editing notes/images/tags, deleting, and loading wallets into Exodus.
* Backs up current Exodus wallet before importing new wallets using the restore-mnemonic trigger.
* Custom UI with `customtkinter`, including scrollable grid/list views, interactive buttons, search bar, and labels.
* Loads and resizes wallet images with `PIL`, with optional rounded corners.
* Uses `MyInputDialog` for custom modal input prompts.
* Manages Exodus.exe with `ctypes` message boxes, `os.startfile`, and `taskkill`.
* Performs file operations using `shutil` and `pathlib`.
* Updates window title with dynamic variables (wallet count, time, date, username, computer name, Exodus version, MOTD) via a `background thread`.
* Validates the running executable with `SHA-256`, checks GitHub for newer releases, downloads the latest installer, and launches it using `os.startfile`.
* Connects to Discord RPC via `pypresence` using the `Application ID` from the discord developer portal.
* Uses `win10toast` for Windows Toast Notifications.
* To encrypt wallet data it uses `cryptography (Fernet)` with `AES-256` Encryption.
* System tray integration with `pystray` for background operation and quick access menu.
* Single instance enforcement with `psutil` to prevent multiple app instances from running simultaneously.
* Wallet search functionality filters by wallet name and tags in real-time.
* Tag system allows up to 5 tags per wallet for better organization, stored in `tags.txt` files.
* Layout toggle feature switches between grid (5 columns) and list (single column) view modes.
* Wallet starring system stores favorite status in `starred.txt` files and prioritizes starred wallets in the UI.

---

## ⚖️ License

Distributed under the **MIT License**. See [`LICENSE`](https://github.com/SwezyDev/MultiExodus/blob/main/LICENSE) for more information.

---

## 🙌 Credits & contact

- Maintainer: [@SwezyDev](https://github.com/SwezyDev) — reach out via Telegram: [@Swezy](https://t.me/swezy)  

---

## 🚨 Disclaimer

This project is **unofficial** and is **not** affiliated with any vendor. It is meant for **personal use** only.

---

## 📣 Final note

MultiExodus is a personal wallet‑management helper, built to let users organize and switch between multiple Exodus wallets more efficiently.
It does not modify Exodus itself and is not affiliated with Exodus or any other vendor.

Use it responsibly, securely, and only on systems and wallets you own and control. Always keep backups of important wallets, and never share your seed phrases with anyone — including this tool.
