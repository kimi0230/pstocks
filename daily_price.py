import datetime
import time
import requests
from io import StringIO
import pandas as pd
import numpy as np
import csv
import os
import json
import re


def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def crawl_price(date):
    filepath = os.path.join("raw_data", "MI_INDEX_ALL_" +
                            date.strftime("%Y%m%d")+".csv")
    print(filepath)
    if not os.path.isfile(filepath):  # 如果檔案不存在就建立檔案
        url = 'http://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date=' + \
            str(date).split(' ')[0].replace('-', '') + '&type=ALL'
        print("URL :", url)

        res = requests.post(url)
        if res.status_code != 200:
            raise Exception('error code != 200')

        jdata = json.loads(res.text)  # json解析
        if jdata["stat"] != "OK":
            raise Exception('stat != OK')

        outputfile = open(filepath, 'a', newline='',
                          encoding='utf-8')  # 開啟儲存檔案
        print("------ Ddownload File ------")
        outputwriter = csv.writer(outputfile)  # 以csv格式寫入檔案
        outputwriter.writerow(jdata['fields9'])
        for dataline in (jdata['data9']):  # 逐月寫入資料
            dataline[9] = remove_html_tags(dataline[9])
            outputwriter.writerow(dataline)

        # 偽停頓
        time.sleep(5)

    pdstock = pd.read_csv(filepath, encoding='utf-8')  # 以pandas讀取檔案
    pdstock = pdstock.set_index('證券代號')
    pdstock['成交金額'] = pdstock['成交金額'].str.replace(',', '')
    pdstock['成交股數'] = pdstock['成交股數'].str.replace(',', '')

    return pdstock


def Nday(n_days=3):
    data = {}
    date = datetime.datetime.now()

    # TODO: 待優化
    while len(data) < n_days:
        print('parsing', date)
        # 使用 crawPrice 爬資料
        try:
            # 抓資料
            data[date.date()] = crawl_price(date)
            print('success!')
        except:
            # 爬不到 往前找一天
            print('holiday')
            date -= datetime.timedelta(days=1)
            time.sleep(10)
            continue

        # 減一天
        date -= datetime.timedelta(days=1)
        time.sleep(10)

    close = pd.DataFrame({k: d['收盤價'] for k, d in data.items()}).transpose()
    close.index = pd.to_datetime(close.index)

    openPrice = pd.DataFrame({k: d['開盤價']
                             for k, d in data.items()}).transpose()
    openPrice.index = pd.to_datetime(openPrice.index)

    high = pd.DataFrame({k: d['最高價'] for k, d in data.items()}).transpose()
    high.index = pd.to_datetime(high.index)

    low = pd.DataFrame({k: d['最低價'] for k, d in data.items()}).transpose()
    low.index = pd.to_datetime(low.index)

    volume = pd.DataFrame({k: d['成交股數'] for k, d in data.items()}).transpose()
    volume.index = pd.to_datetime(volume.index)

    tsmc = {
        'close': close['2330']['2021'].dropna().astype(float),
        'open': openPrice['2330']['2021'].dropna().astype(float),
        'high': high['2330']['2021'].dropna().astype(float),
        'low': low['2330']['2021'].dropna().astype(float),
        'volume': volume['2330']['2021'].dropna().astype(float),
    }
    print(tsmc['open'])
    tsmc['open'].plot()


if __name__ == "__main__":
    # print(remove_html_tags("元大台灣50正2"))
    # crawl_price(datetime.date.fromisoformat("2021-06-18"))
    Nday(3)
