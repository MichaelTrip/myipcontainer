#!/usr/bin/env python3
"""
IP Address Display Web Server

A simple Flask web server that displays the client's IP address.
- Returns plain text for curl/API requests
- Returns fancy HTML for web browser requests
"""

from flask import Flask, request, render_template_string
import os
import socket
import datetime

app = Flask(__name__)

# HTML template for browser requests
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your IP Address</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: rgba(255, 255, 255, 0.95);
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 600px;
            width: 90%;
        }
        .ip-display {
            font-size: 3rem;
            font-weight: bold;
            color: #4a5568;
            margin: 1rem 0;
            padding: 1rem;
            background: #f7fafc;
            border-radius: 10px;
            border: 3px solid #e2e8f0;
            font-family: 'Courier New', monospace;
        }
        .info {
            color: #718096;
            margin: 0.5rem 0;
            font-size: 1.1rem;
        }
        .header {
            color: #2d3748;
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        .details {
            background: #edf2f7;
            padding: 1.5rem;
            border-radius: 10px;
            margin-top: 2rem;
            text-align: left;
        }
        .detail-row {
            display: flex;
            justify-content: space-between;
            margin: 0.5rem 0;
            padding: 0.5rem 0;
            border-bottom: 1px solid #cbd5e0;
        }
        .detail-label {
            font-weight: bold;
            color: #4a5568;
        }
        .detail-value {
            font-family: 'Courier New', monospace;
            color: #2d3748;
        }
        @media (max-width: 768px) {
            .container {
                padding: 2rem;
            }
            .ip-display {
                font-size: 2rem;
            }
            .header {
                font-size: 2rem;
            }
            .detail-row {
                flex-direction: column;
                gap: 0.25rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="header">🌐 Your IP Address</h1>
        <div class="ip-display">{{ client_ip }}</div>
        <p class="info">This is your public IP address as seen by this server</p>
        
        <div class="details">
            <div class="detail-row">
                <span class="detail-label">Client IP:</span>
                <span class="detail-value">{{ client_ip }}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Server Host:</span>
                <span class="detail-value">{{ server_host }}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Server Port:</span>
                <span class="detail-value">{{ server_port }}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Request Time:</span>
                <span class="detail-value">{{ timestamp }}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">User Agent:</span>
                <span class="detail-value">{{ user_agent }}</span>
            </div>
            {% if forwarded_for %}
            <div class="detail-row">
                <span class="detail-label">X-Forwarded-For:</span>
                <span class="detail-value">{{ forwarded_for }}</span>
            </div>
            {% endif %}
            {% if real_ip %}
            <div class="detail-row">
                <span class="detail-label">X-Real-IP:</span>
                <span class="detail-value">{{ real_ip }}</span>
            </div>
            {% endif %}
        </div>
        
        <div style="margin-top: 2rem; color: #718096; font-size: 0.9rem;">
            <p>💡 <strong>API Usage:</strong> Use <code>curl {{ request_url }}</code> for plain text output</p>
        </div>
    </div>
</body>
</html>
"""

def get_client_ip():
    """
    Get the real client IP address, handling various proxy headers
    """
    # Check for X-Forwarded-For header (most common proxy header)
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For can contain multiple IPs, get the first one
        forwarded_for = request.headers.get('X-Forwarded-For')
        client_ip = forwarded_for.split(',')[0].strip()
        return client_ip
    
    # Check for X-Real-IP header (nginx proxy)
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    
    # Check for CF-Connecting-IP header (Cloudflare)
    if request.headers.get('CF-Connecting-IP'):
        return request.headers.get('CF-Connecting-IP')
    
    # Fall back to remote_addr
    return request.remote_addr

def is_browser_request():
    """
    Determine if the request is from a web browser based on User-Agent
    """
    user_agent = request.headers.get('User-Agent', '').lower()
    
    # Common browser user agents contain these strings
    browser_indicators = [
        'mozilla', 'webkit', 'chrome', 'firefox', 'safari', 'edge', 'opera'
    ]
    
    # curl and similar tools typically don't have these indicators
    return any(indicator in user_agent for indicator in browser_indicators)

@app.route('/')
def show_ip():
    """
    Main endpoint that returns client IP
    - Returns JSON/plain text for API clients (curl, etc.)
    - Returns HTML for web browsers
    """
    client_ip = get_client_ip()
    
    # Check if this is a browser request or API request
    if is_browser_request() and 'application/json' not in request.headers.get('Accept', ''):
        # Return fancy HTML for browsers
        return render_template_string(HTML_TEMPLATE,
            client_ip=client_ip,
            server_host=socket.gethostname(),
            server_port=os.environ.get('PORT', '8080'),
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            user_agent=request.headers.get('User-Agent', 'Unknown'),
            forwarded_for=request.headers.get('X-Forwarded-For'),
            real_ip=request.headers.get('X-Real-IP'),
            request_url=request.url
        )
    else:
        # Return plain text for curl/API requests
        return f"{client_ip}\n", 200, {'Content-Type': 'text/plain'}

@app.route('/json')
def show_ip_json():
    """
    JSON API endpoint that always returns structured data
    """
    client_ip = get_client_ip()
    
    response_data = {
        'client_ip': client_ip,
        'server_host': socket.gethostname(),
        'server_port': int(os.environ.get('PORT', '8080')),
        'timestamp': datetime.datetime.now().isoformat() + 'Z',
        'headers': {
            'user_agent': request.headers.get('User-Agent'),
            'x_forwarded_for': request.headers.get('X-Forwarded-For'),
            'x_real_ip': request.headers.get('X-Real-IP'),
            'cf_connecting_ip': request.headers.get('CF-Connecting-IP')
        }
    }
    
    return response_data

@app.route('/health')
def health_check():
    """
    Health check endpoint for container orchestration
    """
    return {'status': 'healthy', 'timestamp': datetime.datetime.now().isoformat() + 'Z'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 Starting IP Display Server on {host}:{port}")
    print(f"🌐 Visit http://localhost:{port} in your browser")
    print(f"🔧 Or use: curl http://localhost:{port}")
    
    app.run(host=host, port=port, debug=debug)