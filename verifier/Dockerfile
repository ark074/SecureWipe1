FROM python:3.11-slim

WORKDIR /app

# Copy only the contents of the verifier folder into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the Flask app entrypoint explicitly
ENV FLASK_APP=app.py

# Expose the default Flask port
EXPOSE 5000

# Launch the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
