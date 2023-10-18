FROM ubuntu:22.04

# updating and installing python3 and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install poetry && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copying all the file to /app
COPY . /app

RUN poetry config virtualenvs.create false && \
    poetry install --no-dev

CMD ["python3", "store_management_system/server.py"]
