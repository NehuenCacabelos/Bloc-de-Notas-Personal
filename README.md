# Dark-Mode Notepad Suite (Bloc de Notas)

A dual-implementation of a modern, premium dark-mode notepad suite, featuring clean aesthetics, responsive interfaces, and custom styling.

This repository contains two implementations:
1. **Python version (`notepad.py`)**: A lightweight desktop app built with Tkinter, featuring a Windows 11-style top bar, session auto-saving, and a standalone precompiled executable with a custom icon.
2. **Java version (`src/main/`)**: A robust desktop application managed by **Spring Boot 3.x** and built using **JavaFX 17** and **Maven**.

---

## 🐍 Python Implementation (Tkinter)

A fast, standalone minimalist notepad with dark mode, custom file naming, and auto-session loading.

### Key Features
- **File Naming Top Bar**: Name entry field with auto-clear placeholder ("Sin nombre") and legibility enhancements.
- **Auto-Session Restore**: Remembers and automatically reopens your last edited file.
- **Custom Icon**: Bundled with a premium neon-themed glassmorphism icon.
- **Built Executable**: A standalone `.exe` version is precompiled in the `dist/` directory.

### Quick Start
To run the python version:
```powershell
py notepad.py
```
Or simply double-click the standalone executable located in:
`dist/notepad.exe`

---

## ☕ Java Implementation (Spring Boot & JavaFX)

A professional desktop text editor utilizing Spring's Dependency Injection and JavaFX styling.

### Key Features
- **Spring Lifecycle Management**: App configuration and UI controllers are fully managed components in Spring context.
- **Rich Status Bar**: Displays current zoom level, cursor line/column, encoding, and CRLF options in real-time.
- **Dynamic Zoom & Style**: Global text color picker, font formatting (bold/regular), and font-zoom utilities (+ / - / 100%).

### Quick Start
To build and run the Java version using the local Maven wrapper:
```powershell
.\mvnw.cmd spring-boot:run
```

---

## ⌨️ General Keyboard Shortcuts
- **Ctrl + N**: New File
- **Ctrl + O**: Open File
- **Ctrl + S**: Save File
- **Ctrl + Shift + S**: Save As
- **Ctrl + =** / **Ctrl + -**: Zoom In / Zoom Out
- **Ctrl + 0**: Reset zoom to 100%
- **Ctrl + Q**: Exit application
