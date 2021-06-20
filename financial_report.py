import pandas as pd
import requests
from io import StringIO
import time
import os
import datetime
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = [u'Arial Unicode MS']  # 設定中文字型
plt.rcParams["axes.unicode_minus"] = False
pd.options.mode.chained_assignment = None  # 取消顯示pandas資料重設警告


def monthly_report(year, month):

    # 假如是西元，轉成民國
    if year > 1990:
        year -= 1911

    url = 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_' + \
        str(year)+'_'+str(month)+'_0.html'
    if year <= 98:
        url = 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_' + \
            str(year)+'_'+str(month)+'.html'

    filepath = os.path.join("raw_data", "t21sc03_" +
                            str(year)+'_'+str(month)+".csv")

    # print(filepath)
    if not os.path.isfile(filepath):
        # 偽瀏覽器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'
        }

        # 下載該年月的網站，並用pandas轉換成 dataframe
        r = requests.get(url, headers=headers)
        r.encoding = 'big5'

        dfs = pd.read_html(StringIO(r.text), encoding='big-5')

        df = pd.concat([df for df in dfs if df.shape[1]
                       <= 11 and df.shape[1] > 5])

        if 'levels' in dir(df.columns):
            df.columns = df.columns.get_level_values(1)
        else:
            df = df[list(range(0, 10))]
            column_index = df.index[(df[0] == '公司代號')][0]
            df.columns = df.iloc[column_index]

        df['當月營收'] = pd.to_numeric(df['當月營收'], 'coerce')
        df = df[~df['當月營收'].isnull()]
        df = df[df['公司代號'] != '合計']

        # 偽停頓
        time.sleep(5)

        df.to_csv(filepath,
                  index=False, header=True)

    df = pd.read_csv(filepath, encoding='utf-8')
    return df


def NMons(n_mons=12):
    data = {}
    n_days = 12
    now = datetime.datetime.now()

    year = now.year
    month = now.month

    filepath = os.path.join("data", "financial_report" +
                            str(year)+'_'+str(month)+".csv")
    if not os.path.isfile(filepath):
        while len(data) < n_days:

            print('parsing', year, month)

            # 使用 crawPrice 爬資料
            try:
                data['%d-%d-01' % (year, month)] = monthly_report(year, month)
            except Exception as e:
                print('get 404, please check if the revenues are not revealed')

            # 減一個月
            month -= 1
            if month == 0:
                month = 12
                year -= 1

        time.sleep(10)
        for k in data.keys():
            data[k].index = data[k]['公司代號']

        df = pd.DataFrame({k: df['當月營收']
                          for k, df in data.items()}).transpose()
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.to_csv(filepath, header=True)

    df = pd.read_csv(filepath, encoding='utf-8', index_col=0)
    df.index = pd.to_datetime(df.index)
    return df


if __name__ == "__main__":
    # print(monthly_report(2020, 1))
    # print(NMons2())
    r = NMons()
    g1 = r["2330"].plot(legend=True)
    # g1 = ((r["2330"]/r["2330"].shift()-1)*100).plot()

    # g1 = r["1101"].plot(legend=True)
