FROM python:3.9.16-slim

ENV PYTHONBUFFERED 1
ENV PYTHONWRITEBYTECODE 1

RUN apt-get update \
    && apt-get install -y netcat

ENV APP=/app

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/bin/bash","/app/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

