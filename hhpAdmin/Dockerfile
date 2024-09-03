FROM python:3.12

ADD ./requirements.txt /deploy/
RUN python3 -m pip install --no-cache-dir -U -r /deploy/requirements.txt

WORKDIR /deploy
EXPOSE 6700