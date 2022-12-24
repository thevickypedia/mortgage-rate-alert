import logging
import os
from datetime import datetime

import dotenv

dotenv.load_dotenv(dotenv_path=".env")

if not os.path.isdir('logs'):
    os.makedirs('logs')

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

TYPE_OF_MORTGAGE = os.environ.get("TYPE_OF_MORTGAGE", "30_year_fixed_rate")
if TYPE_OF_MORTGAGE not in ('30_year_fixed_rate', '20_year_fixed_rate', '15_year_fixed_rate', '10_year_fixed_rate',
                            '7_year_ARM', '5_year_ARM', '3_year_ARM', '30_year_fixed_rate_FHA', '30_year_fixed_rate_VA'):
    LOGGER.error(f"Invalid type of mortgage {TYPE_OF_MORTGAGE!r}. Defaulting to '30_year_fixed_rate'")
    TYPE_OF_MORTGAGE = "30_year_fixed_rate"

TYPE_OF_RATE = os.environ.get("TYPE_OF_RATE", "interest_rate")
if TYPE_OF_RATE not in ("interest_rate", "apr"):
    LOGGER.error(f"Invalid type of rate {TYPE_OF_RATE!r}. Defaulting to 'interest_rate'")
    TYPE_OF_RATE = "interest_rate"

MIN_THRESHOLD = os.environ.get("MIN_THRESHOLD")
MAX_THRESHOLD = os.environ.get("MAX_THRESHOLD")

if not MIN_THRESHOLD and not MAX_THRESHOLD:
    raise ValueError(
        "either min or max threshold is required. "
        "refer https://github.com/thevickypedia/mortgage-rate-alert/blob/main/README.md"
    )

if MIN_THRESHOLD and MIN_THRESHOLD.isdigit():
    MIN_THRESHOLD = float(MIN_THRESHOLD)
elif MIN_THRESHOLD:
    LOGGER.error(f"Invalid minimum threshold {MIN_THRESHOLD!r}. Defaulting to 4.5")
    MIN_THRESHOLD = 4.5

if MAX_THRESHOLD and MAX_THRESHOLD.isdigit():
    MAX_THRESHOLD = float(MAX_THRESHOLD)
elif MAX_THRESHOLD:
    LOGGER.error(f"Invalid max threshold {MAX_THRESHOLD!r}. Defaulting to None")
    MAX_THRESHOLD = None
