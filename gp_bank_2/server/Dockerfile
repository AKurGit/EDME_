FROM python:latest

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install -r requirements.txt

EXPOSE 1276

COPY . .

CMD ["python", "server.py"]