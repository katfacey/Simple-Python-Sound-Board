# Simple-Python-Sound-Board

<img src="https://github.com/katfacey/Simple-Python-Sound-Board/blob/1b6dab816d140c8d925e85c092635171f1d0d164/Screenshot%202025-12-23%20083411.png" width="400px" alt="Project IMG"/>

A simple python-based soundboard for my desktop. Vibe-coded with Gemini, and works as intended.

👉Download the zip with the exe in the releases if you just want to use it🔊

🎼Supports MP3, OGG, and WAV🎶

Be advised it will make a JSON file that saves the settings.

Sharing because I can ☠️

# Building Yourself
1. 🌐Download the soundboard🐍 script,💾save to whatever folder you want to work in📁
2. 👨‍💻⌨️
```<PowerShell>
#Create virtual environment
python -m venv venv
venv\Scripts\activate

#Install dependencies
pip install customtkinter pygame pyinstaller

#Build exe
pyinstaller --noconsole --onefile --name "PySoundBoard" soundboard.py

#The final file will be located in the "dist/" folder👈
```
3. ❓❓❓❓
4.  📈Profit💰💸
