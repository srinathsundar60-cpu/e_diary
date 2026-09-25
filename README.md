# 📔 E-Diary (MiniDiary)

A modern, distraction-free desktop personal journal and daily task management application built with **Python**, **Kivy**, and **SQLite3**.

Designed with a sleek dark theme, **E-Diary** connects your thoughts, memories, and daily tasks directly to calendar dates.

---

## ✨ Features

- 📅 **Interactive Calendar & Date Navigation**
  - Clean monthly view highlighting the current day.
  - Compact segmented navigators (`‹` / `›`) for both Month and Year.
  - Compact, scrollable dropdown selectors that keep your workspace neat.
  - One-click **Today** shortcut to instantly jump back to the current date.

- ✍️ **Daily Journaling Editor**
  - Distraction-free, full-featured multiline text editor for each date.
  - **Dynamic Journaling Prompts**: Empty dates greet you with motivational journaling prompts (e.g., *"What's today's vibe? ✨"*, *"What made you smile today?"*).
  - Prompts disappear automatically when you start typing and are never stored in your database.
  - Visual save confirmation ("Saved ✔") ensures your thoughts are safe.

- ✅ **Date-Specific To-Do Planner**
  - Add tasks categorized with priority levels:
    - 🔴 **High**
    - 🟠 **Medium**
    - 🟢 **Low**
  - Mark tasks as completed with a single click (`✓` / `✔`), moving them down with subtle visual feedback.
  - Delete individual tasks quickly with `✕`.
  - Cheerful empty-state illustrations when all tasks are complete.

- 🔒 **Safe Local Data Storage**
  - Built-in SQLite persistence stored in `%LOCALAPPDATA%\E-Diary\mini_diary.db`.
  - Your personal thoughts and tasks stay 100% offline and private on your machine.
  - Data remains intact across app updates and runs safely without requiring administrator privileges.

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+ (Tested on Python 3.13)
- **GUI Framework:** [Kivy](https://kivy.org/)
- **Database:** SQLite 3
- **Packaging:** PyInstaller & Inno Setup

---

## 🚀 Getting Started

### Prerequisites

Ensure you have **Python 3.10+** installed on your system.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/srinathsundar60-cpu/e_diary.git
   cd e_diary
   ```

2. **Install dependencies:**
   ```bash
   pip install kivy
   ```

3. **Launch the application:**
   ```bash
   python main.py
   ```

---

## 📁 Project Structure

```text
├── main.py            # Main application entry point & screen controllers
├── ediary.kv          # Declarative Kivy UI layouts and styling
├── database.py        # SQLite database operations & table definitions
├── main.spec          # PyInstaller build specification
├── APP/
│   └── E-Diary.iss    # Inno Setup Windows installer script
├── .gitignore         # Excludes build caches, executables, and temporary files
└── README.md          # Project documentation
```

---

## 📦 Building Standalone Executable (Windows)

To package the application into a standalone `.exe`:

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Build executable:**
   ```bash
   python -m PyInstaller main.spec --noconfirm
   ```
   The compiled executable will be generated inside the `dist/` directory.

3. **Create Windows Installer (Optional):**
   Open `APP/E-Diary.iss` with [Inno Setup](https://jrsoftware.org/isinfo.php) and click **Compile** to build the Windows setup installer wizard.

---

## 📄 License

This project is licensed under the MIT License - feel free to use and customize it for your personal journaling needs.
