# Mortgage Rate Monitor
A simple python script to run on a cron schedule to monitor mortgage rates and alert based on threshold

## Env Variables
- **GMAIL_USER**: Gmail account username or email address.
- **GMAIL_PASS**: Gmail account password for authentication.
- **RECIPIENT**: Email address of the recipient.

**Any one of the following is required**
- **MIN_THRESHOLD**: Threshold below when a notification has to be triggered.
- **MAX_THRESHOLD**: Threshold above when a notification has to be triggered.

### Optional:
*Refer [nerdwallet](https://www.nerdwallet.com/mortgages/mortgage-rates) for options*
- **TYPE_OF_RATE**: Defaults to `interest_rate`
- **TYPE_OF_MORTGAGE**: Defaults to `30_year_fixed_rate`
