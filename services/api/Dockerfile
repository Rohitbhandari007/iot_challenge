FROM python:3.11-slim

WORKDIR /app
COPY ./app ./
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
