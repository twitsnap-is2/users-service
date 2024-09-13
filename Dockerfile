FROM python:3.10.12-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY /src/ /app/

CMD ["uvicorn", "endpoint_app:app", "--port", "9212", "--host", "0.0.0.0", "--reload"]