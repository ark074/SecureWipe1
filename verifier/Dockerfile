FROM python:3.11-slim
WORKDIR /app
COPY verifier /app/verifier
WORKDIR /app/verifier
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_APP=app
EXPOSE 5000
CMD ["flask","run","--host=0.0.0.0","--port=5000"]
