import logging
import requests
import bs4
import yagmail
import time
import random
from urllib.parse import urljoin

logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO)

class BetonInFormCrawler:
    def __init__(self):
        self.rootUrl = 'https://silke-hermes.de'
        self.silikonformenUrl = urljoin(self.rootUrl, '/shop/silikonformen')
        logging.debug("silikonformenUrl: '{}'".format(self.silikonformenUrl))

    def urlToSoup(self, url):
        return bs4.BeautifulSoup(requests.get(url).text, 'html.parser')

    def download(self):
        self.rootSoup = self.urlToSoup(self.rootUrl)
        #logging.debug("rootSoup: '{}'".format(self.rootSoup))
        self.silikonformenSoup = self.urlToSoup(self.silikonformenUrl)
        #logging.debug("silikonformenSoup: '{}'".format(self.silikonformenSoup))

    def isShopOpenViaBanner(self):
        banners = self.rootSoup.find_all('p', 'woocommerce-store-notice demo_store')
            
        for p in banners:
            for content in p.contents:
                if 'geschlossen' in content.lower():
                    logging.info("Found Banner '{}'".format(content))
                    return False
        
        if(len(banners) == 0):
            logging.info('html shop closed banner not found')
        else:
            logging.info('shop closed banner not found')
        
        return True
    
    def isShopOpenViaAddToCartButton(self):

        def getProductTitle(productTag):
            assert isinstance(productTag, bs4.element.Tag)
            title = productTag.find(class_='product_title')
            title = title.string if title else 'unknown'
            return title

        products = self.silikonformenSoup.find_all('li', 'product')
        if len(products) == 0:
            logging.error('no products found')
            return False

        logging.debug('found {} products'.format(len(products)))

        productInStockTag = None
        for product in products:
            href = None
            for child in product.children:
                if isinstance(child, bs4.element.Tag) and child['href']:
                    href = child['href']
                    break
            if not href:
                logging.debug('strange: found no href for product {}'.format(product.string))
                continue
            productSoup = self.urlToSoup(href)
            variationsTag = productSoup.find(class_='variations_form')
            if variationsTag == None:
                logging.debug('strange: found no variations for product {}'.format(getProductTitle(productSoup)))
                continue
            if 'in-stock' in variationsTag['data-product_variations']:
                productInStockTag = productSoup
                break
        
        if not productInStockTag:
            productInStockTag = products[0]
            logging.info("strange: no product found that is in stock; using '{}'".format(getProductTitle(productInStockTag)))
        else:
            logging.debug("product '{}' is in stock".format(getProductTitle(productInStockTag)))

        warumKannIchNichtBestellenButtonTag = productInStockTag.find('a', 'single_add_to_cart_button')
        if not warumKannIchNichtBestellenButtonTag:
            logging.error("'Warum kann ich nicht bestellen?' button not found")
            return False

        if 'deaktiviert' in warumKannIchNichtBestellenButtonTag['href']:
            logging.info("found button '{}' in product '{}'".format(
                    warumKannIchNichtBestellenButtonTag.string,
                    getProductTitle(productInStockTag)))
            return False

        return True

if __name__ == '__main__':
    crawler = BetonInFormCrawler()
    while True:
        crawler.download()
        sleepSec = random.randint(600, 1800)
        
        if crawler.isShopOpenViaAddToCartButton():
            logging.info("shop seems open, will notify")
            yag = yagmail.SMTP("johannes.stark.js@gmail.com", oauth2_file="./lib/secret.json")
            yag.send(subject="Beton In Form Shop ist offen", contents="Der Shop ist jetzt offen.", to="evaa.b@hotmail.com")
            sleepSec += 3600
        else:
            logging.info("shop seems closed")

        logging.info("rechecking in {} minutes".format(int(sleepSec/60)))
        time.sleep(sleepSec)
