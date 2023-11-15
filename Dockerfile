FROM python:3.9-slim

ENV LOG_HANDLER="stream"

RUN mkdir /opt/mortgage-rate-alert
COPY . /opt/mortgage-rate-alert

RUN /usr/local/bin/python3 -m pip install --upgrade pip

WORKDIR /opt/mortgage-rate-alert
RUN pip3 install --no-warn-script-location --user -r src/requirements.txt

ENTRYPOINT ["/usr/local/bin/python", "./src/main.py"]
