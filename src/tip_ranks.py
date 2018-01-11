from sp500 import get_sp500_tickers
from dateutil.parser import *
from datetime import timedelta
from datetime import datetime
from flask import Flask, render_template

import requests
import json
import statistics
import pickle


def write_to_pickle(ticker, data):
    filename = "tipranks_data/{}.pickle".format(ticker)
    with open(filename, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def read_from_pickle(ticker):
    path = "tipranks_data/{}.pickle".format(ticker)
    try:
        with open(path.format(ticker), 'rb') as handle:
            data = pickle.load(handle)

        return data

    except FileNotFoundError:
        print("File '{}' not found.".format(path))
        return None


def company_data_gen(tickers, update=False, to_date=datetime.today(), date_range=90):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
    }

    rel_st_dev = lambda price_list: (statistics.stdev(price_list) / statistics.mean(price_list)) * 100

    for ticker in tickers:
        ticker = ticker['ticker']
        # todo
        if not update:
            data = read_from_pickle(ticker)

        path = "https://www.tipranks.com/api/stocks/getData//?name={}".format(ticker)
        print("Retrieving data from : '{}'".format(path))

        try:
            resp = requests.get(path, headers=headers)
            data = json.loads(resp.text)
            print("Data loaded. Retrieving Expert Price Target")

            # retrieve only reviews within the last 90 days
            from_date = to_date - timedelta(days=date_range)

            # expert price target
            expert_price_targets = [
                {
                    "expert": expert['name'],
                    "rating": expert['rankings'][0]['stars'],
                    "priceTarget": rating['priceTarget'],
                    "date": parse(rating['time'])
                }
                for expert in data['experts']
                for rating in expert['ratings']
                if rating['priceTarget'] is not None and from_date < parse(rating['time']) < to_date
            ]

            price_targets = [priceTarget['priceTarget'] for priceTarget in expert_price_targets]
            last_price = data['prices'][len(data['prices']) - 1]['p']

            company_data = {
                'ticker': data['ticker'],
                'sector': ticker['gics_sector'],
                'sub_sector': ticker['gics_sub_sector'],
                'market': data['market'],
                'description': data['description'],
                'hasDividends': data['hasDividends'],
                'lastPrice': last_price,
                'expertPriceTarget': expert_price_targets,
                'meanPriceTarget': statistics.mean(price_targets),
                'stdDevPriceTargets': statistics.stdev(price_targets),
                'relStdDevPriceTargets': rel_st_dev(price_targets),
                'averageExpectedPercChange': float((statistics.mean(price_targets) - last_price) / last_price) * 100,
                'peRatio': get_pe_ratio(ticker['ticker'])
            }

            yield company_data

        except:
            print("Connection Error with Ticker {}".format(ticker))


# path = f"https://www.tipranks.com/api/stocks/getNewsSentiments/?ticker={ticker}"
# path = f"https://www.tipranks.com/api/stocks/getNews/?ticker={ticker}"


def get_forward_pe_ratio(ticker):
    """
        Stock Price / Future Earnings Per Share
    :param ticker:
    :return: forward PE Ratio
    """

    from pinance import Pinance
    pinance_data = Pinance(ticker)
    pinance_data.get_quotes()
    pinance_data.quotes_data['forwardPE']


def get_trailing_pe_ratio(ticker):
    """
    Stock Price
    :param ticker:
    :return:
    """

def get_company_price_changes(ticker, from_date, to_date):
    import pandas_datareader.data as web
    f = web.DataReader("F", 'google', from_date, to_date)
    # todo


def update_data(tickers, to_date=datetime.today()):
    print("tickers retrieved.")

    for company_data in company_data_gen(tickers, update=True, to_date=to_date):
        write_to_pickle(company_data['ticker'], company_data)


def retrieve_data(tickers=get_sp500_tickers(), update=False, to_date=datetime.today()):
    if update:
        update_data(tickers, to_date=to_date)

    for ticker in tickers:
        data = read_from_pickle(ticker['ticker'])
        if data is not None:
            yield data


def tickers_where_none(tickers=get_sp500_tickers()):
    for ticker in tickers:
        data = read_from_pickle(ticker)
        if data is None:
            yield ticker


def get_data_list(update=False, to_date=datetime.today()):
    sp500_data = []

    for company in retrieve_data(update=update, to_date=to_date):
        sp500_data.append(company)

    sp500_data.sort(key=lambda k: k['averageExpectedPercChange'])
    # we care about most profitable first!
    sp500_data.reverse()

    return sp500_data


