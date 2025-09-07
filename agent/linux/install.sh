#!/bin/bash
set -e
echo "Installing SecureWipe agent (Linux)"
sudo mkdir -p /etc/securewipe /var/lib/securewipe /usr/local/bin
echo "Copy the built binary to /usr/local/bin/securewipe_agent and place config at /etc/securewipe/config.yaml"
echo "Enable and start systemd service: sudo systemctl enable --now securewipe-agent"
