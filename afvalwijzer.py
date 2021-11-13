from datetime import datetime, date
import requests
import os
from bs4 import BeautifulSoup
import locale
from dateutil import relativedelta
import telegram_send

import logging
from logging.handlers import TimedRotatingFileHandler
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M',
                    handlers=[TimedRotatingFileHandler('afvalwijzer.log', 
                                                        when='d',
                                                        interval=30,
                                                        backupCount=1,
                                                        encoding = 'utf-8')
                              ]
                    )


URL = os.environ["URL"]
CATEGORIES = ["gft", "papier", "pmd"]
TELEGRAM_CONF = "telegram-send.conf" # generate the conf file: telegram-send --configure --config <name>.conf


# list object to store the parsed collection dates
collection_dates = list()


def parse_date(date_str: str) -> datetime:
    # save the current locale
    old_loc = locale.getlocale(locale.LC_TIME)

    # date format is in NL locale and we set same for the runtime to be able to parse it
    # make sure locale is installed on the machine where script would run
    # locale.setlocale(locale.LC_TIME, 'nl_NL.utf8') # locale name on arch
    locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8') #locale name on alpine used on docker

    # date = 'dinsdag 30 november 2011'
    format = '%A %d %B %Y'
    retval = datetime.strptime(date_str, format)

    # switch back to original locale
    locale.setlocale(locale.LC_TIME, old_loc)
    return retval



def parse_webpage(soup: BeautifulSoup, month_year: tuple[str, int], category: str):
    res = soup.select(f"div#{month_year[0]} .column .{category} .span-line-break") # css selector can be used
    #return res
    for e in res:
        date = parse_date(e.get_text() + " " + str(month_year[1]))
        collection_dates.append((category, date))
        # print(f"{category}: {e.get_text()} {month_year[1]}")



def publish_to_telegram(collection_date: tuple[str, datetime]):
    tomorrow = datetime.today() + relativedelta.relativedelta(days=1)

    # below is for test only
    # tomorrow = date(2021, 11, 15) + relativedelta.relativedelta(days=1) 

    if  tomorrow == collection_date[1].date():
        msg = f"*__Tomorrow__*, {tomorrow.strftime('%A, %d %B')}, is *__{collection_date[0]} bin collection__* day\."
        msg_for_log = msg.replace("*","").replace("__","").replace("\\","")  #remove markdown formatting characters
        print(msg_for_log)
        logging.info(msg_for_log)
        telegram_send.send(messages=[msg], conf=TELEGRAM_CONF, parse_mode="MarkdownV2")
    else:
        logging.info("No collection date reminder on Telegram needeed.")



def run():
    logging.info("Garbage bins collection dates check initiated...")

    now = datetime.now()
    current_month_str = now.strftime('%B-%Y').lower()

    # as app will run daily, get also next month to cover edge case of run on last day of the month
    next_month = now + relativedelta.relativedelta(months=1)
    next_month_str = next_month.strftime('%B-%Y').lower()

    months = [(current_month_str, now.year), (next_month_str, next_month.year)]

    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    # seek in the web page the dates for current and next month, for each trash-bin category 
    [parse_webpage(soup, m, c) for m in months for c in CATEGORIES]

    # get the next collection date per category
    for cat in CATEGORIES:
        next_date = next(d for d in collection_dates if cat in d[0] and datetime.today() < d[1])
        logging.info(f"Next {cat} collection date: {next_date[1].strftime('%d-%B-%Y')}.")

        # implement update for openhab here
        publish_to_telegram(next_date)


if __name__ == '__main__':
    try:
        run()
        logging.info("Finished!")
    except Exception:
        logging.info("Exception occured during execution.", exc_info=True)

