import logging
from typing import Tuple
import requests
import bs4
from urllib.parse import urljoin
import re
import hashlib
import json
import os
from datetime import datetime

class BetonInFormCrawler:
    def __init__(self):
        self.rootUrl = 'https://silke-hermes.de'
        self.silikonformenUrl = urljoin(self.rootUrl, '/shop/silikonformen')
        logging.debug("silikonformenUrl: '{}'".format(self.silikonformenUrl))

    @staticmethod
    def __urlToSoup(url : str) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(requests.get(url).text, 'html.parser')

    def getRootUrl(self) -> str:
        return self.rootUrl

    def download(self) -> None:
        self.rootSoup = self.__urlToSoup(self.rootUrl)
        #logging.debug("rootSoup: '{}'".format(self.rootSoup))
        self.silikonformenSoup = self.__urlToSoup(self.silikonformenUrl)
        #logging.debug("silikonformenSoup: '{}'".format(self.silikonformenSoup))

    def isShopOpenViaBanner(self) -> bool:
        banners = self.rootSoup.find_all('p', 'woocommerce-store-notice demo_store')
            
        for p in banners:
            for content in p.contents:
                if 'geschlossen' in content.lower():
                    logging.debug(f"found banner '{content}'")
                    return False
        
        if(len(banners) == 0):
            logging.info('html shop closed banner not found')
        else:
            logging.info('shop closed banner not found')
        
        return True
    
    def isShopOpenViaAddToCartButton(self) -> Tuple[bool, str]:

        def getProductTitle(productTag):
            assert isinstance(productTag, bs4.element.Tag)
            title = productTag.find(class_='product_title')
            title = title.string if title else 'unknown'
            return title

        products = self.silikonformenSoup.find_all('li', 'product')
        if len(products) == 0:
            logging.error('no products found')
            return False, None

        logging.debug(f"found {len(products)} products")

        productInStockTag = None
        productInStockUrl = None
        for product in products:
            href = None
            for child in product.children:
                if isinstance(child, bs4.element.Tag) and child['href']:
                    href = child['href']
                    break
            if not href:
                logging.debug(f"strange: found no href for product {product.string}")
                continue
            productSoup = self.__urlToSoup(href)
            variationsTag = productSoup.find(class_='variations_form')
            if variationsTag == None:
                logging.debug(f"strange: found no variations for product {getProductTitle(productSoup)}")
                continue
            if 'in-stock' in variationsTag['data-product_variations']:
                productInStockTag = productSoup
                productInStockUrl = href
                break
        
        if not productInStockTag:
            productInStockTag = (products[0], None)
            logging.warning(f"strange: no product found that is in stock; using '{getProductTitle(productInStockTag)}'")
        else:
            logging.debug(f"product '{getProductTitle(productInStockTag)}' is in stock")

        warumKannIchNichtBestellenButtonTag = productInStockTag.find('a', 'single_add_to_cart_button')
        if not warumKannIchNichtBestellenButtonTag:
            logging.info("'Warum kann ich nicht bestellen?' button not found; printing all add to cart buttons:")
            logging.info(str(productInStockTag.find_all(class_=re.compile('add_to_cart'))))
            return True, productInStockUrl

        if 'deaktiviert' in warumKannIchNichtBestellenButtonTag['href']:
            logging.debug("found button '{}' in product '{}'".format(
                    warumKannIchNichtBestellenButtonTag.string,
                    getProductTitle(productInStockTag)))
            return False, None

        return True, productInStockUrl

    def isNewsSectionUpdateAvailable(self) -> bool:
        rootWebsiteStrings = []

        for string in self.rootSoup.strings:
            string = string.strip().strip('\n').strip('-').strip('.')

            if len(string) > 10:
                rootWebsiteStrings.append(string)

        if len(rootWebsiteStrings) <= 100:
            logging.error(f"only {len(rootWebsiteStrings)} strings found in root site, something is not right")
            return False

        logging.debug(f"all strings on root site: '{';'.join(rootWebsiteStrings)}'")

        hashStorageFile = 'hashes.json'
        jsonKey = 'newsSection'

        if not os.path.isfile(hashStorageFile):
            with open(hashStorageFile, 'a+') as f:
                json.dump({jsonKey : {'date':'', 'md5':'none'}}, f)
        
        with open(hashStorageFile, 'r+') as f:
            jsonDoc = json.load(f)
            oldHashString = jsonDoc[jsonKey]['md5']
            logging.debug(f"old hash {oldHashString}")
            newHashString = hashlib.md5("".join(rootWebsiteStrings).encode()).hexdigest()
            logging.debug(f"new hash {newHashString}")
            if oldHashString != newHashString:
                f.seek(0)
                jsonDoc[jsonKey]['md5'] = newHashString
                jsonDoc[jsonKey]['date'] = datetime.today().strftime('%H:%M %d.%m.%Y')
                json.dump(jsonDoc, f)
                return True
        
        return False
