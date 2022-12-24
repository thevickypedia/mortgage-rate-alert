import jinja2
import pandas
import requests
from bs4 import BeautifulSoup
from gmailconnector.send_email import SendEmail

from constants import (LOGGER, SKIP_SCHEDULE, datetime, PRODUCT,
                       TYPE_OF_RATE, MIN_THRESHOLD, MAX_THRESHOLD)

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
    updated = html.select_one('time').text or ""
    dataframe = pandas.read_html(io=response.text)
    header = list(dataframe[0].keys())

    # todo: reduce multiple conversions
    raw_data = {key: list(value.values) for key, value in dataframe[0].items()}
    dictionary = {}
    for index, element in enumerate(raw_data[header[0]]):
        dictionary[element] = {header[1]: float(raw_data[header[1]][index].rstrip('%')),
                               header[2]: float(raw_data[header[2]][index].rstrip('%'))}

    if updated.replace("Accurate as of", "").replace(".", "").strip() != datetime.now().strftime("%m/%d/%Y"):
        LOGGER.warning(f"{SOURCE_URL} returned outdated information.")
    else:
        LOGGER.info(updated)

    rate = dictionary[PRODUCT][TYPE_OF_RATE]
    msg = f"{TYPE_OF_RATE} for {PRODUCT}: {rate}%"
    LOGGER.info(msg)

    condition_min = MIN_THRESHOLD and rate <= MIN_THRESHOLD
    condition_max = MAX_THRESHOLD and rate >= MAX_THRESHOLD

    if condition_min and condition_max:
        subject = f"Mortgage Rate alert: {datetime.now().strftime('%c')}"
    elif condition_min:
        subject = f"Mortgage Rates below {MIN_THRESHOLD!r}% - {datetime.now().strftime('%c')}"
    elif condition_max:
        subject = f"Mortgage Rates above {MAX_THRESHOLD!r}% - {datetime.now().strftime('%c')}"
    else:
        LOGGER.debug(dictionary)
        return

    with open('email_template.html') as email_temp:
        template_data = email_temp.read()

    # todo: remove framing new dict and try to accommodate existing
    rendered = jinja2.Template(template_data).render(
        result={item[0]: {"interest_rate": item[1], "apr": item[2]} for item in [d.values for d in dataframe][0]},
        title=msg
    )
    response = SendEmail().send_email(subject=subject, html_body=rendered, sender="Mortgage Rate Alert")
    if response.ok:
        LOGGER.info(response.body)
    else:
        LOGGER.error(response.json())


if __name__ == '__main__':
    trigger()
