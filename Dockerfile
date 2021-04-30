#FROM python:3.7.9-slim-buster
#
## set user and app home variables
#ENV USER=app
#ENV APP_HOME=/home/$USER/web
#ENV FLASK_APP app.py
#
## add user
## RUN adduser -D $USER
#RUN addgroup --system $USER && adduser --system --group $USER
#
## make user and app homes
#RUN mkdir $APP_HOME
#WORKDIR $APP_HOME
#
#
#
## install dependencies
#RUN apt-get update && apt-get install -y --no-install-recommends netcat
#
#RUN pip install --upgrade pip==21.1
#COPY ./requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#
#COPY . $APP_HOME
#RUN chown -R $USER:$USER $HOME
#
#USER $USER
#
#
#

FROM python:3.7-alpine

COPY requirements.txt requirements.txt
RUN apk update && \
    apk add --virtual build-deps gcc musl-dev && \
    apk add postgresql-dev && \
    rm -rf /var/cache/apk/*

RUN pip install -r requirements.txt

# delete dependencies required to install certain python packages
# so the docker image size is low enough for Zeit now
RUN apk del build-deps gcc musl-dev

COPY . /app
WORKDIR /app

# for the flask config
ENV FLASK_ENV=prod

EXPOSE 5000
ENTRYPOINT [ "gunicorn", "-b", "0.0.0.0:5000", "--log-level", "INFO", "manage:app" ]
