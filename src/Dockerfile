FROM python:3.7.9-slim

# install some utils
RUN  apt-get update && apt-get install -y git ssh tar gzip ca-certificates

WORKDIR /app/

# install pipenv
RUN pip install pipenv

COPY ./Pipfile* /app/

# install dependencies
RUN pipenv install
COPY ./app /app
ENV PYTHONPATH=/app
EXPOSE 8000/udp
CMD pipenv run uvicorn main:app --host 0.0.0.0
