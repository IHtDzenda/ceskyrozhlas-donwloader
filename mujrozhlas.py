import argparse
import youtube_dl
import time
import json
import logging
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from colorama import init, Fore

init()#start colorama


def check_if_pageexists(url):
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
    options.add_argument('--disable-logging') 


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
                return url
        except Exception as e:
            pass

    print(Fore.RED + 'Nebyla nalezena adressa MPD streamu' + Fore.RESET)
    return None




def download_mpd_stream(url,title="output"):
    ydl_opts = {
        'no_warnings': True,
        'format': 'bestvideo[ext=mp3]+bestaudio[ext=m4a]/best',
        'merge_output_format': 'mp3',
        'outtmpl': f'{title}.mp3',
    }
    print(Fore.GREEN + f'---------------[Downloading]----------------'+Fore.RESET)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print(Fore.GREEN + f'-------------------[DONE]-------------------'+Fore.RESET)


if __name__ == '__main__':
    #arguments
    parser = argparse.ArgumentParser(description='MPD Stream Downloader')
    parser.add_argument('url', nargs='?', help='URL of the website to scan')
    parser.add_argument('-i', '--input', nargs='?',default=50, type=int, help='Range of nubers from 0 to X that are taken as a range and replaces the X in the url ')
    args = parser.parse_args()
    if not args.url:
        args.url = input("Enter the URL of the website to scan \n=> ")

    # if url has $i then create 
    if "X" in args.url:
        #-----------------------TRY FOR THE SOURCE URL withou any parametrs
        timeoutcap=7
        timeout=0
        try:
            tmpurl = args.url.replace("-X", "")
            print(Fore.YELLOW +'Checking for:'+Fore.RESET)
            print('=>'+Fore.BLUE+tmpurl+Fore.RESET)
            status =check_if_pageexists(tmpurl)

            if status == 200:
                print(Fore.GREEN +f'=>Status {status} - OK'+Fore.RESET )
                mpd_url = find_mpd_url(tmpurl)
                website_title = get_website_title(tmpurl)
                print(Fore.MAGENTA +f'=>File name: {website_title}.mp3'+Fore.RESET )
                download_mpd_stream(mpd_url,website_title)
            else:
                print(Fore.RED + f'=>Status {status} - Failed page not found' +Fore.RESET)
        except Exception as e:
            pass

        for i in range(0, args.input):
            tmpurl = args.url.replace("X", str(i))
            status =check_if_pageexists(tmpurl)
            print(Fore.YELLOW +'Checking for:'+Fore.RESET)
            print('=>'+Fore.MAGENTA+tmpurl+Fore.RESET)
            if timeoutcap==timeout:
                print(Fore.RED + '-----------------ERROR-----------------' +Fore.RESET)
                print(Fore.RED + f'WEBSITE TIMEOUT TO MANY FAILED URLS ' +Fore.RESET)
                print(Fore.RED + f'            !!!EXITING!!!           ' +Fore.RESET)
                exit()

            if status == 200:
                print(Fore.GREEN +f'=>Status {status} - OK'+Fore.RESET)
                mpd_url = find_mpd_url(tmpurl)
                website_title = get_website_title(tmpurl)
                print(Fore.BLUE +f'=>File name: {website_title}.mp3'+Fore.RESET )
                download_mpd_stream(mpd_url,website_title)
            else:
                timeout=timeout+1
                print(Fore.RED + f'=>Status {status} - Failed page not found' +Fore.RESET)
            
    else:
        status =check_if_pageexists(args.url)
        print(Fore.YELLOW +'Checking for:'+Fore.RESET)
        print('=>'+Fore.MAGENTA+args.url+Fore.RESET)
        if status == 200:
            print(Fore.GREEN +f'=>Status {status} - OK'+Fore.RESET)
            mpd_url = find_mpd_url(args.url)
            website_title = get_website_title(args.url)
            print(Fore.BLUE +f'=>File name: {website_title}.mp3'+Fore.RESET )
            download_mpd_stream(mpd_url,website_title)
        else:
            print(Fore.RED + f'=>Status {status} - Failed page not found' +Fore.RESET)



    if mpd_url:
        download_mpd_stream(mpd_url, get_website_title(args.url))
    else:
        print(Fore.RED +'No  stream found on the website.'+Fore.RESET)