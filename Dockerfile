FROM python:3-slim

COPY ./findmyoctoprint_server /app
COPY requirements.txt /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD [ "python", "__init__.py" ]
