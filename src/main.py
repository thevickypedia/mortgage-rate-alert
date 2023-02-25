import os
import time
from datetime import datetime
from typing import NoReturn

import jinja2
import pandas
import requests
from bs4 import BeautifulSoup
from gmailconnector.send_email import SendEmail

from src.constants import settings, LOGGER


def trigger() -> NoReturn:
    """Trigger monitoring mortgage alerts."""
    if settings.skip_schedule == datetime.now().strftime("%I:%M %p"):
        LOGGER.info(f"Schedule ignored at {settings.skip_schedule!r}")
        return
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
    dataframe = pandas.read_html(io=response.text)
    if dataframe and len(dataframe) == 1:
        dataframe = dataframe[0]
        dataframe = dataframe.to_dict()
    else:
        title = "Mortgage Rate Alert failed to run."
        message = "Dataframe looks altered, code needs to be refactored."
        if settings.operating_system == "Darwin":
            os.system(f"""osascript -e 'display notification "{message}" with title "{title}"'""")
        elif settings.operating_system == "Linux":
            os.system(f"""notify-send -t 0 '{title}' '{message}'""")
        else:
            raise LookupError(
                f"Something is off, code needs to be refactored if there are any changes in {settings.source_url!r}"
            )

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

    if os.path.isfile(settings.notification):
        with open(settings.notification) as file:
            last_notified = file.read()
        if last_notified and time.time() - float(last_notified) < 3_600:
            LOGGER.info("Last notification was sent within an hour.")
            return

    with open(settings.email_template) as email_temp:
        template_data = email_temp.read()

    rendered = jinja2.Template(template_data).render(result=dictionary, title=msg)
    response = SendEmail().send_email(subject=subject, html_body=rendered, sender="Mortgage Rate Alert")
    if response.ok:
        LOGGER.info(response.body)
        with open(settings.notification, 'w') as file:
            file.write(time.time().__str__())
    else:
        LOGGER.error(response.json())
