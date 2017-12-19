from yahoo_finance import Share
from sp500 import get_sp500_tickers
from pinance import Pinance

import pickle


def get_stock_data(tickers = get_sp500_tickers(), path='pinance_data/{}.pickle', update= False):
    for symbol in tickers:
        if update:
            print("Reading data for ticker " + symbol['ticker'])
            stock = Pinance(symbol['ticker'])
            stock.get_quotes()
            stock.get_news()

            stock_data = stock.quotes_data
            stock_news = stock.news_data

            data = {
                'ticker': symbol['ticker'],
                'data': stock_data,
                'news': stock_news
            }

            write_to_pickle(data, path.format(symbol['ticker']))

        else:
            with open(path.format(symbol['ticker']), 'rb') as handle:
                data = pickle.load(handle)

        yield data


def write_to_pickle(data, filename):
    with open(filename, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def get_estimate_tickers():
    data_gen = get_stock_data()

    # list of tickers with One year price target
    estimate_tickers = [stock_data['data']['ticker'] for stock_data in data_gen if 'OneyrTargetPrice' in stock_data['data']]
    return estimate_tickers

