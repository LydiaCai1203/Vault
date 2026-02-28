#!/bin/bash
# Build agent images. Run from backend/
set -e
cd "$(dirname "$0")/.."
docker build -f agent_runtime/docker/Dockerfile.recorder -t vault-agent-recorder .
docker build -f agent_runtime/docker/Dockerfile.orchestrator -t vault-agent-orchestrator .
docker build -f agent_runtime/docker/Dockerfile.analyzer -t vault-agent-analyzer .
docker build -f agent_runtime/docker/Dockerfile.reporter -t vault-agent-reporter .
echo "Done. Images: vault-agent-{recorder,orchestrator,analyzer,reporter}"
