import yagmail
import logging
import requests

def __getRandomGermanJoke() -> str:
    joke = None
    try:
        joke = requests.get('https://witzapi.de/api/joke').json()[0]['text']
    except Exception as e:
        logging.exception(e)

    logging.debug(joke)
    return joke

def send(subject : str, body : str, appendJokeToBody : bool = True) -> None:
    if appendJokeToBody:
        joke = __getRandomGermanJoke()
        if joke:
            body += f"\n\nUnd hier noch ein Witz für dich:\n{joke}"

    yag = yagmail.SMTP('johannes.stark.js@gmail.com', oauth2_file='./secrets/beton-in-form-crawler/gmail.json')

    kwargs = {
        'subject' : subject,
        'contents' : body,
        'to' : 'evaa.b@hotmail.com',
    }
    yag.send(**kwargs)
