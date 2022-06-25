import os, re, time, datetime, sys, csv, pandas
from bs4 import BeautifulSoup
from os.path import join,dirname
from selenium.webdriver import Chrome,ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin

from make_graph import make_graph


def login():
    options = ChromeOptions()
    options.add_argument("--window-size=720,1080")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--headless")


    driver = Chrome(ChromeDriverManager().install(), options=options)

    LOGIN_URL = "https://trade.sbineomobile.co.jp/login"
    driver.get(LOGIN_URL)
    time.sleep(0.5)

    input_name = driver.find_element(By.NAME,"username")
    input_name.send_keys(os.environ['USER_ID'])
    input_pass = driver.find_element(By.NAME, "password")
    input_pass.send_keys(os.environ['PASSWORD'])
    login_btn = driver.find_element(By.ID, "neo-login-btn")
    login_btn.click()

    return driver



def main():
    driver = login()
    
    PORTFOLIO_URL = "https://trade.sbineomobile.co.jp/account/portfolio"
    driver.get(PORTFOLIO_URL)
    time.sleep(2)

    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.select('#portfolio-layout > section')
    table_length = len(tables)
    while True:
        driver.execute_script("document.getElementById('portfolio-foot').scrollIntoView({behavior: 'smooth',block: 'start'});")
        time.sleep(1)
        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
        tables = soup.select('#portfolio-layout > section')
        if(table_length == len(tables)):
            break
        table_length = len(tables)

    all_dict = {
        'code':[],
        'name':[],
        'amount':[],
        'valuation':[],
        'valuation_rate':[],
        'acquisition_unit_price':[],
        'pl':[],
        'present_value':[]
    }



    for x in range(4, table_length):
        code = re.findall(r'p .*?"ticker">(\d+?)</p>',str(tables[x]))[0]
        name = re.findall(r'<a>\n +?(\S.+?)\n',str(tables[x]))[0]
        amount = re.findall(r'保有数量</th>\n<td><span>(\d+?)</span>',str(tables[x]))[0]
        amount = round(float(amount.replace(',','')))
        valuation = re.findall(r'評価額</div>\n<span>(\S+?)\n',str(tables[x]))[0]
        valuation = round(float(valuation.replace(',','')))
        acquisition_unit_price = re.findall(r'平均取得単価</th>\n<td><span>\n\s*(.+?)\n',str(tables[x]))[0]
        acquisition_unit_price = round(float(acquisition_unit_price.replace(',','')))
        present_value = re.findall(r'現在値/前日比</th>\n<td>\n<span>(.*?)</span>',str(tables[x]))[0]
        present_value = round(float(present_value.replace(',','')))
        pl = round((present_value - acquisition_unit_price) * amount)
        valuation_rate = round(float(pl/valuation*100),2)

        all_dict['code'].append(code)
        all_dict['name'].append(name)
        all_dict['amount'].append(amount)
        all_dict['valuation'].append(valuation)
        all_dict['valuation_rate'].append(valuation_rate)
        all_dict['acquisition_unit_price'].append(acquisition_unit_price)
        all_dict['pl'].append(pl)
        all_dict['present_value'].append(present_value)

    df_neomobile = pandas.DataFrame({
        'コード':all_dict['code'],
        '銘柄名':all_dict['name'],
        '保有数量(株)':all_dict['amount'],
        '評価額(円)':all_dict['valuation'],
        '評価損益率(%)':all_dict['valuation_rate'],
        '平均取得単価(円)':all_dict['acquisition_unit_price'],
        '損益(円)':all_dict['pl'],
        '現在値(円)':all_dict['present_value']
        })

    driver.quit()
    
    make_graph(df_neomobile)


if __name__ == "__main__":
    main()