import json
import os.path as osp
import platform
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.action_chains import ActionChains


class CollectLinks:
    def __init__(self, no_gui=False, proxy=None):
        executable = ''

        if platform.system() == 'Windows':
            print('Detected OS : Windows')
            executable = './chromedriver/chromedriver_win.exe'
        elif platform.system() == 'Linux':
            print('Detected OS : Linux')
            executable = './chromedriver/chromedriver_linux'
        elif platform.system() == 'Darwin':
            print('Detected OS : Mac')
            executable = './chromedriver/chromedriver_mac'
        else:
            raise OSError('Unknown OS Type')

        if not osp.exists(executable):
            raise FileNotFoundError(
                'Chromedriver file should be placed at {}'.format(executable))

        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        if no_gui:
            chrome_options.add_argument('--headless')
        if proxy:
            chrome_options.add_argument("--proxy-server={}".format(proxy))
        self.browser = webdriver.Chrome(
            ChromeDriverManager().install(), chrome_options=chrome_options)

        browser_version = 'Failed to detect version'
        chromedriver_version = 'Failed to detect version'
        major_version_different = False

        if 'browserVersion' in self.browser.capabilities:
            browser_version = str(self.browser.capabilities['browserVersion'])

        if 'chrome' in self.browser.capabilities:
            if 'chromedriverVersion' in self.browser.capabilities['chrome']:
                chromedriver_version = str(
                    self.browser.capabilities['chrome']['chromedriverVersion']).split(' ')[0]

        if browser_version.split('.')[0] != chromedriver_version.split('.')[0]:
            major_version_different = True

        print('_________________________________')
        print('Current web-browser version:\t{}'.format(browser_version))
        print('Current chrome-driver version:\t{}'.format(chromedriver_version))
        if major_version_different:
            print('warning: Version different')
            print(
                'Download correct version at "http://chromedriver.chromium.org/downloads" and place in "./chromedriver"')
        print('_________________________________')

    def extract_item_shopee(self, html_doc):
        list_item = []
        soup = BeautifulSoup(html_doc, 'html.parser')
        items = soup.find_all(
            "div", {"class": "col-xs-2-4 shopee-search-item-result__item"})
        for item in items:
            item_name = item.find_all("div", {"class": "ie3A+n bM+7UW Cve6sh"})
            if item_name:
                item_info = {
                    "name": item_name[0].decode_contents().strip(),
                    "price": 0,
                    "quantity_sold": 0,
                    "shop_name": "",
                    "url": ""
                }
                item_quantity_sold = item.find_all(
                    "div", {"class": "r6HknA uEPGHT"})
                if not item_quantity_sold:
                    item_quantity_sold = item.find_all(
                        "div", {"class": "r6HknA"})
                item_link = item.find("a")["href"]
                item_price = item.find_all("div", {"class": "vioxXd rVLWG6"})[0].find_all(
                    "span", {"class": "ZEgDH9"})[0].decode_contents().strip()
                if item_quantity_sold:
                    item_info["quantity_sold"] = item_quantity_sold[0].decode_contents(
                    ).strip()
                item_info["price"] = item_price
                item_info["url"] = f"https://shopee.vn{item_link}"
                list_item.append(item_info)

        return list_item

    def shopee(self, url, number_pages, keyword):
        self.browser.get(url)
        self.browser.maximize_window()

        time.sleep(1)

        print('Scrolling down')
        result = []

        try:
            for i in range(number_pages):
                try:
                    elem = self.browser.find_element(By.TAG_NAME, "body")
                    for i in range(6):
                        elem.send_keys(Keys.PAGE_DOWN)
                        time.sleep(1)

                    full_page_html = self.browser.page_source
                    with open("full_page_html.html", "w", encoding='utf-8') as file:
                        file.write(str(full_page_html))
                    items = self.extract_item_shopee(full_page_html)
                    result.extend(items)

                    elem.send_keys(Keys.HOME)
                    time.sleep(1)

                except Exception as e:
                    print(e)
                    print("One page error occured")

                self.browser.find_element(
                    By.XPATH, "//button[@class='shopee-button-outline shopee-mini-page-controller__next-btn']").click()
                time.sleep(3)

        except Exception as es:
            print(es)

        result = {
            f'{keyword}': result
        }

        with open(f"result/shopee({keyword}).json", 'w', encoding='utf-8') as file:
            json.dump(result, file, ensure_ascii=False, indent=4)

        self.browser.close()


if __name__ == '__main__':
    # Run on background if no_gui=True
    no_gui = False
    number_pages = 1
    url = "https://shopee.vn/buiducminh?categoryId=100013&entryPoint=ShopByPDP&itemId=1428754739"

    collect = CollectLinks(no_gui=no_gui)
    collect.test(url, 10, "Shop Sim Giá Rẻ")
