# ------------------------------
# Stage 1: Build Rust backend
# ------------------------------
FROM rust:1.82 as builder

WORKDIR /usr/src/app

# Copy backend and frontend
COPY backend ./backend
COPY frontend ./frontend

WORKDIR /usr/src/app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*

# Build Rust backend in release mode
RUN cargo build --release

# ------------------------------
# Stage 2: Python runtime
# ------------------------------
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y ca-certificates libssl-dev wget && rm -rf /var/lib/apt/lists/*

# Copy Rust binary
COPY --from=builder /usr/src/app/backend/target/release/securewipe_agent /usr/local/bin/securewipe_agent

# Copy frontend files
COPY --from=builder /usr/src/app/frontend /opt/frontend

# Copy Python tools
COPY tools /opt/tools
WORKDIR /opt/tools
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Run backend binary
ENTRYPOINT ["/usr/local/bin/securewipe_agent"]
