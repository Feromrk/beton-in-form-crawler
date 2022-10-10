import sys
MIN_PYTHON = (3,6)
assert sys.version_info >= MIN_PYTHON, "Python %s.%s or later is required.\n" % MIN_PYTHON

import logging
import time
import random

from BetonInFormCrawler import BetonInFormCrawler
import Email


def main():
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(funcName)s: %(message)s',
        level=logging.INFO
    )

    crawler = BetonInFormCrawler()
    while True:
        crawler.download()
        sleepSec = random.randint(300, 900)

        shopOpen = False
        shopOpenReason = None
        emailSubject = None
        emailBody = None

        if crawler.isShopOpenViaBanner():
            shopOpen = True
            shopOpenReason = 'banner'
            emailSubject = 'BETON IN FORM Shop scheint geöffnet zu sein'
            emailBody = f"{crawler.getRootUrl()} scheint geöffnet zu sein.\nWie komm ich drauf? 'Shop geschlossen' Banner am unteren Displayrand ist nicht da."

        shopOpenViaAddToCartButton, shopOpenViaAddToCartButtonProductUrl = crawler.isShopOpenViaAddToCartButton()
        
        if shopOpenViaAddToCartButton:
            shopOpen = True
            shopOpenReason = 'addToCartButton'
            emailSubject = 'BETON IN FORM Shop ist jetzt offen'
            emailBody = f"Jetzt aber schnell: {crawler.getRootUrl()} hat geöffnet."
            
            if shopOpenViaAddToCartButtonProductUrl:
                emailBody += f"\nWie komm ich drauf? 'Warum kann ich nicht bestellen?' Button fehlt hier: {shopOpenViaAddToCartButtonProductUrl}"
        
        if shopOpen:
            logging.info(f"shop seems open, reason '{shopOpenReason}', will notify")
            emailBody += '\nNormalerweise würde ich dir noch einen Witz mitgeben, aber dafür hast du jetzt keine Zeit.'
            Email.send(emailSubject, emailBody, False)
            sleepSec += 3600
        else:
            logging.info('shop seems closed')
        
        if crawler.isNewsSectionUpdateAvailable():
            logging.info('news section was updated, will notify')
            Email.send('BETON IN FORM Shop Update', f"{crawler.getRootUrl()} hat sich verändert. Schau mal lieber nach, ob es Neuigkeiten gibt.")
        else:
            logging.info('no news updates available')

        logging.info("rechecking in {} minutes".format(int(sleepSec/60)))
        time.sleep(sleepSec)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.exception(e)
