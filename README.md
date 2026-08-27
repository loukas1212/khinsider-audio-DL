# Khinsider Audio DL - Fork

A Fork of Khinsider MP3 Downloader by Trash (https://github.com/trash/khinsider-mp3-downloader)

This fork add :

- User Agent
- Compatibility with new python version (Tested on Python 3.14.6, on macOS 26.6.1)
- Fixed the 403's error issue
- Better error handling and log
- Adding color on log (using Colorama)

---

To use the script, put your URL in `inputs.txt` and launch `python3 downloader.py`

To create a VENV and install requirements, please do `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
