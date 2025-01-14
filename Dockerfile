FROM python:3.13
WORKDIR /code
COPY . .
CMD ["python", "./main.py"]