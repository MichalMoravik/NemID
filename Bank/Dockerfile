FROM alpine:latest

RUN apk add --update --no-cache build-base python3-dev python3 \
 && apk add py3-pip \
 && apk add vim

WORKDIR /app

COPY . /app

RUN pip3 --no-cache-dir install -r requirements.txt

EXPOSE 5000

ENTRYPOINT  ["python3"]

CMD ["app.py"]