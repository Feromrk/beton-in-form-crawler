import logging
import requests
from bs4 import BeautifulSoup
import yagmail
import time

logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO)

class BetonInFormCrawler:
    def __init__(self):
        self.url = 'https://silke-hermes.de'

        self.html = requests.get(self.url).text
        self.soup = BeautifulSoup(self.html, 'html.parser')
    
    def isShopOpenViaBanner(self):
        banners = self.soup.find_all('p', 'woocommerce-store-notice demo_store')
            
        for p in banners:
            for content in p.contents:
                if 'geschlossen' in content.lower():
                    logging.info(f'Found Banner "{content}"')
                    return False
        
        if(len(banners) == 0):
            logging.info('html shop closed banner not found')
        else:
            logging.info('shop closed banner not found')
        
        return True

if __name__ == '__main__':
    while True:
        if BetonInFormCrawler().isShopOpenViaBanner():
            logging.info("shop is open")
            yag = yagmail.SMTP("johannes.stark.js@gmail.com", oauth2_file="./secret.json")
            yag.send(subject="Beton In Form Shop ist offen", contents="Der Shop ist jetzt offen.", to="evaa.b@hotmail.com")
        else:
            logging.info("shop is closed")

        time.sleep(60*30)
