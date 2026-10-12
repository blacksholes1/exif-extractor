# exif-extractor
opsec level 100
# Media Forensic Scanner and Metadata Toolkit

A command-line Python application designed to inspect, analyze, and scrub metadata from image and video files. The toolkit includes forensic scanning for synthetic generation signatures, an atomic overwrite tool to sanitize privacy markers, and an advanced extractor that parses EXIF/ISO data into structured JSON files with embedded geographic mappings.

## System Prerequisites

To process video formats (such as .mp4, .mov, and .mkv), this suite requires FFmpeg to be installed on your system path.

* **macOS**: Install via Homebrew using `brew install ffmpeg`
* **Windows**: Install via winget using `winget install Gyan.FFmpeg` or download the binaries from the official FFmpeg website and add them to your System Environment Variables.

---

## 1. Installing Python

### macOS
macOS often includes a stub version of Python. Follow these steps to install the official production release:

1. Download the latest Python 3 installer from the official Python website (python.org).
2. Run the downloaded package installer and follow the on-screen prompts.
3. Verify the installation by opening Terminal and running:
   ```bash
   python3 --version
   pip3 --version
   ```

### Windows
1. Download the executable installer for Windows x64 from python.org.
2. Launch the installer.
3. **Critical Step**: Check the box at the bottom that reads **"Add python.exe to PATH"** before clicking "Install Now".
4. Open Command Prompt or PowerShell and verify the installation:
   ```cmd
   python --version
   pip --version
   ```

---

## 2. Installing Required Dependencies

This toolkit relies on external Python packages to process image layouts and matrix operations. Run the following command matching your operating system.

### macOS
Open the Terminal application and execute:
```bash
pip3 install pillow opencv-python numpy
```

### Windows
Open Command Prompt or PowerShell and execute:
```cmd
pip install pillow opencv-python numpy
```

---

## 3. How to Run the Script

Execute the Python script by invoking the python interpreter followed by the relative path of the file you wish to run.

### macOS
```bash
python3 advanced_extractor.py
```

### Windows
```cmd
python advanced_extractor.py
```

To exit any of the scripts while they are running in the loop, type `exit` into the prompt and press Enter, or press `Ctrl + C`.

---

## 4. How to Drag and Drop Files into the Terminal

The scripts are engineered with automatic path parsing to support native file drag-and-drop actions across all major platforms. 

1. Launch your script using the execution commands listed in Section 3.
2. Locate the target image or video file within Finder (macOS) or File Explorer (Windows).
3. Click and hold the file, then drag it directly into the active Terminal window.
4. Release the mouse button. The terminal will automatically paste the absolute file path at your active cursor.
5. Press `Enter` to run the analysis or metadata operation.

### Usage Restrictions
* **Windows Administrator Mode Block**: If you run Windows Terminal or Command Prompt with elevated administrative permissions ("Run as Administrator"), Windows User Account Control (UAC) security policies will block standard File Explorer windows from dragging and dropping files into it. To fix this, run your Terminal normally without elevation.
* **Window Focus**: When you drop an object into a terminal shell, formatting characters are populated, but window focus may remain on your file system explorer. Ensure you click inside the terminal window to focus the prompt before pressing Enter.
