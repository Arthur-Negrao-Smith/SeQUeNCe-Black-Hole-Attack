FROM  python:3.12.10

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

USER app

CMD ["python", "default_simulations.py"]

