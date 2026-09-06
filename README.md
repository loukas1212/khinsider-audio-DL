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

Or, if you don't want to use `inputs.txt`, just run `python3 downloader.py -u "urlhere"`

To create a VENV and install requirements, please run the following commands :

```bash
python3 -m venv venv

venv\Scripts\activate # Windows
source venv/bin/activate # macOS/Linux

pip install -r requirements.txt
```
