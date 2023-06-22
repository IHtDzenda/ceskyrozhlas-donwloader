# Downloader for  muj-rozhlas.cz
This tool allows you to download audio from  muj-rozhlas.cz

This program uses [YT-DLP](https://github.com/yt-dlp/yt-dlp) 

# Installation
You will need:
 - [Python 3.10+](https://www.python.org/downloads/)
 - Google Chrome browser

In CMD (as administrator), run the following command:

``cd <the path you downloaded this repo to>``

and then:

``python pip install -r dependencies.txt``

This will ensure you have all the dependencies required for this program to work.


# How to use?
In CMD , run the following command:

``cd <the path you downloaded this repo to>``

## If you are on windows 
You can doubleclick on the ``windows_run.bat`` (this fixed the permission error on windows with the file network_log.json)
After which you will promted to input the url 



## Single file download

``python mujrozhlas.py example.com ``

## Multiple file download
example sites:

 `example.com/audiopodcast/epizoda-1 ` 
 `example.com/audiopodcast/epizoda-2 `

- Replace the episode number at the end of the url with  -X 


``python mujrozhlas.py example.com/audiopodcast-X ``


# Issues
As of writing this README.md, it seems that everything is working correctly. Please submit an issue if you find one.


# Getting help
In case something doesn't work:
 - Make sure you have everything set up correctly
 - Google the error code or **submit an issue**.


# To do
 - Fix that awful speed display


## Note
This program was created solely for **educational purposes**. 
This program is a learning example of "web scraping"