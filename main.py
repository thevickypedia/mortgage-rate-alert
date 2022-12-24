import jinja2
import pandas
import requests
from bs4 import BeautifulSoup
from gmailconnector.send_email import SendEmail

from constants import LOGGER, SKIP_SCHEDULE, datetime, TYPE_OF_MORTGAGE, TYPE_OF_RATE, MIN_THRESHOLD, MAX_THRESHOLD

SOURCE_URL = "https://www.nerdwallet.com/mortgages/mortgage-rates"


def trigger():
    if SKIP_SCHEDULE == datetime.now().strftime("%I:%M %p"):
        LOGGER.info(f"Schedule ignored at {SKIP_SCHEDULE!r}")
        return
    try:
        response = requests.get(url=SOURCE_URL)
    except requests.RequestException as error:
        LOGGER.error(error)
        return
    if not response.ok:
        LOGGER.error(response.text)
        return
    html = BeautifulSoup(response.text, "html.parser")
    updated = html.select_one('time').text
    dataframe = pandas.read_html(io=response.text)
    dictionary = {
        item[0].replace("-", "_").replace(" ", "_"): {
            "interest_rate": float(item[1].rstrip("%")), "apr": float(item[2].rstrip("%"))
        } for item in [d.values for d in dataframe][0]
    }

    if updated and updated.replace("Accurate as of", "").strip() == datetime.now().strftime("%m/%d/%Y"):
        LOGGER.warning(message=f"{SOURCE_URL} returned outdated information.")
    else:
        LOGGER.info(updated)

    rate = dictionary[TYPE_OF_MORTGAGE][TYPE_OF_RATE]
    msg = f"Current mortgage interest rate: {rate}%"
    LOGGER.info(msg)

    if MIN_THRESHOLD and rate <= MIN_THRESHOLD:
        subject = f"Mortgage Rates below {MIN_THRESHOLD!r} - {datetime.now().strftime('%c')}"
    elif MAX_THRESHOLD and rate >= MAX_THRESHOLD:
        subject = f"Mortgage Rates above {MAX_THRESHOLD!r} - {datetime.now().strftime('%c')}"
    else:
        LOGGER.debug(dictionary)
        return

    with open('email_template.html') as email_temp:
        template_data = email_temp.read()
    rendered = jinja2.Template(template_data).render(result=dictionary)
    response = SendEmail().send_email(subject=subject, body=msg, html_body=rendered)
    if response.ok:
        LOGGER.info(response.body)
    else:
        LOGGER.error(response.json())


if __name__ == '__main__':
    trigger()
