# Use debian linux to use python
FROM python:3.12.10-slim

WORKDIR /usr/src/app

# Install libs python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all data to workdir
COPY . .
