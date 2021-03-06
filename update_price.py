import re
import csv
import requests
import time
import datetime
import webbrowser
from collections import namedtuple
from typing import *
import sys

FundInfo = namedtuple('FundInfo', 'query_code, query_type, update_code')
PriceInfo = namedtuple('PriceInfo', 'update_code, price')


def extract_fund_info() -> List[FundInfo]:
    fund_info_list = []
    with open('./fund_code.csv', 'r') as f:
        content = csv.reader(f)
        for row in content:
            if len(row) == 3:
                query_code, query_type, update_code = row
                fund_info_list.append(FundInfo(query_code, query_type, update_code))
            else:
                continue
    return fund_info_list


def add_fund(input_str: str) -> None:
    with open('./fund_code.csv', 'a+') as f:
        writer = csv.writer(f)
        writer.writerow(input_str.split(','))


def get_query_date(fund_type: str) -> str:
    if fund_type == 'OF':
        query_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    else:
        weekday = datetime.date.today().weekday()
        if weekday == 5:
            day_shift = 2
        elif weekday == 6:
            day_shift = 3
        elif weekday == 0:
            day_shift = 3
        else:
            day_shift = 1
        query_date = (datetime.date.today() - datetime.timedelta(days=day_shift)).strftime('%Y-%m-%d')
    return query_date


def get_latest_price(fund_code: str, start_time: str, end_time: str) -> str:
    url = f'https://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={fund_code}&page=1&per=20&sdate={start_time}&edate={end_time}'
    resp = requests.get(url, timeout=30)
    extracted_price = re.findall(r'(\d+\.\d+)</td>', resp.text)
    return extracted_price[0] if extracted_price else '-1'


def generate_update_info(fund_info: FundInfo) -> PriceInfo:
    query_code, query_type, update_code = fund_info
    query_date = get_query_date(query_type)
    latest_price = get_latest_price(query_code, query_date, query_date)
    if latest_price == '-1':
        return PriceInfo(update_code, '-1')
    return PriceInfo(update_code, latest_price)


def generate_moneywiz_url(price_info: PriceInfo) -> None:
    url = f'moneywiz://updateholding?symbol={price_info.update_code}&price={price_info.price}'
    webbrowser.open(url, new=0, autoraise=True)


def main() -> None:
    fund_list = extract_fund_info()
    price_info = []
    for fund in fund_list:
        price_info.append(generate_update_info(fund))
    for price in price_info:
        if price.price == '-1':
            continue
        generate_moneywiz_url(price)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'add':
        add_fund(sys.argv[2])
    else:
        main()
