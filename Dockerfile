FROM python:3.9-alpine

# setup musl-locale to gain basic support for locales in alpine
# creadit: https://grrr.tech/posts/2020/add-locales-to-alpine-linux-docker-image/
ENV MUSL_LOCALE_DEPS cmake make musl-dev gcc gettext-dev libintl 
ENV MUSL_LOCPATH /usr/share/i18n/locales/musl
RUN apk add --no-cache \
    $MUSL_LOCALE_DEPS \
    && wget https://gitlab.com/rilian-la-te/musl-locales/-/archive/master/musl-locales-master.zip \
    && unzip musl-locales-master.zip \
      && cd musl-locales-master \
      && cmake -DLOCALE_PROFILE=OFF -D CMAKE_INSTALL_PREFIX:PATH=/usr . && make && make install \
      && cd .. && rm -r musl-locales-master


#setup the afvalwijzer app environment
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy main script
COPY afvalwijzer.py /app/
# copy telegram_send config file. Do not change the config file name within the image 
COPY telegram-send.conf /app/telegram-send.conf

# below is to make sure the single file mapping for afvalwijzer.log works
# be sure upfront to create an empty afvalwijzer.log in the app directory on docker host
COPY afvalwijzer.log /app/
RUN touch /app/afvalwijzer.log

# copy crontabs for root user
COPY cronjobs /etc/crontabs/root

# start crond with log level 8 in foreground, output to stderr
CMD ["crond", "-f", "-d", "8"]