FROM python:3.9-alpine

LABEL maintainer="carl.wilson@openpreservation.org" \
      org.openpreservation.vendor="Open Preservation Foundation" \
      version="0.1"

RUN  apk update && apk --no-cache --update-cache add gcc build-base libxml2-dev libxslt-dev git

WORKDIR /src

COPY requirements.txt /src/requirements.txt
RUN pip install -U pip && pip install -U -r /src/requirements.txt
COPY ./fidosigs /src/fidosigs

RUN adduser --uid 1000 -h /opt/fidosigs -S fidosig

USER fidosig

EXPOSE 80
ENTRYPOINT uvicorn fidosigs.main:APP --host 0.0.0.0 --port 80
