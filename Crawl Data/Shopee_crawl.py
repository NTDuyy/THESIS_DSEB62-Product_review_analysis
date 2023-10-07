import re
import json
import requests
import pandas as pd
import datetime as dt
import time

class ShopeeCrawler:
    """ A class to crawl product reviews on Shopee.vn """
    def __init__(self):
        self.data = {"itemid": [], "shopid": [], "username": [], "rating": [], "time": [], "source": [], "comment": []}
        self.shop_id, self.item_id = None, None

    def get_ids_from_link(self, base_url):
        """
        Gets Product id and Shop id

        Parameters
        ----------
        base_url : str
            Product link

        Returns
        ----------
        tuple
            a tuple containing Product id and Shop id
        """

        r = re.search(r"i\.(\d+)\.(\d+)", base_url)
        return (r[1], r[2])

    def Crawl(self, item_id, shop_id, display = False, most_recent = False, verbose = 100):
        """
        Gets reviews and related information about a product

        Parameters
        ----------
        item_id : int
            Product ID
        
        shop_id : int
            Shop ID 
        
        display : bool 
            Display data as crawled

        most_recent: bool
            only save reviews that are at most 1 day old

        Returns
        ----------
        dict
            a dictionary containing username (reviewer's account name), rating (number of stars the reviewer gave), comment (the review on the product), time (date and time of the comment in unix time),
            itemid and shopid.


        """
        offset = 0
        while True:
            ratings_url = f"https://shopee.vn/api/v2/item/get_ratings?filter=0&flag=1&itemid={item_id}&limit=20&offset={offset}&shopid={shop_id}&type=0"
            response = requests.get(ratings_url).json()
            if not response["data"]["ratings"]:
                break

            for i, rating in enumerate(response["data"]["ratings"], 1):
                if most_recent:
                    delta = dt.datetime.now() - dt.datetime.fromtimestamp(rating["ctime"])
                    if delta <= dt.timedelta(days=1):
                        self.data["username"].append(rating["author_username"])
                        self.data["rating"].append(rating["rating_star"])
                        self.data["comment"].append(rating["comment"])
                        self.data["time"].append(rating["ctime"]) # convert to unix timestamp
                        self.data["shopid"].append(item_id)
                        self.data["itemid"].append(shop_id)
                        self.data["source"].append("Shopee")
                else:
                        self.data["username"].append(rating["author_username"])
                        self.data["rating"].append(rating["rating_star"])
                        self.data["comment"].append(rating["comment"])
                        self.data["time"].append(rating["ctime"])
                        self.data["shopid"].append(item_id)
                        self.data["itemid"].append(shop_id)
                        self.data["source"].append("Shopee")
            if display:
                print(rating["author_username"])
                print(rating["rating_star"])
                print(rating["comment"])
                print("-" * 100)
                print(offset)
            

            offset += 20
            

        return self.data
    
    def get_data(self):
        """
        Get all data crawled within the object

        Returns
        ----------
        dict
            a dictionary containing username (reviewer's account name), rating (number of stars the reviewer gave), comment (the review on the product), time (date and time of the comment in unix time),
            itemid and shopid.    
        """
        return self.data
    
    def CrawlByCat(self, catid, cat_level = 2, limit = None):
        """
        Crawl reviews by categories

        Parameters
        ----------
        catid : int
            category ID

        cat_level : int
            1 for category, 2 for subcategory
        
        limit : int
            limit number of products in the category (None to crawl all products)

        Returns
        ----------
        dict
            a dictionary containing username (reviewer's account name), rating (number of stars the reviewer gave), comment (the review on the product), time (date and time of the comment in unix time),
            itemid and shopid.        
        
        """
        
        params = {
        "bundle": "category_landing_page",
        "cat_level": cat_level,
        "catid": catid, 
        "offset": 0,
        }
        
            
        crawler = ShopeeCrawler()
        product_data = []
        url = 'https://shopee.vn/api/v4/recommend/recommend'

        response = requests.get(url, params=params)
        n = response.json().get('data').get('sections')[0].get('data').get('item')

        for record in n:
            product_data.append({'itemid': record['itemid'], 'shopid': record['shopid']})

        for product in product_data:
            crawler.Crawl(product["itemid"], product["shopid"])
        self.data = crawler.get_data()
        return self.data

    def GetShopInfo(self):
        """
        Get shop information

        Returns
        ----------
        dict
            a dictionary containing shop information    
        
        """
        df = pd.DataFrame(self.data)
        itemids = df["itemid"].unique()

        output = {"shopid": [], "name": [], "ctime": [], "is_shopee_verified": [], "is_preferred_plus_seller": [], "is_official_shop": [], "shop_location": [], "item_count": [],
                  "rating_star": [], "response_rate": [], "response_time": [],  'rating_bad': [],'rating_good': [], 'rating_normal': []}
        for itemid in itemids:
            url = f'https://shopee.vn/api/v4/product/get_shop_info?shopid={itemid}'
            response = requests.get(url).json()
            data = response.get("data")
            for key in list(output.keys())[1::]:
                output[key].append(data[key])
            output["shopid"].append(df[df["itemid"] == str(itemid)]["shopid"].iloc[0])
        return output