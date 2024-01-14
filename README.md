# Rapidgator Downloader
A program to download multiple rapidgator files at the same time. **THIS DOESN'T WORK IF YOU DON'T HAVE A PREMIUM SUBSCRIPTION !**
## Installation
```
git clone https://github.com/zhgwn/rgdl
cd rgdl
pip install -r requirements.txt
```
## Usage
```
python main.py -u <The value of the `user__` cookie of your rapidgator session> "https://rapidgator.net/file/ab94ffffdcd1e096a0ad74b4bd719e29/2022.03.01_3542728312.mp4" "https://rapidgator.net/file/565671ffffffffffffff934ce74f91dd/2023.03.19_358121352441372672.mp4"
```
This will download both of the files at the same time. You can put as much as you want. Here is the help:
```
usage: Rapidgator Download [-h] -u USER [-d DIR] [-c CONCURENCY] [urls ...]

positional arguments:
  urls                  The urls to download. Can also be just the hash.

options:
  -h, --help            show this help message and exit
  -u USER, --user USER  Value of your `user__` cookie.
  -d DIR, --dir DIR, --directory DIR
                        The directory to write the files to.
  -c CONCURENCY, --concurency CONCURENCY
                        The max amount of file to download at the same time.
```