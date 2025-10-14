#!/bin/bash

# My IP Container - Docker Examples
# This script demonstrates various ways to run the IP container with Docker

echo "🐳 My IP Container - Docker Examples"
echo "====================================="

# Basic run
echo ""
echo "1. Basic Docker Run"
echo "docker run -d --name myipcontainer -p 8080:8080 ghcr.io/michaeltrip/myipcontainer:latest"
echo "Test with: curl http://localhost:8080"

# Custom port
echo ""
echo "2. Custom Port (3000)"
echo "docker run -d --name myipcontainer-3000 -p 3000:3000 -e PORT=3000 ghcr.io/michaeltrip/myipcontainer:latest"
echo "Test with: curl http://localhost:3000"

# With debug mode
echo ""
echo "3. Debug Mode"
echo "docker run -d --name myipcontainer-debug -p 8080:8080 -e DEBUG=true ghcr.io/michaeltrip/myipcontainer:latest"
echo "View logs: docker logs -f myipcontainer-debug"

# Multiple replicas with different ports
echo ""
echo "4. Multiple Replicas"
echo "docker run -d --name myipcontainer-1 -p 8081:8080 ghcr.io/michaeltrip/myipcontainer:latest"
echo "docker run -d --name myipcontainer-2 -p 8082:8080 ghcr.io/michaeltrip/myipcontainer:latest"
echo "docker run -d --name myipcontainer-3 -p 8083:8080 ghcr.io/michaeltrip/myipcontainer:latest"
echo "Test load balancing: curl http://localhost:808{1,2,3}"

# With network
echo ""
echo "5. Custom Network"
echo "docker network create myip-network"
echo "docker run -d --name myipcontainer --network myip-network -p 8080:8080 ghcr.io/michaeltrip/myipcontainer:latest"

# Docker Compose
echo ""
echo "6. Docker Compose (Recommended)"
echo "docker-compose up -d"
echo "docker-compose logs -f"

echo ""
echo "🧹 Cleanup Commands:"
echo "docker stop \$(docker ps -q --filter ancestor=ghcr.io/michaeltrip/myipcontainer:latest)"
echo "docker rm \$(docker ps -aq --filter ancestor=ghcr.io/michaeltrip/myipcontainer:latest)"
echo "docker-compose down"