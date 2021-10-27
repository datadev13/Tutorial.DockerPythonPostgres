FROM python:3.9-slim


RUN /usr/local/bin/python -m pip install --upgrade pip
RUN mkdir /app && chmod 770 ./app
WORKDIR /app
COPY . /app
RUN pip install -r /app/requirements.txt
CMD [ "python", "/app/main.py" ]