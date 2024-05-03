FROM python:3.9
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY src/main.py /app/app.py
COPY src/jobs.py /app/jobs.py
COPY src/worker.py /app/worker.py
