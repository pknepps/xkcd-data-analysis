import requests
from bs4 import BeautifulSoup

COMICS_SOURCE = r"https://www.explainxkcd.com/wiki/index.php/List_of_all_comics_(full)"


def main():
    res = requests.get(COMICS_SOURCE)
    if not res.ok:
        print("Error getting COMICS_SOURCE")
        exit(1)
    data = res.content

if __name__ == '__main__':
    main()