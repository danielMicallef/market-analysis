# File for retrieval of FTSE-100 Tickers from Wikipedia Page

import os, requests, pickle
import bs4 as bs
import unittest

def get_ftse100_tickers(update_ftse=False):
    """

    Retrieve list of tickers together with relevant data from the FTSE 100 Index Wiki Page.

    :param update: Unless set to True, the function will try to avoid parsing the Wiki Page, and will instead retrieve
                   locally saved data.
    :return: List of Tickers

    """

    ticker_filename = 'tickers_ftse.pickle'
    if not os.path.isfile(ticker_filename) or update_ftse:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
        }
        url = 'http://en.wikipedia.org/wiki/FTSE_100_Index'
        resp = requests.get(url=url,
                            headers=headers)

        # if not status code ok raise exception.
        if resp.status_code is not 200:
            exception = "{} status returned when trying to retrieve Wiki page.\n" \
                        "Url used is '{}'".format(resp.status_code, url)
            raise Exception(exception)

        # Status is ok. Parse and return tickers.
        soup = bs.BeautifulSoup(resp.text)
        wiki_table = soup.find('table', {'class': 'wikitable sortable'})

        ticker_list = []
        for ticker in parse_ftse100_tickers_table(wiki_table):
            ticker_list.append(ticker)

        # write tickers to pickle
        with open(ticker_filename, 'wb') as handle:
            pickle.dump(ticker_list, handle, protocol=pickle.HIGHEST_PROTOCOL)

    else:
        # read tickers from pickle
        with open(ticker_filename, 'rb') as handle:
            ticker_list = pickle.load(handle)

    return ticker_list


def parse_ftse100_tickers_table(wiki_table):
    for row in wiki_table.findAll('tr')[1:]:
        ticker_info = {
            'company': row.findAll('td')[0].text,
            'ticker': row.findAll('td')[1].text,
            'ftse_sector': row.findAll('td')[2].text
        }

        yield ticker_info


def get_ftse_sector(required_ticker, tickers = get_ftse100_tickers()):
    """
    Get sector of ticker.

    :param required_ticker: Company Ticker Name
    :param tickers: list of tickers

    :return: sector of company - as per wiki page.
    """

    return search(tickers, 'ticker', required_ticker)['ftse_sector']


def search(list, key, value):
    for item in list:
        if item[key] == value:
            return item

class TestFtseTickers(unittest.TestCase):
    def setUp(self):
        pass

    def test_search_PositiveTest_DictionaryItem(self):
        test_list = [{'a':n, 'b': 2*n, 'c': 3*n}  for n in range(20)]
        item = search(test_list, 'a', 1)
        self.assertEquals(item['a'], 1)

    def test_getFtseSector_NMCTicker_HealthCareSector(self):
        sector = get_ftse_sector('NMC')
        self.assertEquals(sector, "Health Care Equipment & Services")

    def test_parseFtse100TickersTable_tickers(self):
        pass

    def test_get_ftse100_tickers(self):
        pass
