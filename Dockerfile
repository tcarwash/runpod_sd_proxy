FROM python:3.11-alpine

COPY runpod_sd_proxy /runpod_sd_proxy

RUN mkdir /data

COPY requirements.txt /

RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt

RUN python -m pip install gunicorn

CMD ["gunicorn", "-b", "0.0.0.0:9080", "runpod_sd_proxy:app"]
