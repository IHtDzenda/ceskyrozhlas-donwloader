import argparse
import youtube_dl
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
from bs4 import BeautifulSoup


def check_for_subpages(url):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    div_element = soup.find('h1', class_='b-404__title')
    if div_element:
        return 404
    else:
        return 200

def get_website_title(url):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    div_element = soup.find('div', class_='player-header__title')
    text = div_element.text.strip()
    text = text.replace(' ', '_')
    text = text.replace('/', 'z')
    text=text.split('\n')[0]
    return(text)


def find_mpd_url(url):
    desired_capabilities = DesiredCapabilities.CHROME
    desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    options = webdriver.ChromeOptions()

    options.add_argument('--headless')  
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    time.sleep(1)

    button = driver.find_element(By.XPATH, "//button[@class='as-link audio-btn audio-btn--lg audio-btn--play']")
    button.click()
    time.sleep(2)

    logs = driver.get_log("performance")
    network_logs = []
    for log in logs:
        network_log = json.loads(log["message"])["message"]
        network_logs.append(network_log)

    json_file_path = 'network_log.json'
    with open(json_file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(network_logs))

    driver.quit()

    with open(json_file_path, "r", encoding="utf-8") as f:
        logs = json.loads(f.read())

    for log in logs:
        try:
            url = log["params"]["request"]["url"]

            if url.endswith("manifest.mpd") or url.endswith(".mpd"):
                print(url, end='\n\n')
                return url
        except Exception as e:
            pass

    print('Nebyla nalezena adressa MPD streamu')
    return None




def download_mpd_stream(url,title="output"):
    ydl_opts = {
        'format': 'bestvideo[ext=mp3]+bestaudio[ext=m4a]/best',
        'merge_output_format': 'mp3',
        'outtmpl': f'{title}.mp3',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MPD Stream Downloader')
    parser.add_argument('url', nargs='?', help='URL of the website to scan')
    parser.add_argument('-i', '--input', nargs=2, type=int, help='Two numbers  that are taken as a range and replaces the $i')
    args = parser.parse_args()


    if not args.url:
        args.url = input("Enter the URL of the website to scan: ")

    # if url has $i then create 
    if "X" in args.url:
        #-----------------------TRY FOR THE SOURCE URL withou any parametrs
        try:
            tmpurl = args.url.replace("-X", "")
            status =check_for_subpages(tmpurl)
            print(f'Checking {tmpurl}...status {status}' )
            if status == 200:
                mpd_url = find_mpd_url(tmpurl)
                download_mpd_stream(mpd_url, get_website_title(tmpurl))
        except Exception as e:
            pass
        for i in range(args.input[0], args.input[1]):
            tmpurl = args.url.replace("X", str(i))
            status =check_for_subpages(tmpurl)
            print(f'Checking {tmpurl}...status {status}' )
            if status == 200:
                mpd_url = find_mpd_url(tmpurl)
                download_mpd_stream(mpd_url, get_website_title(tmpurl))
    else:
        print(args.url)


    mpd_url = find_mpd_url(args.url)
    if mpd_url:
        print(f'Downloading MPD stream: {mpd_url}')
        download_mpd_stream(mpd_url, get_website_title(args.url))
    else:
        print('No MPD stream found on the website.')