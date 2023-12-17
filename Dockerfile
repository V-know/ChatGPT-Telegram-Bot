FROM python:3.9-slim

ARG APP_HOME=/app
WORKDIR $APP_HOME

ADD . $APP_HOME

RUN pip install -r $APP_HOME/requirements.txt

ENTRYPOINT ["python", "main.py"]