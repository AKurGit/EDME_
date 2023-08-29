import re
from selenium import webdriver
from bs4 import BeautifulSoup
from typing import List,  Tuple,  Dict


class ParsBank:

    @staticmethod
    def get_links(url: str, teg: str, class_name: str) -> List:
        driver = webdriver.Chrome()
        driver.get(url)
        page = driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        links = soup.find_all(teg, class_=class_name)
        links = list(map(lambda x: x.get('href'), links))
        url = re.findall(r'//[a-z, A-Z,., 1-9]+/', url)[0]
        url = url[2:len(url) - 1]
        links = list(map(lambda x: 'https://' + url + x, links))
        return links

    @staticmethod
    def pars_credits() -> Dict[str, Tuple[str, str]]:
        information = {}
        links = ParsBank.get_links('https://www.belveb.by/credits/', 'a', 'card-list-line__item-link')
        for url in links:
            driver = webdriver.Chrome()
            driver.get(url)
            page = driver.page_source
            soup = BeautifulSoup(page, 'lxml')
            buf1 = soup.find_all('div', class_='cards-deposit__text')
            buf1 = list(map(lambda x: x.text, buf1))
            buf2 = soup.find_all('div', class_='h2')
            buf2 = list(map(lambda x: x.text, buf2))
            text = ''.join([j + ' ' + i + ' ' for i, j in zip(buf2, buf1)])
            name = soup.find('h1', class_='hero-block__title h1 flc').text
            information[name] = (url, text)

        return information

    @staticmethod
    def get_atm_machine() -> List:
        url = 'https://www.mtbank.by/offices/'
        driver = webdriver.Chrome()
        driver.get(url)
        page = driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        atm_machine = list(map(lambda x: x.text.strip(), soup.find_all('span', class_='map-object__location')))
        atm_machine = list(filter(lambda x: True if x[:2] == 'г.' else False, atm_machine))
        return atm_machine

    @staticmethod
    def cards() -> Dict[str, Tuple[str, str]]:
        links = ParsBank.get_links('https://belgazprombank.by/personal_banking/plastikovie_karti/raschetnie_karti/',
                                  'a', 'btn btn-default btn-sm')

        url = 'https://belgazprombank.by/personal_banking/plastikovie_karti/raschetnie_karti/'
        driver = webdriver.Chrome()
        driver.get(url)
        page = driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        card_names = soup.find_all('div', class_='card__title')
        card_names = list(map(lambda x: x.text, card_names))
        cards = {}
        for url, card_name in zip(links, card_names):
            driver = webdriver.Chrome()
            driver.get(url)
            page = driver.page_source
            soup = BeautifulSoup(page, 'lxml')
            description = soup.find_all('div', class_='main-adv__text')
            description = list(map(lambda x: x.text, description))
            description = list(map(lambda x: x.strip(), description))
            descr = ''.join(description)
            cards[card_name] = (url, descr)
        return cards

    @staticmethod
    def deposits() -> Dict[str, Tuple[str, str]]:
        information = {}
        links = ParsBank.get_links('https://www.belveb.by/deposits/', 'a', 'card-list-line__item-link')
        for url in links:
            driver = webdriver.Chrome()
            driver.get(url)
            page = driver.page_source
            soup = BeautifulSoup(page, 'lxml')
            buf1 = soup.find_all('div', class_='cards-deposit__text')
            buf1 = list(map(lambda x: x.text, buf1))
            buf2 = soup.find_all('div', class_='h2')
            buf2 = list(map(lambda x: x.text, buf2))
            descr = ''.join([j + ' ' + i + ' ' for i, j in zip(buf2, buf1)])
            name = soup.find('h1', class_='hero-block__title h1 flc').text
            information[name] = (url, descr)

        return information

    @staticmethod
    def exchange_rate() -> Dict:
        url = 'https://myfin.by/currency/minsk'
        driver = webdriver.Chrome()
        driver.get(url)
        page = driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        res = {'USD_BUY': 0,
               'USD_SELL': 0,
               'EUR_BUY': 0,
               'EUR_SELL': 0,
               'RUB_BUY': 0,
               'RUB_SELL': 0,
               }
        buf = soup.find_all('td', class_='currencies-courses__currency-cell')
        buf = list(map(lambda x: x.text, buf))
        for name, value in zip(res.keys(), buf):
            res[name] = value

        return res

    @staticmethod
    def insurance() -> Dict[str, Tuple[str, str]]:
        url = 'https://www.belveb.by/insurance/'
        links = ParsBank.get_links(url, 'a', 'slide-top__link')
        res = {}
        for url in links:
            driver = webdriver.Chrome()
            driver.get(url)
            page = driver.page_source
            soup = BeautifulSoup(page, 'lxml')
            buf = soup.find('h1', class_='hero-block__title h1 flc').text
            buf1 = soup.find_all('div', class_='cards-deposit__text')
            buf1 = list(map(lambda x: x.text, buf1))
            buf2 = soup.find_all('div', class_='h2')
            buf2 = list(map(lambda x: x.text, buf2))
            descr = ''.join([j + ' ' + i + ' ' for i, j in zip(buf2, buf1)])
            res[buf] = (url, descr)

        return res

    @staticmethod
    def money_transfers() -> List:
        url = 'https://belarusbank.by/ru/fizicheskim_licam/cards/uslugi/10908'
        driver = webdriver.Chrome()
        driver.get(url)
        page = driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        a = soup.find_all('h4', class_='accordion__bar js-accordion__btn')
        a = list(map(lambda x: x.text, a))
        b = soup.find_all('div', class_='js-accordion__body accordion__body text-guide table-scroller midiTable')
        b = list(map(lambda x: x.findNext('a').get('href'), b))

        return list(zip(a, b))

    @staticmethod
    def bank_account() -> Dict[str, Tuple[str, str]]:
        information = {}
        links = ['https://www.alfabank.by/business/small/rko/join/', 'https://www.alfabank.by/business/small/rko/start/', 'https://www.alfabank.by/business/small/rko/for-business/']
        for url in links:
            driver = webdriver.Chrome()
            driver.get(url)
            page = driver.page_source
            soup = BeautifulSoup(page, 'lxml')
            name = soup.find('h1', class_='page-top-section__title h0').text
            buf = soup.find('ul', class_='benefits-classic__list dashed-list')
            description = buf.find_all('li')
            description = list(map(lambda x: x.text + ' ', description))
            description = ''.join(description)
            information[name] = (url, description)

        return information


# print(ParsBank.insurance())
# print(ParsBank.exchange_rate())
# print(ParsBank.deposits())
# print(ParsBank.cards())
# print(ParsBank.get_atm_machine())
# print(ParsBank.pars_credits())
# print(ParsBank.bank_account())
# print(ParsBank.money_transfers())
