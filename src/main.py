import io
import os
import time
from datetime import datetime

import jinja2
import pandas
from pynotification import pynotifier
import requests
from bs4 import BeautifulSoup
from gmailconnector.send_email import SendEmail

from constants import settings, LOGGER


def trigger() -> None:
    """Trigger monitoring mortgage alerts."""
    try:
        response = requests.get(url=settings.source_url)
    except requests.RequestException as error:
        LOGGER.error(error)
        return
    if not response.ok:
        LOGGER.error(response.text)
        return
    html = BeautifulSoup(response.text, "html.parser")
    updated = html.select_one('time').text or ""
    dataframe = pandas.read_html(io.StringIO(response.text))
    if dataframe and len(dataframe) == 1:
        dataframe = dataframe[0]
        dataframe = dataframe.to_dict()
    else:
        pynotifier(title="Mortgage Rate Alert failed to run.",
                   message="Dataframe looks altered, code needs to be refactored.")

    header = list(dataframe.keys())
    raw_data = {key: list(value.values()) for key, value in dataframe.items()}  # Transpose the dataframe
    dictionary = {}
    for index, element in enumerate(raw_data[header[0]]):
        dictionary[element] = {header[1].lower().replace(' ', '_'): raw_data[header[1]][index],
                               header[2].lower().replace(' ', '_'): raw_data[header[2]][index]}

    if updated.replace("Accurate as of", "").replace(".", "").strip() != datetime.now().strftime("%m/%d/%Y"):
        LOGGER.warning(f"{settings.source_url!r} returned outdated information.")
    else:
        LOGGER.info(updated)

    rate = float(dictionary[settings.product][settings.type_of_rate.replace(' ', '_').lower()].rstrip('%'))
    msg = f"{settings.type_of_rate} for {settings.product}: {rate}%"
    LOGGER.info(msg)

    condition_min = settings.min_threshold and rate <= settings.min_threshold
    condition_max = settings.max_threshold and rate >= settings.max_threshold

    if condition_min and condition_max:
        subject = f"Mortgage Rate alert: {datetime.now().strftime('%c')}"
    elif condition_min:
        subject = f"Mortgage Rates below {settings.min_threshold!r}% - {datetime.now().strftime('%c')}"
    elif condition_max:
        subject = f"Mortgage Rates above {settings.max_threshold!r}% - {datetime.now().strftime('%c')}"
    else:
        LOGGER.debug(dictionary)
        return

    with open(settings.email_template) as email_temp:
        template_data = email_temp.read()

    rendered = jinja2.Template(template_data).render(result=dictionary, title=msg)
    emailer = SendEmail(gmail_user=settings.gmail_user, gmail_pass=settings.gmail_pass)
    response = emailer.send_email(recipient=settings.recipient, subject=subject,
                                  html_body=rendered, sender="Mortgage Rate Alert")
    if response.ok:
        LOGGER.info(response.body)
    else:
        LOGGER.error(response.json())


if __name__ == '__main__':
    trigger()
