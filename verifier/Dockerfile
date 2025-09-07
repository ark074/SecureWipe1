FROM python:3.11-slim

WORKDIR /app

# Copy only the verifier directory contents
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app.py
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
