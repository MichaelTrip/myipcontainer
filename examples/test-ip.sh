#!/bin/bash

echo "🧪 Testing IP Detection in Docker Container"
echo "==========================================="

# Start the services
echo "📦 Starting Docker Compose services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Test the IP detection
echo ""
echo "🔍 Testing IP detection:"
echo ""

echo "1. Testing with curl (should show your real IP):"
curl -s http://localhost:8080
echo ""

echo "2. Testing JSON endpoint:"
curl -s http://localhost:8080/json | jq -r '.client_ip // .client_ip'
echo ""

echo "3. Testing health check:"
curl -s http://localhost:8080/health | jq -r '.status // "ERROR"'
echo ""

echo "4. Checking nginx logs for X-Forwarded-For headers:"
docker-compose logs nginx | tail -5

echo ""
echo "✅ Test complete!"
echo ""
echo "📝 If you see your real external IP above, the fix worked!"
echo "   If you see 172.x.x.x or 192.168.x.x, there might still be an issue."
echo ""
echo "🛑 To stop the services: docker-compose down"