# Base image
FROM python:3.7-slim

# Working directory
WORKDIR ./manager

# Copy files into the container
COPY ./manager .
COPY ./mongodb ./mongodb
COPY ./producers/producer.py ./producers/
COPY ./producers/__init__.py ./producers/
COPY ./consumers/consumer.py ./consumers/
COPY ./consumers/__init__.py ./consumers/

# Install dependencies
RUN pip3 install -r requirements.txt

CMD python3 -m manager
