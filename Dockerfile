# Rust build stage
FROM rust:1.82 as builder
WORKDIR /usr/src/app
COPY backend ./backend
WORKDIR /usr/src/app/backend
RUN apt-get update && apt-get install -y pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*
RUN cargo build --release

# Final image
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ca-certificates libssl-dev wget && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/src/app/backend/target/release/securewipe_agent /usr/local/bin/securewipe_agent
COPY tools /opt/tools
COPY frontend /opt/frontend  # <-- copy frontend to match your main.rs path

WORKDIR /opt/tools
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/securewipe_agent"]
