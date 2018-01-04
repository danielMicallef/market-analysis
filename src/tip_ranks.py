from sp500 import get_sp500_tickers
from dateutil.parser import *
from datetime import timedelta
from datetime import datetime

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


def company_data_gen(tickers, update=False, to_date= datetime.today(), date_range = 90):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
    }

    rel_st_dev = lambda price_list: (statistics.stdev(price_list) / statistics.mean(price_list)) * 100

    for ticker in tickers:
        ticker = ticker['ticker']
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
                    "date":parse(rating['time'])
                }
                for expert in data['experts']
                for rating in expert['ratings']
                if rating['priceTarget'] is not None and
                   from_date < parse(rating['time']) < to_date
            ]

            price_targets = [priceTarget['priceTarget'] for priceTarget in expert_price_targets]
            last_price = data['prices'][len(data['prices'])-1]['p']

            company_data = {
                'ticker': data['ticker'],
                'market': data['market'],
                'description': data['description'],
                'hasDividends': data['hasDividends'],
                'lastPrice': last_price,
                'expertPriceTarget': expert_price_targets,
                'meanPriceTarget': statistics.mean(price_targets),
                'stdDevPriceTargets':  statistics.stdev(price_targets),
                'relStdDevPriceTargets': rel_st_dev(price_targets),
                'averageExpectedPercChange': float((statistics.mean(price_targets) - last_price)/last_price) * 100
            }

            yield company_data
        except :
            print("Connection Error with Ticker {}".format(ticker))


# path = f"https://www.tipranks.com/api/stocks/getNewsSentiments/?ticker={ticker}"
# path = f"https://www.tipranks.com/api/stocks/getNews/?ticker={ticker}"


def get_company_price_changes(ticker, from_date, to_date):
    import pandas_datareader.data as web
    f = web.DataReader("F", 'google', from_date, to_date)

def update_data(tickers):
    print("tickers retrieved.")

    for company_data in company_data_gen(tickers, update=True):
        write_to_pickle(company_data['ticker'], company_data)


def retrieve_data(tickers = get_sp500_tickers(), update=False):
    if update:
        update_data(tickers)

    for ticker in tickers:
        data = read_from_pickle(ticker['ticker'])
        if data is not None:
            yield data

def test_data(update = False):
    sp500_data = []

    for company in retrieve_data(update= update):
        sp500_data.append(company)

    sp500_data.sort(key=lambda k: k['averageExpectedPercChange'])

# update_data()

    for company in sp500_data[:10]:
       print("Company: " + company['ticker']+" Rel Std Dev: " + company['relStdDevPriceTargets'] + " Avg Expected Perc Change " + company['averageExpectedPercChange'])

company_gen = company_data_gen(get_sp500_tickers())
next(company_gen)