from bs4 import BeautifulSoup
import requests
import webbrowser

VERSION = '1.0.0'
AUTHOR = 'GrenManSK'

SITE = 'https://kayoanime.com/'
SITE_SEARCH = 'https://kayoanime.com/?s='


class ParseSite:
    def __init__(self, url):
        self.url = url
        self.instance = requests.get(self.url)
        self.parser = BeautifulSoup(self.instance.text, 'html.parser')
        self.title = self.parser.title.text
        print(self.title)
        div = self.title.split(' ')
        top = False
        missing = False
        __list = False
        anime = False
        year = False
        season = False
        for element in div:
            element = element.lower()
            if element == 'top':
                top = True
            elif element == 'missing':
                missing = True
            elif element == 'list':
                __list = True
            elif element == 'anime':
                anime = True
            elif element[0] == '(':
                element = element[1:]
                if element.isnumeric():
                    year = True
                if element.lower() in ['spring', 'summer', 'winter', 'autumn']:
                    season = True
            elif element[-1] == ')':
                element = element[:-1]
                if element.isnumeric():
                    year = True
                if element.lower() in ['spring', 'summer', 'winter', 'autumn']:
                    season = True
        loop = [top, missing, __list, anime, year, season]
        a = 0
        for i in loop:
            if i:
                a += 1
        if a >= 4:
            self.type = 'list'
        else:
            self.type = 'casual'

    def __str__(self) -> str:
        return self.instance.text

    def get(self, __name: str) -> any:
        if __name == 'dow_link':
            if self.type == 'casual':
                items = self.parser.find_all(
                    'a', class_=['shortc-button', 'small'])
                return items
            elif self.type == 'list':
                items = self.parser.find_all(
                    'div', class_=['toggle', 'tie-sc-close'])
                names = []
                links = []
                for i in items:
                    links.append(
                        i.find('a', class_=['shortc-button', 'small'])['href'])
                    names.append(i.find('h3', class_='toggle-head').text)
                print(list(zip(names, links)))
                return list(zip(names, links))


class HomePage:
    def __init__(self, url):
        self.url = url
        self.instance = requests.get(self.url)
        self.parser = BeautifulSoup(self.instance.text, 'html.parser')

    def __str__(self) -> str:
        return self.instance.text

    def get(self, __name: str) -> any:
        if __name == 'recommendations':
            items = self.parser.find_all('a', class_='all-over-thumb-link')
            return items


def main():
    print(f'KayoPy {VERSION}')
    print(f'Using: \'{SITE}\'')
    home = HomePage(SITE)

    while True:
        vstup = input('> ')

        if vstup == 'grec':
            recomendations = home.get('recommendations')
            for times, item in enumerate(recomendations):
                print(f"{times + 1}) {item['aria-label']}")
            vstup = input('Select anime > ')
            if vstup.isnumeric():
                links = ParseSite(
                    recomendations[int(vstup) - 1]['href']).get('dow_link')
                if len(links) == 1:
                    print(links[0].text)
                    dow_link = links[0]['href']
                    vstup = input(
                        f'You will be transferred to \'{dow_link}\'. Continue? (Y/n) > ')
                    if vstup in ['', 'Y', 'y']:
                        webbrowser.open(dow_link)
                else:
                    if len(links[0]) == 1:
                        for times, link in enumerate(links):
                            print(f"{times + 1}) {link.text}")
                        vstup = input('Select anime > ')
                        if vstup.isnumeric():
                            dow_link = links[int(vstup) - 1]['href']
                            vstup = input(f'You will be transferred to \'{dow_link}\'. Continue? (Y/n) > ')
                            if vstup in ['', 'Y', 'y']:
                                webbrowser.open(dow_link)
                    else:
                        for times, link in enumerate(links):
                            print(f"{times + 1}) {link[0]}")
                        vstup = input('Select anime > ')
                        if vstup.isnumeric():
                            dow_link = links[int(vstup) - 1][1]
                            vstup = input(f'You will be transferred to \'{dow_link}\'. Continue? (Y/n) > ')
                            if vstup in ['', 'Y', 'y']:
                                webbrowser.open(dow_link)
            else:
                continue

        if vstup in ['q', 'quit']:
            break


if __name__ == '__main__':
    main()
