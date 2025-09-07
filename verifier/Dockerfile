FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy verifier folder correctly
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r verifier/requirements.txt

# Set environment variables
ENV FLASK_APP=verifier/app.py

# Expose port
EXPOSE 5000

# Run Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
