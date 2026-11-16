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
import requests
import json
import subprocess

app = Flask(__name__)


def is_env_var_enabled(name, default='false'):
    """
    Return True when the named environment variable is explicitly enabled.
    """
    return os.environ.get(name, default).lower() == 'true'


def is_reverse_dns_enabled():
    """
    Return whether reverse DNS lookups are enabled.
    """
    return is_env_var_enabled('ENABLE_REVERSE_DNS', 'true')

# HTML template for browser requests
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your IP Address</title>
    <script>
        // Apply the preferred appearance before the page is painted.
        function readTheme() {
            try { return localStorage.getItem('theme'); } catch { return null; }
        }
        const systemTheme = window.matchMedia('(prefers-color-scheme: dark)');
        const storedTheme = readTheme();
        document.documentElement.dataset.theme =
            storedTheme === 'light' || storedTheme === 'dark'
                ? storedTheme : (systemTheme.matches ? 'dark' : 'light');
    </script>
    <style>
        :root {
            color-scheme: light;
            --bg-color: #f0f4f8;
            --container-bg: #ffffff;
            --text-primary: #2d3748;
            --text-secondary: #4a5568;
            --text-muted: #52647a;
            --border-color: #d8e0e9;
            --ip-bg: #f7fafc;
            --button-bg: #246aa4;
            --button-hover: #1e5787;
        }

        [data-theme="dark"] {
            color-scheme: dark;
            --bg-color: #1a202c;
            --container-bg: #2d3748;
            --text-primary: #f7fafc;
            --text-secondary: #e2e8f0;
            --text-muted: #bac6d6;
            --border-color: #526078;
            --ip-bg: #263141;
            --button-bg: #246aa4;
            --button-hover: #1e5787;
        }

        * { box-sizing: border-box; }
        body {
            margin: 0;
            padding: 5rem 1.5rem 2rem;
            background: var(--bg-color);
            color: var(--text-primary);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.5;
        }
        .container {
            width: 100%;
            max-width: 60rem;
            margin: 0 auto;
            padding: 2rem 3rem;
            background: var(--container-bg);
            border-radius: 8px;
        }
        .theme-toggle {
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 1;
            min-height: 44px;
            padding: 0.5rem 1rem;
            border: 1px solid transparent;
            border-radius: 6px;
            background: var(--button-bg);
            color: #fff;
            font: inherit;
            cursor: pointer;
        }
        .theme-toggle:hover { background: var(--button-hover); }
        .theme-toggle:active { border-color: #fff; }
        :focus-visible { outline: 3px solid var(--text-primary); outline-offset: 4px; }
        .header { margin: 0; font-size: 1.25rem; font-weight: 600; }
        .ip-display {
            margin: 0.75rem 0;
            font-family: 'Courier New', monospace;
            font-size: clamp(1.5rem, 3.5vw, 2.25rem);
            font-weight: 600;
            line-height: 1.4;
            overflow-wrap: anywhere;
            font-variant-numeric: tabular-nums;
            user-select: all;
        }
        .info { margin: 0; color: var(--text-muted); }
        .details { margin: 2rem 0; }
        .detail-row {
            display: grid;
            grid-template-columns: 10rem minmax(0, 1fr);
            gap: 1rem;
            padding: 0.75rem 0;
            border-bottom: 1px solid var(--border-color);
        }
        .detail-row:first-child { border-top: 1px solid var(--border-color); }
        .detail-label { color: var(--text-secondary); font-weight: 600; }
        .detail-value {
            margin: 0;
            min-width: 0;
            font-family: 'Courier New', monospace;
            overflow-wrap: anywhere;
            font-variant-numeric: tabular-nums;
        }
        .api-usage { margin-top: 2rem; }
        .api-usage h2 { margin: 0 0 1rem; font-size: 1.125rem; font-weight: 600; }
        .api-usage p { margin: 0 0 1rem; }
        .api-usage span { display: block; margin-bottom: 0.25rem; color: var(--text-secondary); }
        .api-usage code {
            display: block;
            padding: 0.75rem 1rem;
            background: var(--ip-bg);
            border-left: 2px solid var(--border-color);
            font: 1rem/1.5 'Courier New', monospace;
            white-space: pre;
            overflow-x: auto;
        }
        .footer {
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-color);
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 0.75rem 1.5rem;
            color: var(--text-muted);
        }
        .github-link {
            display: inline-flex;
            align-items: center;
            min-height: 44px;
            color: var(--text-secondary);
            text-underline-offset: 4px;
        }
        .github-link:hover { color: var(--text-primary); }
        .github-logo { width: 20px; height: 20px; margin-right: 8px; fill: currentColor; }
        .version-info { font: 0.875rem/1.5 'Courier New', monospace; overflow-wrap: anywhere; }
        @media (max-width: 600px) {
            body { padding: 5rem 0 0; }
            .container { padding: 1.5rem; border-radius: 0; }
            .detail-row { grid-template-columns: minmax(0, 1fr); gap: 0.25rem; }
        }
        @media print {
            body { padding: 0; }
            .container { max-width: none; padding: 0; }
            .theme-toggle { display: none; }
        }
    </style>
</head>
<body>
    <button class="theme-toggle" type="button" onclick="toggleTheme()" id="themeToggle" aria-label="Switch to dark mode">
        Dark mode
    </button>
    
    <main class="container">
        <h1 class="header">Your IP address</h1>
        <div class="ip-display">{% for group in client_ip.split(':') %}{{ group }}{% if not loop.last %}:<wbr>{% endif %}{% endfor %}</div>
        <p class="info">Client address seen by this server</p>
        
        <dl class="details" aria-label="Connection details">
            <div class="detail-row">
                <dt class="detail-label">Client IP:</dt>
                <dd class="detail-value">{{ client_ip }}</dd>
            </div>
            {% if reverse_dns %}
            <div class="detail-row">
                <dt class="detail-label">Reverse DNS:</dt>
                <dd class="detail-value">{{ reverse_dns }}</dd>
            </div>
            {% endif %}
            {% if geolocation %}
            <div class="detail-row">
                <dt class="detail-label">Location:</dt>
                <dd class="detail-value">{{ geolocation.flag_emoji }} {{ geolocation.city }}, {{ geolocation.region }}, {{ geolocation.country }}</dd>
            </div>
            <div class="detail-row">
                <dt class="detail-label">Coordinates:</dt>
                <dd class="detail-value">{{ geolocation.latitude }}, {{ geolocation.longitude }}</dd>
            </div>
            <div class="detail-row">
                <dt class="detail-label">Timezone:</dt>
                <dd class="detail-value">{{ geolocation.timezone }}</dd>
            </div>
            <div class="detail-row">
                <dt class="detail-label">ISP:</dt>
                <dd class="detail-value">{{ geolocation.isp }}</dd>
            </div>
            {% if geolocation.org and geolocation.org != geolocation.isp %}
            <div class="detail-row">
                <dt class="detail-label">Organization:</dt>
                <dd class="detail-value">{{ geolocation.org }}</dd>
            </div>
            {% endif %}
            {% else %}
            <div class="detail-row">
                <dt class="detail-label">Location:</dt>
                <dd class="detail-value">Unavailable (local address, disabled, or lookup failed)</dd>
            </div>
            {% endif %}
            <div class="detail-row">
                <dt class="detail-label">Server Host:</dt>
                <dd class="detail-value">{{ server_host }}</dd>
            </div>
            <div class="detail-row">
                <dt class="detail-label">Server Port:</dt>
                <dd class="detail-value">{{ server_port }}</dd>
            </div>
            <div class="detail-row">
                <dt class="detail-label">Request Time:</dt>
                <dd class="detail-value">{{ timestamp }}</dd>
            </div>
            <div class="detail-row">
                <dt class="detail-label">User Agent:</dt>
                <dd class="detail-value">{{ user_agent }}</dd>
            </div>
            {% if forwarded_for %}
            <div class="detail-row">
                <dt class="detail-label">X-Forwarded-For:</dt>
                <dd class="detail-value">{{ forwarded_for }}</dd>
            </div>
            {% endif %}
            {% if real_ip %}
            <div class="detail-row">
                <dt class="detail-label">X-Real-IP:</dt>
                <dd class="detail-value">{{ real_ip }}</dd>
            </div>
            {% endif %}
        </dl>

        <section class="api-usage" aria-labelledby="api-heading">
            <h2 id="api-heading">Use from the command line</h2>
            <p><span>Full info, including available location and ISP</span><code tabindex="0">curl {{ base_url }}</code></p>
            <p><span>IP address only</span><code tabindex="0">curl {{ base_url }}?compact=true</code></p>
            <p><span>JSON response</span><code tabindex="0">curl {{ base_url }}/json</code></p>
        </section>

        <div class="footer">
            <a href="https://github.com/MichaelTrip/myipcontainer" target="_blank" rel="noopener noreferrer" class="github-link">
                <svg class="github-logo" viewBox="0 0 16 16" aria-hidden="true">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                </svg>
                GitHub
            </a>
            <div class="version-info">
                {{ version_info.version }} ({{ version_info.commit }}) • {{ version_info.build_date }}
            </div>
        </div>
    </main>
    
    <script>
        function updateThemeToggle(theme) {
            const toggle = document.getElementById('themeToggle');
            const label = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
            toggle.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
            toggle.setAttribute('aria-label', label);
            toggle.title = label;
        }

        function toggleTheme() {
            const newTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
            document.documentElement.dataset.theme = newTheme;
            try { localStorage.setItem('theme', newTheme); } catch { /* Appearance still works without storage. */ }
            updateThemeToggle(newTheme);
        }

        systemTheme.addEventListener('change', (event) => {
            if (!readTheme()) {
                const theme = event.matches ? 'dark' : 'light';
                document.documentElement.dataset.theme = theme;
                updateThemeToggle(theme);
            }
        });
        updateThemeToggle(document.documentElement.dataset.theme);
    </script>
</body>
</html>
"""

def get_base_url():
    """
    Get the base URL for the current request, handling proxies
    """
    scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
    host = request.headers.get('X-Forwarded-Host', request.headers.get('Host', request.host))
    return f"{scheme}://{host}"

def get_ip_geolocation(ip_address):
    """
    Get geolocation information for an IP address using ip-api.com (free service)
    Returns None if IP is private/local or if lookup fails
    """
    # Check if geolocation is enabled
    if os.environ.get('ENABLE_GEOLOCATION', 'true').lower() != 'true':
        return None
        
    # Skip geolocation for private/local IPs
    if (ip_address.startswith('127.') or 
        ip_address.startswith('192.168.') or 
        ip_address.startswith('10.') or 
        ip_address.startswith('172.') or
        ip_address == 'localhost' or
        '::1' in ip_address):
        return None
    
    try:
        # Use ip-api.com free service (no API key required)
        response = requests.get(
            f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,region,regionName,city,lat,lon,timezone,isp,org",
            timeout=3
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'country': data.get('country'),
                    'country_code': data.get('countryCode'),
                    'region': data.get('regionName'),
                    'city': data.get('city'),
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon'),
                    'timezone': data.get('timezone'),
                    'isp': data.get('isp'),
                    'org': data.get('org'),
                    'flag_emoji': get_flag_emoji(data.get('countryCode', ''))
                }
    except Exception as e:
        print(f"Geolocation lookup failed: {e}")
    
    return None

def get_flag_emoji(country_code):
    """
    Convert country code to flag emoji
    """
    if not country_code or len(country_code) != 2:
        return ""
    
    # Convert country code to flag emoji using Unicode regional indicator symbols
    return ''.join(chr(ord(c) + 127397) for c in country_code.upper())

def get_reverse_dns(ip_address):
    """
    Perform reverse DNS lookup for an IP address
    Returns the hostname if found, None if lookup fails
    """
    # Check if reverse DNS is enabled
    if not is_reverse_dns_enabled():
        return None
        
    try:
        # Perform reverse DNS lookup with timeout
        socket.setdefaulttimeout(3)  # 3 second timeout
        hostname, _, _ = socket.gethostbyaddr(ip_address)
        return hostname
    except (socket.herror, socket.gaierror, socket.timeout) as e:
        # DNS lookup failed or timed out
        return None
    except Exception as e:
        print(f"Reverse DNS lookup failed: {e}")
        return None
    finally:
        # Reset socket timeout to default
        socket.setdefaulttimeout(None)

def get_version_info():
    """
    Get version information from git or environment variables
    """
    version_info = {
        'version': 'unknown',
        'commit': 'unknown',
        'build_date': 'unknown'
    }
    
    try:
        # Try to get version from git tag
        git_tag = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0'], 
                                        stderr=subprocess.DEVNULL, cwd=os.path.dirname(__file__)).decode().strip()
        version_info['version'] = git_tag
    except:
        # Fallback to environment variable or default
        version_info['version'] = os.environ.get('APP_VERSION', 'v1.0.0')
    
    try:
        # Try to get commit hash
        git_commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], 
                                           stderr=subprocess.DEVNULL, cwd=os.path.dirname(__file__)).decode().strip()
        version_info['commit'] = git_commit
    except:
        version_info['commit'] = os.environ.get('GIT_COMMIT', 'unknown')[:7]
    
    # Get build date from environment or current date
    version_info['build_date'] = os.environ.get('BUILD_DATE', datetime.datetime.now().strftime('%Y-%m-%d'))
    
    return version_info

def log_visitor_info(client_ip, geolocation, user_agent, request_type="web"):
    """
    Log visitor information to stdout with IP, location, and ISP details
    """
    # Check if visitor logging is enabled
    if not is_env_var_enabled('LOG_VISITORS', 'true'):
        return
        
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    if geolocation:
        location_str = f"{geolocation.get('city', 'Unknown')}, {geolocation.get('country', 'Unknown')}"
        isp_str = geolocation.get('isp', 'Unknown ISP')
        org_str = geolocation.get('org', 'Unknown Org')
        flag = geolocation.get('flag_emoji', '')
        
        print(f"📍 [{timestamp}] VISITOR: {client_ip} | {flag} {location_str} | ISP: {isp_str} | ORG: {org_str} | TYPE: {request_type} | UA: {user_agent[:50]}...")
    else:
        print(f"🏠 [{timestamp}] VISITOR: {client_ip} | Local/Private Network | TYPE: {request_type} | UA: {user_agent[:50]}...")
    
    # Also log to Flask's default logger for structured logging
    app.logger.info(f"Client visit: IP={client_ip}, Location={location_str if geolocation else 'Local'}, ISP={isp_str if geolocation else 'N/A'}, Type={request_type}")

def get_client_ip():
    """
    Get the real client IP address, handling various proxy headers
    """
    trust_proxy = is_env_var_enabled('TRUST_PROXY')
    
    # If TRUST_PROXY is enabled, check proxy headers
    if trust_proxy:
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
    
    # For direct connections or when TRUST_PROXY=false, use remote_addr
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
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Check if this is a browser request or API request
    if is_browser_request() and 'application/json' not in request.headers.get('Accept', ''):
        # Get geolocation and reverse DNS for browser requests
        geolocation = get_ip_geolocation(client_ip)
        reverse_dns = get_reverse_dns(client_ip)
        
        # Log visitor information
        log_visitor_info(client_ip, geolocation, user_agent, "browser")
        
        # Get version information
        version_info = get_version_info()
        
        # Return fancy HTML for browsers
        return render_template_string(HTML_TEMPLATE,
            client_ip=client_ip,
            geolocation=geolocation,
            reverse_dns=reverse_dns,
            server_host=socket.gethostname(),
            server_port=os.environ.get('PORT', '8080'),
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            user_agent=user_agent,
            forwarded_for=request.headers.get('X-Forwarded-For'),
            real_ip=request.headers.get('X-Real-IP'),
            base_url=get_base_url(),
            version_info=version_info
        )
    else:
        # Get geolocation and reverse DNS for API requests too (for logging)
        geolocation = get_ip_geolocation(client_ip)
        reverse_dns = get_reverse_dns(client_ip)
        
        # Log visitor information
        log_visitor_info(client_ip, geolocation, user_agent, "api")
        
        # Check if compact mode is requested
        compact = request.args.get('compact', 'false').lower() == 'true'
        
        if compact:
            # Return just the IP for compact mode
            return f"{client_ip}\n", 200, {'Content-Type': 'text/plain'}
        
        # Return enhanced plain text for curl/API requests
        response_lines = [f"IP: {client_ip}"]
        
        if reverse_dns:
            response_lines.append(f"Reverse DNS: {reverse_dns}")
        
        if geolocation:
            location = f"{geolocation.get('city', 'Unknown')}, {geolocation.get('region', 'Unknown')}, {geolocation.get('country', 'Unknown')}"
            response_lines.append(f"Location: {geolocation.get('flag_emoji', '')} {location}")
            
            if geolocation.get('isp'):
                response_lines.append(f"ISP: {geolocation.get('isp')}")
            
            if geolocation.get('org') and geolocation.get('org') != geolocation.get('isp'):
                response_lines.append(f"Organization: {geolocation.get('org')}")
                
            if geolocation.get('timezone'):
                response_lines.append(f"Timezone: {geolocation.get('timezone')}")
        else:
            response_lines.append("Location: Local/Private Network")
        
        return "\n".join(response_lines) + "\n", 200, {'Content-Type': 'text/plain'}

@app.route('/json')
def show_ip_json():
    """
    JSON API endpoint that always returns structured data
    """
    client_ip = get_client_ip()
    geolocation = get_ip_geolocation(client_ip)
    reverse_dns = get_reverse_dns(client_ip)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Log visitor information
    log_visitor_info(client_ip, geolocation, user_agent, "json")
    
    response_data = {
        'client_ip': client_ip,
        'reverse_dns': reverse_dns,
        'geolocation': geolocation,
        'server_host': socket.gethostname(),
        'server_port': int(os.environ.get('PORT', '8080')),
        'timestamp': datetime.datetime.now().isoformat() + 'Z',
        'headers': {
            'user_agent': user_agent,
            'x_forwarded_for': request.headers.get('X-Forwarded-For'),
            'x_real_ip': request.headers.get('X-Real-IP'),
            'cf_connecting_ip': request.headers.get('CF-Connecting-IP')
        }
    }
    
    return response_data

@app.route('/debug')
def debug():
    """
    Debug endpoint to show all request headers and IP detection
    """
    client_ip = get_client_ip()
    trust_proxy = is_env_var_enabled('TRUST_PROXY')
    enable_geolocation = is_env_var_enabled('ENABLE_GEOLOCATION', 'true')
    enable_reverse_dns = is_reverse_dns_enabled()
    geolocation = get_ip_geolocation(client_ip) if enable_geolocation else None
    reverse_dns = get_reverse_dns(client_ip) if enable_reverse_dns else None
    
    debug_info = {
        'detected_ip': client_ip,
        'remote_addr': request.remote_addr,
        'trust_proxy': trust_proxy,
        'enable_geolocation': enable_geolocation,
        'enable_reverse_dns': enable_reverse_dns,
        'geolocation': geolocation,
        'reverse_dns': reverse_dns,
        'proxy_headers': {
            'X-Forwarded-For': request.headers.get('X-Forwarded-For'),
            'X-Real-IP': request.headers.get('X-Real-IP'),
            'CF-Connecting-IP': request.headers.get('CF-Connecting-IP'),
        },
        'all_headers': dict(request.headers),
        'request_info': {
            'method': request.method,
            'path': request.path,
            'query_string': request.query_string.decode(),
            'scheme': request.scheme,
            'host': request.host,
            'remote_addr': request.remote_addr,
        }
    }
    
    return debug_info

@app.route('/health')
def health_check():
    """
    Health check endpoint for container orchestration
    """
    return {'status': 'healthy', 'timestamp': datetime.datetime.now().isoformat() + 'Z'}

@app.route('/version')
def version():
    """
    Version information endpoint
    """
    return get_version_info()

def get_local_urls(host, port):
    """
    Get the local URLs where the server can be accessed
    """
    urls = []
    
    if host in ['0.0.0.0', '::']:
        # Server is listening on all interfaces (IPv4 and/or IPv6)
        urls.append(f"http://localhost:{port}")
        
        # Try to get the actual IP addresses (IPv4 and IPv6)
        try:
            import socket
            hostname = socket.gethostname()
            
            # Get IPv4 address
            try:
                local_ipv4 = socket.gethostbyname(hostname)
                if local_ipv4 != '127.0.0.1':
                    urls.append(f"http://{local_ipv4}:{port}")
            except:
                pass
            
            # Get IPv6 addresses
            try:
                addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET6)
                for info in addr_info:
                    ipv6_addr = info[4][0]
                    # Skip loopback and link-local addresses
                    if not ipv6_addr.startswith('::1') and not ipv6_addr.startswith('fe80'):
                        urls.append(f"http://[{ipv6_addr}]:{port}")
                        break  # Just add the first valid IPv6 address
            except:
                pass
                
        except:
            pass
            
        # Add common Docker internal IP if it looks like we're in a container
        if os.path.exists('/.dockerenv'):
            try:
                # Get the container's IP in the Docker network
                result = os.popen("hostname -i").read().strip()
                if result and result != '127.0.0.1':
                    # Handle both IPv4 and IPv6 addresses from hostname -i
                    for ip in result.split():
                        if ':' in ip and not ip.startswith('::1'):
                            urls.append(f"http://[{ip}]:{port}")
                        elif '.' in ip and ip != '127.0.0.1':
                            urls.append(f"http://{ip}:{port}")
            except:
                pass
    else:
        # Specific host binding
        if ':' in host and not host.startswith('['):
            # IPv6 address
            urls.append(f"http://[{host}]:{port}")
        else:
            urls.append(f"http://{host}:{port}")
    
    return urls

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '::')  # Default to IPv6 dual-stack
    debug = is_env_var_enabled('DEBUG')
    
    # If HOST is explicitly set to 0.0.0.0, keep it for IPv4-only compatibility
    if host == '0.0.0.0':
        print(f"🚀 Starting IP Display Server on {host}:{port} (IPv4 only)")
    elif host == '::':
        print(f"🚀 Starting IP Display Server on [::]:{port} (IPv4 + IPv6 dual-stack)")
    else:
        print(f"🚀 Starting IP Display Server on {host}:{port}")
    
    # Show all possible access URLs
    urls = get_local_urls(host, port)
    for i, url in enumerate(urls):
        if i == 0:
            print(f"🌐 Visit {url} in your browser")
            print(f"🔧 Or use: curl {url}")
        else:
            print(f"📡 Also available at: {url}")
    
    # Configure Flask for dual-stack if using ::
    if host == '::':
        # Flask's built-in server doesn't support :: directly, fall back to 0.0.0.0
        print("💡 Note: Flask dev server using 0.0.0.0 (IPv6 support requires production server)")
        app.run(host='0.0.0.0', port=port, debug=debug)
    else:
        app.run(host=host, port=port, debug=debug)