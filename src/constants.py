import logging
import os
import platform
import warnings
from datetime import datetime

import dotenv

dotenv.load_dotenv(dotenv_path=".env")

if not os.path.isdir('logs'):
    os.makedirs('logs')


def is_float(value: str) -> bool:
    """Returns True is value is a float, False otherwise."""
    try:
        float(value)
        return True
    except ValueError:
        return False


DEFAULT_LOG_FORMAT = logging.Formatter(
    datefmt='%b-%d-%Y %I:%M:%S %p',
    fmt='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(funcName)s - %(message)s'
)

log_handler = os.environ.get('LOG_HANDLER', os.environ.get('log_handler', 'file'))
if log_handler == 'stream':
    HANDLER = logging.StreamHandler()
else:
    FILENAME = datetime.now().strftime(os.path.join('logs', 'mortgage_%d-%m-%Y.log'))
    HANDLER = logging.FileHandler(filename=FILENAME, mode='a')
    write = ''.join(['*' for _ in range(120)])
    with open(FILENAME, 'a+') as file:
        file.seek(0)
        if not file.read():
            file.write(f"{write}\n")
        else:
            file.write(f"\n{write}\n")

LOGGER = logging.getLogger(__name__)
HANDLER.setFormatter(fmt=DEFAULT_LOG_FORMAT)
LOGGER.addHandler(hdlr=HANDLER)
LOGGER.setLevel(level=logging.DEBUG)


class Settings:
    """Wrapper for all env variables."""

    source_url = "https://www.nerdwallet.com/mortgages/mortgage-rates"
    operating_system = platform.system()
    notification = os.path.join(os.getcwd(), 'last_notify')
    if os.getcwd().endswith('src'):
        email_template = 'email_template.html'
    else:
        email_template = os.path.join('src', 'email_template.html')

    skip_schedule = os.environ.get("skip_schedule") or os.environ.get("SKIP_SCHEDULE") or ""
    if skip_schedule:
        try:
            datetime.strptime(skip_schedule, "%I:%M %p")  # Validate datetime format
        except ValueError as error:
            LOGGER.error(error)

    product = os.environ.get("PRODUCT") or os.environ.get("product") or "30-year fixed-rate"
    if product not in ('30-year fixed-rate', '20-year fixed-rate', '15-year fixed-rate', '10-year fixed-rate',
                       '7-year ARM', '5-year ARM', '3-year ARM', '30-year fixed-rate FHA', '30-year fixed-rate VA'):
        LOGGER.error(f"Invalid type of mortgage {product!r}. Defaulting to '30_year_fixed_rate'")
        product = "30-year fixed-rate"

    type_of_rate = os.environ.get("TYPE_OF_RATE") or os.environ.get("type_of_rate") or "Interest rate"
    if type_of_rate not in ("Interest rate", "APR"):
        LOGGER.error(f"Invalid type of rate {type_of_rate!r}. Defaulting to 'interest_rate'")
        type_of_rate = "Interest rate"

    min_threshold = os.environ.get("MIN_THRESHOLD") or os.environ.get("min_threshold")
    max_threshold = os.environ.get("MAX_THRESHOLD") or os.environ.get("max_threshold")

    if not min_threshold and not max_threshold:
        raise ValueError(
            "either 'min_threshold' or 'max_threshold' is required. "
            "refer https://github.com/thevickypedia/mortgage-rate-alert/blob/main/README.md#env-variables"
        )

    if min_threshold and (min_threshold.isdigit() or is_float(min_threshold)):
        min_threshold = float(min_threshold)
    elif min_threshold:
        LOGGER.error(f"Invalid minimum threshold {min_threshold!r}. Defaulting to 4.5")
        min_threshold = 4.5

    if max_threshold and (max_threshold.isdigit() or is_float(max_threshold)):
        max_threshold = float(max_threshold)
    elif max_threshold:
        LOGGER.error(f"Invalid max threshold {max_threshold!r}. Defaulting to None")
        max_threshold = None

    if min_threshold and max_threshold:
        warnings.warn(
            "both minimum and maximum threshold are present. alert will fire only for one of it."
        )


settings = Settings()
