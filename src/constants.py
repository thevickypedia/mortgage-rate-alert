import logging
import os
import platform
import warnings
from datetime import datetime

import dotenv

SYSTEM = platform.system()

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
FILENAME = datetime.now().strftime(os.path.join('logs', 'jarvis_%d-%m-%Y.log'))

NOTIFICATION = os.path.join(os.getcwd(), 'last_notify.yaml')

LOGGER = logging.getLogger("jarvis")

HANDLER = logging.FileHandler(filename=FILENAME, mode='a')
HANDLER.setFormatter(fmt=DEFAULT_LOG_FORMAT)

LOGGER.addHandler(hdlr=HANDLER)
LOGGER.setLevel(level=logging.INFO)

write = ''.join(['*' for _ in range(120)])
with open(FILENAME, 'a+') as file:
    file.seek(0)
    if not file.read():
        file.write(f"{write}\n")
    else:
        file.write(f"\n{write}\n")

SKIP_SCHEDULE = os.environ.get("SKIP_SCHEDULE", "")
if SKIP_SCHEDULE:
    try:
        datetime.strptime(SKIP_SCHEDULE, "%I:%M %p")  # Validate datetime format
    except ValueError as error:
        LOGGER.error(error)

PRODUCT = os.environ.get("PRODUCT", "30-year fixed-rate")
if PRODUCT not in ('30-year fixed-rate', '20-year fixed-rate', '15-year fixed-rate', '10-year fixed-rate',
                   '7-year ARM', '5-year ARM', '3-year ARM', '30-year fixed-rate FHA', '30-year fixed-rate VA'):
    LOGGER.error(f"Invalid type of mortgage {PRODUCT!r}. Defaulting to '30_year_fixed_rate'")
    PRODUCT = "30-year fixed-rate"

TYPE_OF_RATE = os.environ.get("TYPE_OF_RATE", "Interest rate")
if TYPE_OF_RATE not in ("Interest rate", "APR"):
    LOGGER.error(f"Invalid type of rate {TYPE_OF_RATE!r}. Defaulting to 'interest_rate'")
    TYPE_OF_RATE = "Interest rate"

MIN_THRESHOLD = os.environ.get("MIN_THRESHOLD")
MAX_THRESHOLD = os.environ.get("MAX_THRESHOLD")

if not MIN_THRESHOLD and not MAX_THRESHOLD:
    raise ValueError(
        "either min or max threshold is required. "
        "refer https://github.com/thevickypedia/mortgage-rate-alert/blob/main/README.md#env-variables"
    )

if MIN_THRESHOLD and (MIN_THRESHOLD.isdigit() or is_float(MIN_THRESHOLD)):
    MIN_THRESHOLD = float(MIN_THRESHOLD)
elif MIN_THRESHOLD:
    LOGGER.error(f"Invalid minimum threshold {MIN_THRESHOLD!r}. Defaulting to 4.5")
    MIN_THRESHOLD = 4.5

if MAX_THRESHOLD and (MAX_THRESHOLD.isdigit() or is_float(MAX_THRESHOLD)):
    MAX_THRESHOLD = float(MAX_THRESHOLD)
elif MAX_THRESHOLD:
    LOGGER.error(f"Invalid max threshold {MAX_THRESHOLD!r}. Defaulting to None")
    MAX_THRESHOLD = None

if MIN_THRESHOLD and MAX_THRESHOLD:
    warnings.warn(
        "both minimum and maximum threshold are present. alert will fire only for one of it."
    )
