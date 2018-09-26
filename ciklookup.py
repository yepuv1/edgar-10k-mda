import argparse
import codecs
import os
import time
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import xml.dom.minidom
import csv


class ApiError(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "ApiError: status={}".format(self.status)


def get_ticker_metadata(tickers):
    url = "https://csuite.xbrl.us/php/dispatch.php?Task=xbrlCIKLookup&Ticker={0}"
    for ticker in tickers:
        url_i = url.format(ticker)
        msg = 'Fetching {0}...'.format(ticker)

        s = requests.Session()
        resp = s.get(url_i)

        if resp.status_code != 200:
            # This means something went wrong.
            err = 'GET /tasks/ {}'.format(resp.status_code)
            msg = '{0}{1}'.format(msg, err)
            raise ApiError(err)
        print(msg + 'Success.')

        root = ET.fromstring(resp.text)
        tickerLookup = root.find('tickerLookup')
        cik = tickerLookup.find('cik').text
        ticker = tickerLookup.find('ticker').text
        name = tickerLookup.find('name').text
        sic = tickerLookup.find('sic').text
        yield {'ticker': ticker, 'cik': cik, 'company_name': name, 'sic': sic}


def save_cik(ticker_file, cik_filename):
    path, ba_name = os.path.split(ticker_file)
    b_name = os.path.basename(ticker_file)
    b_name_list = b_name.split('.')
    if len(b_name_list) > 1:
        b_name_list = b_name_list[:-1]
    if not cik_filename:
        cik_filename = os.path.join(path, '.'.join(b_name_list) + '_cik.csv')

    df_tickers = pd.read_csv(ticker_file)
    tickers = df_tickers['Symbol'].values
    cik = []
    sic = []
    tik = []
    for meta_data in get_ticker_metadata(tickers):
        tik.append(meta_data['ticker'])
        cik_item = str(meta_data['cik'])
        if cik_item.isnumeric():
            cik.append(cik_item)
        else:
            cik.append(None)
        sic.append(meta_data['sic'])
    df_tickers['cik'] = cik
    df_tickers['sic'] = sic
    df_tickers.to_csv(cik_filename, header=False, index=False, quoting=csv.QUOTE_ALL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("python ciklookup")
    parser.add_argument('ticker_file', type=str, help='File name of the csv file with symbol column name as "Symbol".')
    parser.add_argument('--cik_filename', type=str, help = 'File name of the csv file')
    args = parser.parse_args()
    save_cik(ticker_file=args.ticker_file, cik_filename=args.cik_filename)

