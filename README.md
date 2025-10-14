# My IP Container 🌐

A simple, lightweight Python web server that displays the client's IP address. Perfect for testing load balancers, proxies, and container networking.

## Features

- 🌐 **Dual Interface**: Shows fancy HTML for browsers, plain text for curl/API clients
- 🔍 **Smart IP Detection**: Handles various proxy headers (X-Forwarded-For, X-Real-IP, CF-Connecting-IP)
- 🌍 **IP Geolocation**: Shows location, country flag, timezone, and ISP information
- 🎨 **Modern UI**: Light/dark mode with responsive design optimized for IPv6 addresses
- 🐳 **Container Ready**: Multi-architecture Docker image (AMD64, ARM64)
- ⚡ **Production Ready**: Uses Gunicorn with optimal settings
- 🏥 **Health Checks**: Built-in health check endpoint
- 📊 **Detailed Info**: Shows headers, timestamps, and server details
- 🔒 **Secure**: Runs as non-root user in container

## Quick Start

### Docker

```bash
# Run the container
docker run -p 8080:8080 ghcr.io/michaeltrip/myipcontainer:latest

# Visit in browser
open http://localhost:8080

# Or use curl for plain text
curl http://localhost:8080
```

### Docker Compose

```bash
# Start with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### Kubernetes

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/

# Get service URL
kubectl get services myipcontainer
```

## Usage Examples

### Browser Access
Visit `http://localhost:8080` in your web browser to see a modern HTML interface with:
- 🔢 **Large IP display** - Optimized for both IPv4 and IPv6 addresses
- 🌍 **Location details** - Country flag, city, ISP, and timezone information
- 🎨 **Light/Dark mode** - Automatic system theme detection with manual toggle
- 📱 **Responsive design** - Works perfectly on desktop, tablet, and mobile
- 🎯 **Smart layout** - IPv6 addresses wrap properly and remain readable

### API Access
Use curl or any HTTP client for programmatic access:

```bash
# Get full info with location and ISP
curl http://localhost:8080
# Output: 
# IP: 203.0.113.42
# Location: 🇺🇸 New York, New York, United States
# ISP: Example ISP Corp
# Organization: Example Organization
# Timezone: America/New_York

# Get just IP address (compact mode)
curl http://localhost:8080?compact=true
# Output: 203.0.113.42

# Get JSON response with all details
curl http://localhost:8080/json
# Output: {"client_ip": "203.0.113.42", "geolocation": {...}, ...}

# Health check
curl http://localhost:8080/health
# Output: {"status": "healthy", "timestamp": "2025-10-14T..."}
```

## API Endpoints

| Endpoint | Description | Response Format |
|----------|-------------|-----------------|
| `/` | Main endpoint - HTML for browsers, enhanced text for curl | HTML/Text |
| `/?compact=true` | Compact mode - returns only IP address | Text |
| `/json` | Always returns JSON with geolocation | JSON |
| `/health` | Health check for monitoring | JSON |
| `/debug` | Debug info with headers and geolocation | JSON |

## Geolocation Features

The application automatically detects the geographic location of public IP addresses and displays:

- 🌍 **Country and city** with flag emoji
- 📍 **Coordinates** (latitude, longitude)  
- 🕐 **Timezone** information
- 🌐 **ISP and organization** details
- 🏠 **Private network detection** (no geolocation for local IPs)

**Privacy Notes:**
- Geolocation only works for public IP addresses
- Private/local IPs (192.168.x.x, 10.x.x.x, etc.) show "Local/Private Network"
- Uses free ip-api.com service (no API key required)
- Can be disabled by setting `ENABLE_GEOLOCATION=false`

## Visitor Logging

The application logs detailed visitor information to stdout for monitoring and analytics:

**Log Format:**
```
📍 [2025-10-14 10:30:15 UTC] VISITOR: 203.0.113.42 | 🇺🇸 New York, United States | ISP: Example ISP | ORG: Example Corp | TYPE: browser | UA: Mozilla/5.0 (Windows NT 10.0; Win64; x64)...
🏠 [2025-10-14 10:31:22 UTC] VISITOR: 192.168.1.100 | Local/Private Network | TYPE: api | UA: curl/7.68.0...
```

**Logged Information:**
- 📅 **Timestamp** - Request time in UTC
- 🌐 **IP Address** - Client's detected IP
- 🌍 **Location** - Country flag, city, and country (for public IPs)
- 🏢 **ISP/Organization** - Internet service provider details
- 📱 **Request Type** - browser, api, json
- 🔧 **User Agent** - Client information (first 50 characters)

**Configuration:**
- Enable/disable with `LOG_VISITORS=true/false`
- Logs are sent to stdout for container log aggregation
- Also logged to Flask's structured logger for external log systems

## Configuration

The application can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | Port to listen on |
| `HOST` | `0.0.0.0` | Host to bind to |
| `DEBUG` | `false` | Enable debug mode |
| `TRUST_PROXY` | `false` | Trust proxy headers for IP detection |
| `ENABLE_GEOLOCATION` | `true` | Enable IP geolocation lookup |
| `LOG_VISITORS` | `true` | Log visitor IP, location, and ISP info to stdout |
| `TRUST_PROXY` | `false` | Enable proxy header parsing (X-Forwarded-For, X-Real-IP) |

### Docker Environment Variables

```bash
# Direct access (default)
docker run -p 8080:8080 \
  -e PORT=3000 \
  -e DEBUG=true \
  ghcr.io/michaeltrip/myipcontainer:latest

# Behind reverse proxy (nginx, traefik, etc.)
docker run -p 8080:8080 \
  -e TRUST_PROXY=true \
  ghcr.io/michaeltrip/myipcontainer:latest
```

**⚠️ Security Note**: Only set `TRUST_PROXY=true` when the container is actually behind a trusted reverse proxy. This enables parsing of X-Forwarded-For headers which can be spoofed by clients if not properly filtered by a proxy.

### Kubernetes Environment Variables

```yaml
env:
  - name: PORT
    value: "8080"
  - name: DEBUG
    value: "false"
```

## Deployment Examples

### Docker

#### Simple Run
```bash
docker run -d --name myipcontainer -p 8080:8080 ghcr.io/michaeltrip/myipcontainer:latest
```

#### With Custom Port
```bash
docker run -d --name myipcontainer -p 3000:3000 -e PORT=3000 ghcr.io/michaeltrip/myipcontainer:latest
```

#### With Volume for Logs
```bash
docker run -d --name myipcontainer \
  -p 8080:8080 \
  -v $(pwd)/logs:/app/logs \
  ghcr.io/michaeltrip/myipcontainer:latest
```

### Docker Compose

See [`examples/docker-compose.yml`](examples/docker-compose.yml) for a complete example with:
- Environment variable configuration
- Volume mounts
- Network configuration
- Health checks

### Kubernetes

The `k8s/` directory contains complete Kubernetes manifests:

- **Deployment**: Multi-replica deployment with health checks
- **Service**: ClusterIP service for internal access
- **Ingress**: Optional ingress for external access with TLS

#### Basic Deployment
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

#### With Ingress
```bash
kubectl apply -f k8s/ingress.yaml
```

#### With Custom Namespace
```bash
kubectl create namespace ip-checker
kubectl apply -f k8s/ -n ip-checker
```

## Development

### Local Development

```bash
# Clone the repository
git clone https://github.com/MichaelTrip/myipcontainer.git
cd myipcontainer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Building the Container

```bash
# Build locally
docker build -t myipcontainer .

# Run your build
docker run -p 8080:8080 myipcontainer

# Build for multiple architectures
docker buildx build --platform linux/amd64,linux/arm64 -t myipcontainer .
```

### Testing

```bash
# Test with curl
curl http://localhost:8080

# Test JSON endpoint
curl http://localhost:8080/json | jq

# Test health endpoint
curl http://localhost:8080/health
```

## Use Cases

- **Load Balancer Testing**: Verify which backend server is handling requests
- **Proxy Configuration**: Test if proxy headers are being passed correctly
- **Network Debugging**: Check client IP detection in different network setups
- **Container Networking**: Verify service discovery and networking in Kubernetes
- **CI/CD Testing**: Simple service for testing deployment pipelines
- **Learning Tool**: Understand how HTTP headers work in containerized environments

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Load Balancer  │    │  My IP Container│
│                 │────▶│     /Proxy       │────▶│                 │
│                 │    │                  │    │   Python Flask  │
└─────────────────┘    └──────────────────┘    │   + Gunicorn    │
                                               │                 │
┌─────────────────┐                            │   Port 8080     │
│   curl/API      │────────────────────────────▶│                 │
│   Client        │                            └─────────────────┘
└─────────────────┘
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `chore:` for maintenance tasks

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/MichaelTrip/myipcontainer/issues)
- 📖 **Documentation**: This README and inline code comments
- 💬 **Discussions**: [GitHub Discussions](https://github.com/MichaelTrip/myipcontainer/discussions)

## Related Projects

- [lmsensors-container](https://github.com/MichaelTrip/lmsensors-container) - Hardware sensor monitoring for Kubernetes

---

Made with ❤️ by [MichaelTrip](https://github.com/MichaelTrip)