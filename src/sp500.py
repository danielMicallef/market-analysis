import os, requests, pickle
import bs4 as bs
import unittest


def get_sp500_tickers(update_sp500 = False):
    """

    Retrieve Ticker Generic Data. This retrieves the relevant Wikipedia page and parses a table
    containing all the SP500 Tickers. This method may fail if the Wiki page is altered.

    :param update_sp500: retrieve from Pickle or update from Wikipedia
    :return:

    """

    ticker_filename = 'tickers.pickle'
    if not os.path.isfile(ticker_filename) or update_sp500:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
        }
        resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
                            headers=headers)
        soup = bs.BeautifulSoup(resp.text)
        wiki_table = soup.find('table', {'class': 'wikitable sortable'})

        tickers = parse_sp500O_tickers_table(wiki_table)

        # write tickers to pickle
        with open(ticker_filename, 'wb') as handle:
            pickle.dump(tickers, handle, protocol=pickle.HIGHEST_PROTOCOL)

    else:
        # read tickers from pickle
        with open(ticker_filename, 'rb') as handle:
            tickers = pickle.load(handle)

    return tickers


def gen_tickers(tickers = get_sp500_tickers()):
    for ticker in tickers:
        yield ticker


def parse_sp500O_tickers_table(wiki_table):
    tickers = []

    for row in wiki_table.findAll('tr')[1:]:
        ticker_info = {}
        ticker_info['ticker'] = row.findAll('td')[0].text
        ticker_info['gics_sector'] = row.findAll('td')[3].text
        ticker_info['gics_sub_sector'] = row.findAll('td')[4].text

        tickers.append(ticker_info)

    return tickers


def get_sector(required_ticker, tickers = get_sp500_tickers()):
    """
    Get Sector of Ticker

    :param required_ticker: Company Ticker Name
    :param tickers: list of tickers - defaulting to list retrieved from get_sp500_tickers()

    :return: sector of the company

    """

    for ticker in tickers:
        if ticker['ticker'] == required_ticker:
            return ticker['gics_sector']


def get_sub_industry(required_ticker, tickers = get_sp500_tickers()):
    """
    Get sub-industry of company

    :param required_ticker: Company Ticker Name
    :param tickers: list of tickers - defaulting to list retrieved from get_sp500_tickers()
    :return: sub-industry of company
    """

    for ticker in tickers:
        if ticker['ticker'] == required_ticker:
            return ticker['gics_sub_sector']


class TestGetTickers(unittest.TestCase):
    def test_get_tickers(self):
        tickers = get_sp500_tickers()