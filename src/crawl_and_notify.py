import sys
MIN_PYTHON = (3,6)
assert sys.version_info >= MIN_PYTHON, "Python %s.%s or later is required.\n" % MIN_PYTHON

import logging
import yagmail
import time
import random
from BetonInFormCrawler import BetonInFormCrawler

def sendEmail(subject : str, body : str) -> None:
    yag = yagmail.SMTP('johannes.stark.js@gmail.com', oauth2_file='./lib/secret.json')
    yag.send(subject=subject, contents=body, to='evaa.b@hotmail.com')

def main():
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(funcName)s: %(message)s',
        level=logging.INFO
    )

    crawler = BetonInFormCrawler()
    while True:
        crawler.download()
        sleepSec = random.randint(600, 1800)
        
        if crawler.isShopOpenViaAddToCartButton():
            logging.info('shop seems open, will notify')
            sendEmail('BETON IN FORM Shop ist jetzt offen', f"{crawler.getRootUrl()} ist jetzt offen.")
            sleepSec += 3600
        else:
            logging.info('shop seems closed')
        
        if crawler.isNewsSectionUpdateAvailable():
            logging.info('news section was updated, will notify')
            sendEmail('BETON IN FORM Shop Update', f"{crawler.getRootUrl()} hat sich verändert. Schau mal lieber nach, ob es Neuigkeiten gibt.")
        else:
            logging.info('no news updates available')

        logging.info("rechecking in {} minutes".format(int(sleepSec/60)))
        time.sleep(sleepSec)

if __name__ == '__main__':
    main()
