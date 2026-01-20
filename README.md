# Tafim Monitor ☀️

**Tafim Monitor** is a modern, lightweight, and beautiful display brightness controller for Windows. Inspired by Monitorian, it features a sleek "Glass/Acrylic" UI design that integrates seamlessly with Windows 10 and 11 aesthetics.

![Icon](assets/icon.png)

## ✨ Features
- **Glass / Acrylic UI**: Native Windows background blur effect.
- **Multi-Monitor Support**: Control brightness for all connected monitors individually.
- **Smooth Controls**: Non-blocking, threaded slider interaction for instant feedback.
- **System Tray**: Runs quietly in the background; click the tray icon to pop up.
- **Portable**: Available as a standalone installer.

## 🚀 Installation

### Option 1: Installer (Recommended)
Download the latest `tafim_monitor_installer.exe` from the Releases page (if available) or build it yourself.
1. Run `tafim_monitor_installer.exe`.
2. The app will be installed to your Start Menu.

### Option 2: Run from Source
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/tafim_monitor.git
   cd tafim_monitor
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: This project requires Python 3.10+.*

3. **Run the app**:
   ```bash
   python main.py
   ```

## 🛠️ Building

To build the executable and installer yourself:

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```
2. **Build Executable**:
   ```bash
   pyinstaller tafim_monitor.spec
   ```
   *(Or check the `main.py` build command in documentation)*

3. **Compile Installer**:
   - Install [Inno Setup](https://jrsoftware.org/isdl.php).
   - Compile `setup.iss`.

## 📦 Dependencies
- `customtkinter` (UI Framework)
- `screen_brightness_control` (Monitor DDC/CI control)
- `pystray` (System Tray)
- `Pillow` (Image processing)

## 📄 License
MIT License. Free to use and modify.
