import contextlib
from bs4 import BeautifulSoup
import requests
import webbrowser
import argparse
import gdown
from tkinter import filedialog
import urllib.parse
import os
import glob
import shutil
from tqdm import tqdm

try:
    from kayopy.__init__ import VERSION
except ImportError:
    VERSION = "UNEXPECTED ERROR"

SITE = "https://kayoanime.com/"
SITE_SEARCH = "https://kayoanime.com/?s="

UNSPECIFIED = object()


def get_directory_size(path="."):
    total_size = 0
    for dirpath, _dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size


def move_with_progress(source, destination):
    if not os.path.exists(source):
        print(f"Source directory '{source}' does not exist.")
        return

    os.makedirs(destination, exist_ok=True)

    files_to_move = [
        f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))
    ]

    total_size = get_directory_size(source)

    progress_bar = tqdm(
        total=total_size, unit="B", unit_scale=True, desc="Moving Files"
    )

    for file_name in files_to_move:
        source_file_path = os.path.join(source, file_name)
        destination_file_path = os.path.join(destination, file_name)

        try:
            shutil.move(source_file_path, destination_file_path)
        except Exception as e:
            print(f"Error moving file '{file_name}': {e}")
        finally:
            progress_bar.update(os.path.getsize(destination_file_path))

    progress_bar.close()


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
                    title = (
                        html_parser.title.text.split("–")[0][:-1]
                        .replace(":", "")
                        .replace("!", "")
                        .replace("\\", "")
                        .replace("/", "")
                        .replace("@", "")
                    )
                    if args.OutputFolder is None or args.OutputFolder is UNSPECIFIED:
                        where_base = filedialog.askdirectory()
                        where = where_base + "\\" + title
                        sess = gdown._get_session(False, False, "/")
                        try:
                            (
                                return_code,
                                gdrive_file,
                            ) = gdown._download_and_parse_google_drive_link(
                                sess,
                                dow_link,
                            )
                        except RuntimeError:
                            os.system(f"start firefox {dow_link}")
                            return
                        directory_structure = gdown._get_directory_structure(
                            gdrive_file, os.getcwd()
                        )
                        for link in directory_structure:
                            try:
                                filename = gdown.download(
                                    url=f"https://drive.google.com/uc?id={link[0]}"
                                )
                            except gdown.exceptions.FileURLRetrievalError:
                                filename = None
                            if filename is None:
                                before = glob.glob("C:\\Users\\richard\\Downloads\\*")
                                input("You will now download download files as zip")
                                os.system(f"start firefox {dow_link}")
                                input("Wait after u download fully zip and extract it")
                                after = glob.glob("C:\\Users\\richard\\Downloads\\*")
                                now = [i for i in after if i not in before]
                                move_with_progress(
                                    now[0], f"{where_base}/{os.path.basename(now[0])}"
                                )
                                os.rmdir(now[0])
                                break
                            else:
                                os.makedirs(where, exist_ok=True)
                                shutil.move(filename, f"{where}\\{filename}")
                        # gdown.download_folder(
                        #     id=dow_link.split("\\")[-1],
                        #     output=where,
                        #     quiet=False,
                        #     remaining_ok=True,
                        # )


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

    while True:
        vstup = input("> ")
        if vstup in ["q", "quit"]:
            break
        elif vstup == "" or len(vstup) <= 1:
            continue
        elif vstup == "grec":
            home = HomePage(SITE)
            recommendations = home.get("recommendations")
            for times, item in enumerate(recommendations):
                print(f"{times + 1}) {item['aria-label']}")
            vstup = input("Select anime > ")
            if not vstup.isnumeric():
                continue
            links = ParseSite(recommendations[int(vstup) - 1]["href"]).get("dow_link")
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
            with contextlib.suppress(NameError):
                if args.AutoDownload is None:
                    vstup = input("Do you want to download content of folder? (Y/n) > ")
                    if vstup in ["", "Y", "y"]:
                        html_parser = BeautifulSoup(
                            requests.get(dow_link).text, "html.parser"
                        )
                        title = (
                            html_parser.title.text.split("–")[0][:-1]
                            .replace(":", "")
                            .replace("!", "")
                            .replace("\\", "")
                            .replace("/", "")
                            .replace("@", "")
                        )
                        if args.OutputFolder is None or args.OutputFolder is UNSPECIFIED:
                            where_base = filedialog.askdirectory()
                            where = where_base + "\\" + title
                            sess = gdown._get_session(False, False, "/")
                            try:
                                (
                                    return_code,
                                    gdrive_file,
                                ) = gdown._download_and_parse_google_drive_link(
                                    sess,
                                    dow_link,
                                )
                            except RuntimeError:
                                os.system(f"start firefox {dow_link}")
                                return
                            directory_structure = gdown._get_directory_structure(
                                gdrive_file, os.getcwd()
                            )
                            for link in directory_structure:
                                try:
                                    filename = gdown.download(
                                        url=f"https://drive.google.com/uc?id={link[0]}"
                                    )
                                except gdown.exceptions.FileURLRetrievalError:
                                    filename = None
                                if filename is None:
                                    before = glob.glob("C:\\Users\\richard\\Downloads\\*")
                                    input("You will now download download files as zip")
                                    os.system(f"start firefox {dow_link}")
                                    input("Wait after u download fully zip and extract it")
                                    after = glob.glob("C:\\Users\\richard\\Downloads\\*")
                                    now = [i for i in after if i not in before]
                                    move_with_progress(
                                        now[0], f"{where_base}/{os.path.basename(now[0])}"
                                    )
                                    os.rmdir(now[0])
                                    break
                                else:
                                    os.makedirs(where, exist_ok=True)
                                    shutil.move(filename, f"{where}\\{filename}")
                            # gdown.download_folder(
                            #     id=dow_link.split("\\")[-1],
                            #     output=where,
                            #     quiet=False,
                            #     remaining_ok=True,
                            # )
        elif vstup == "report":
            webbrowser.open("https://kayoanime.com/report-dead-link/")

        elif vstup == "request":
            webbrowser.open("https://kayoanime.com/requested-anime/")

        else:
            search(vstup)


if __name__ == "__main__":
    main()
