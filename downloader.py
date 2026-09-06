import argparse
import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

init(autoreset=True)

BASE_URL = 'https://downloads.khinsider.com'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    )
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def validate_url(url):
    return '//downloads.khinsider.com/game-soundtracks/album/' in url


def safe_filename(name):
    """Strip characters that are invalid in file names on most OSes."""
    invalid = '<>:"/\\|?*'
    for ch in invalid:
        name = name.replace(ch, '')
    return name.strip()


def get_soup(url):
    resp = SESSION.get(url, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, 'html.parser')


def fetch_from_url(url):
    url = url.strip()
    if not url:
        print(Fore.RED + "No URL found in inputs.txt")
        return

    if not validate_url(url):
        print(Fore.RED + 'URL is invalid : ' + url)
        return
    print(Fore.GREEN + 'URL found: ' + url)

    base_dir = 'downloads'
    url_parts = url.rstrip('/').split('/')
    dir_name = os.path.join(base_dir, url_parts[-1])

    os.makedirs(dir_name, exist_ok=True)

    print(Fore.GREEN + 'Crawling for links, Please wait...')

    try:
        soup = get_soup(url)
    except requests.RequestException as e:
        print(Fore.RED + 'Failed to load album page : ' + str(e))
        return

    song_list = soup.find(id='songlist')
    if song_list is None:
        print(Fore.RED + 'Could not find song list on page. Please double check the url.')
        return

    anchors = song_list.find_all('a')

    # href (string) -> song name (string)
    song_map = {}

    for anchor in anchors:
        href = anchor.get('href')
        if href and 'mp3' in href:
            full_href = href if href.startswith('http') else BASE_URL + href
            name = anchor.string or anchor.get_text()
            if full_href not in song_map:
                song_map[full_href] = name

    if not song_map:
        print(Fore.RED + 'No links found for the url. Please double check that the url is correct and try again.')
        return

    print(Fore.GREEN + str(len(song_map)) + ' Links acquired')

    downloaded_mp3s = {}

    for href, song_name in song_map.items():
        try:
            link_soup = get_soup(href)
        except requests.RequestException as e:
            print(Fore.RED + 'Failed to load song page for "' + str(song_name) + '": ' + str(e))
            continue

        audio = link_soup.find('audio')
        if audio is None or not audio.get('src'):
            print(Fore.RED + 'No audio source found for "' + str(song_name) + '"')
            continue

        mp3_url = audio.get('src')

        if mp3_url in downloaded_mp3s:
            continue
        downloaded_mp3s[mp3_url] = True

        file_name = safe_filename(str(song_name)) + '.mp3'
        file_on_disk_path = os.path.join(dir_name, file_name)

        try:
            head = SESSION.head(mp3_url, timeout=15, allow_redirects=True)
            file_size = float(head.headers.get('Content-Length', 0)) / 1000000
        except requests.RequestException:
            file_size = 0

        file_already_downloaded = False
        if os.path.exists(file_on_disk_path) and file_size:
            stat = os.stat(file_on_disk_path)
            file_already_downloaded = round(float(stat.st_size) / 1000000, 2) == round(file_size, 2)

        if file_already_downloaded:
            print(Fore.BLUE + 'Skipping "' + file_name + '" already downloaded.')
            continue

        print(Fore.BLUE + 'Downloading ' + file_name + (' [%.2fMB]' % file_size if file_size else ''))

        try:
            with SESSION.get(mp3_url, timeout=30, stream=True) as r:
                r.raise_for_status()
                with open(file_on_disk_path, 'wb') as output:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            output.write(chunk)
            print(Fore.GREEN + 'Download finished for "' + file_name + '"')
        except requests.RequestException as e:
            print(Fore.RED + 'Failed to download "' + file_name + '": ' + str(e))
            if os.path.exists(file_on_disk_path):
                os.remove(file_on_disk_path)

        # Be polite to the server
        time.sleep(0.5)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Downloads an album from downloads.khinsider.com'
    )
    parser.add_argument(
        '-u', '--url',
        type=str,
        default=None,
        help='URL of the khinsider album page to download (e.g. -u "https://downloads.khinsider.com/game-soundtracks/album/..." )'
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.url:
        fetch_from_url(args.url)
        return

    input_file_name = 'inputs.txt'
    if os.path.exists(input_file_name):
        print(Fore.BLUE + 'Input file found. Parsing for links...')
        with open(input_file_name, 'r') as file:
            for line in file:
                fetch_from_url(line)
    else:
        print(Fore.BLUE + "No inputs.txt file found.")
        print(Fore.BLUE + 'Please input link in quotes to album on khinsider.')
        url = input('Url: ')
        fetch_from_url(url)


if __name__ == '__main__':
    main()