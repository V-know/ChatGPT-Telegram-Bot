FROM python:3.9-slim

LABEL org.opencontainers.image.source=https://github.com/V-know/ChatGPT-Telegram-Bot

ARG APP_HOME=/app
WORKDIR $APP_HOME

ADD . $APP_HOME

RUN pip install cryptography && pip install -r $APP_HOME/requirements.txt
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

ENTRYPOINT ["python", "main.py"]