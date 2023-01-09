FROM python:3.9-slim

RUN mkdir /opt/mortgage-rate-alert
COPY src/ /opt/mortgage-rate-alert

RUN /usr/local/bin/python3 -m pip install --upgrade pip
RUN cd /opt/mortgage-rate-alert && pip3 install --no-warn-script-location --user -r requirements.txt

WORKDIR /opt/mortgage-rate-alert

ENTRYPOINT ["/usr/local/bin/python", "./main.py"]
