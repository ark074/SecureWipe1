# Rust build stage
FROM rust:1.82 AS builder
WORKDIR /usr/src/app

# Copy backend code
COPY backend ./backend
WORKDIR /usr/src/app/backend

# Install Rust build dependencies
RUN apt-get update && apt-get install -y pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*

# Build release binary
RUN cargo build --release

# Final image
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates libssl-dev wget \
    && rm -rf /var/lib/apt/lists/*

# Copy Rust binary from builder
COPY --from=builder /usr/src/app/backend/target/release/securewipe_agent /usr/local/bin/securewipe_agent

# Copy Python tools
COPY tools /opt/tools

WORKDIR /opt/tools
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/securewipe_agent"]
