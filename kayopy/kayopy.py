import contextlib
from bs4 import BeautifulSoup
import requests
import webbrowser
import argparse
import gdown
from tkinter import filedialog
import urllib.parse
from kayopy.__init__ import VERSION

SITE = "https://kayoanime.com/"
SITE_SEARCH = "https://kayoanime.com/?s="

UNSPECIFIED = object()


def search(url):
    url = SITE_SEARCH + urllib.parse.quote(url)
    links = ParseSite(url, "search").get("dow_link")
    for times, link in enumerate(links):
        print(f"{times + 1}) {link[0]}")
    if len(links) == 0:
        return
    vstup = input("Select anime > ")
    if vstup.isnumeric():
        links = ParseSite(links[int(vstup) - 1][1]).get("dow_link")
        if len(links) == 1:
            print(links[0].text)
            dow_link = links[0]["href"]
            vstup = input(
                f"You will be transferred to '{dow_link}'. Continue? (Y/n) > "
            )
            if vstup in ["", "Y", "y"]:
                webbrowser.open(dow_link)
        elif len(links[0]) == 1:
            for times, link in enumerate(links):
                print(f"{times + 1}) {link.text}")
            vstup = input("Select anime > ")
            if vstup.isnumeric():
                dow_link = transfer_to_page(links, vstup, "href")
        else:
            for times, link in enumerate(links):
                print(f"{times + 1}) {link[0]}")
            vstup = input("Select anime > ")
            if vstup.isnumeric():
                dow_link = transfer_to_page(links, vstup, 1)
        with contextlib.suppress(NameError):
            if args.AutoDownload is None:
                vstup = input("Do you want to download content of folder? (Y/n) > ")
                if vstup in ["", "Y", "y"]:
                    html_parser = BeautifulSoup(
                        requests.get(dow_link).text, "html.parser"
                    )
                    title = html_parser.title.text.split("–")[0][:-1]
                    if args.OutputFolder is None or args.OutputFolder is UNSPECIFIED:
                        gdown.download_folder(
                            id=dow_link.split("\\")[-1],
                            output=filedialog.askdirectory() + "\\" + title,
                            quiet=False,
                            remaining_ok=True,
                        )
                    else:
                        gdown.download_folder(
                            id=dow_link.split("\\")[-1],
                            output=f"{args.OutputFolder}/{title}",
                            quiet=False,
                            remaining_ok=True,
                        )


def transfer_to_page(links, vstup, arg2):
    result = links[int(vstup) - 1][arg2]
    vstup = input(f"You will be transferred to '{result}'. Continue? (Y/n) > ")
    if vstup in ["", "Y", "y"]:
        webbrowser.open(result)
    return result


class ParseSite:
    def __init__(self, url, type=None):
        print(f"Parsing site {url} ...", end="\r")
        self.url = url
        self.instance = requests.get(self.url)
        self.parser = BeautifulSoup(self.instance.text, "html.parser")
        self.title = self.parser.title.text
        div = self.title.split(" ")
        top = False
        missing = False
        __list = False
        anime = False
        year = False
        season = False
        for element in div:
            element = element.lower()
            if element == "":
                continue
            if element == "top":
                top = True
            elif element in ["missing", "requested"]:
                missing = True
            elif element == "list":
                __list = True
            elif element == "anime":
                anime = True
            elif element[0] == "(":
                element = element[1:]
                if element.isnumeric():
                    year = True
            elif element[-1] == ")":
                element = element[:-1]
                if element.isnumeric():
                    year = True
            elif element.lower() in ["spring", "summer", "winter", "autumn"]:
                season = True
        loop = [top, missing, __list, anime, year, season]
        a = sum(bool(i) for i in loop)
        self.type = "list" if a >= 4 else "casual"
        if type is not None:
            self.type = type
        print(f"Parsing site {url} DONE")

    def __str__(self) -> str:
        return self.instance.text

    def get(self, __name: str) -> any:
        if __name != "dow_link":
            return
        if self.type == "casual":
            return self.parser.find_all("a", class_=["shortc-button", "small"])
        elif self.type == "list":
            items = self.parser.find_all("div", class_=["toggle", "tie-sc-close"])
            names = []
            links = []
            for i in items:
                links.append(i.find("a", class_=["shortc-button", "small"])["href"])
                names.append(i.find("h3", class_="toggle-head").text)
            return list(zip(names, links))
        elif self.type == "search":
            div = self.parser.find_all("h2", class_=["post-title"])
            names = [i.find("a").text for i in div]
            links = [i.find("a")["href"] for i in div]
            return list(zip(names, links))


class HomePage:
    def __init__(self, url):
        print(f"Parsing site {url} ...", end="\r")
        self.url = url
        self.instance = requests.get(self.url)
        self.parser = BeautifulSoup(self.instance.text, "html.parser")
        print(f"Parsing site {url} DONE")

    def __str__(self) -> str:
        return self.instance.text

    def get(self, __name: str) -> any:
        if __name == "recommendations":
            return self.parser.find_all("a", class_="all-over-thumb-link")


def main():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("-ad", "--AutoDownload", default=UNSPECIFIED, nargs="?")
    parser.add_argument("-of", "--OutputFolder", default=UNSPECIFIED, nargs="?")
    args = parser.parse_args()

    print(f"KayoPy {VERSION}")
    print(f"Using: '{SITE}'")
    home = HomePage(SITE)

    while True:
        vstup = input("> ")

        if vstup == "grec":
            recomendations = home.get("recommendations")
            for times, item in enumerate(recomendations):
                print(f"{times + 1}) {item['aria-label']}")
            vstup = input("Select anime > ")
            if not vstup.isnumeric():
                continue

            links = ParseSite(recomendations[int(vstup) - 1]["href"]).get("dow_link")
            if len(links) == 1:
                print(links[0].text)
                dow_link = links[0]["href"]
                vstup = input(
                    f"You will be transferred to '{dow_link}'. Continue? (Y/n) > "
                )
                if vstup in ["", "Y", "y"]:
                    webbrowser.open(dow_link)
            elif len(links[0]) == 1:
                for times, link in enumerate(links):
                    print(f"{times + 1}) {link.text}")
                vstup = input("Select anime > ")
                if vstup.isnumeric():
                    dow_link = links[int(vstup) - 1]["href"]
                    vstup = input(
                        f"You will be transferred to '{dow_link}'. Continue? (Y/n) > "
                    )
                    if vstup in ["", "Y", "y"]:
                        webbrowser.open(dow_link)
            else:
                for times, link in enumerate(links):
                    print(f"{times + 1}) {link[0]}")
                vstup = input("Select anime > ")
                if vstup.isnumeric():
                    dow_link = links[int(vstup) - 1][1]
                    vstup = input(
                        f"You will be transferred to '{dow_link}'. Continue? (Y/n) > "
                    )
                    if vstup in ["", "Y", "y"]:
                        webbrowser.open(dow_link)
        elif vstup == "report":
            webbrowser.open("https://kayoanime.com/report-dead-link/")

        elif vstup == "request":
            webbrowser.open("https://kayoanime.com/requested-anime/")

        elif vstup in ["q", "quit"]:
            break
        else:
            search(vstup)


if __name__ == "__main__":
    main()
