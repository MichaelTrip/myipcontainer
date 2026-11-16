import os
import socket
import unittest
from unittest.mock import patch

import app as server


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            'ENABLE_GEOLOCATION': 'false', 'ENABLE_REVERSE_DNS': 'false',
            'LOG_VISITORS': 'false', 'TRUST_PROXY': 'false', 'PORT': '8080',
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        self.client = server.app.test_client()

    def test_compact_ipv4_and_ipv6(self):
        for address in ('203.0.113.42', '2001:db8::42'):
            with self.subTest(address=address):
                response = self.client.get('/?compact=true', environ_base={'REMOTE_ADDR': address})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_data(as_text=True), address + '\n')
                self.assertEqual(response.mimetype, 'text/plain')

    def test_proxy_headers_require_explicit_trust(self):
        headers = {'X-Forwarded-For': '203.0.113.42, 10.0.0.1', 'X-Real-IP': '203.0.113.43'}
        response = self.client.get('/json', headers=headers)
        self.assertEqual(response.json['client_ip'], '127.0.0.1')
        with patch.dict(os.environ, {'TRUST_PROXY': 'true'}):
            response = self.client.get('/json', headers=headers)
            self.assertEqual(response.json['client_ip'], '203.0.113.42')

    def test_proxy_header_fallbacks(self):
        with patch.dict(os.environ, {'TRUST_PROXY': 'true'}):
            for header in ('X-Real-IP', 'CF-Connecting-IP'):
                with self.subTest(header=header):
                    response = self.client.get('/json', headers={header: '2001:db8::42'})
                    self.assertEqual(response.json['client_ip'], '2001:db8::42')

    def test_browser_rendering_and_header_escaping(self):
        response = self.client.get('/', headers={
            'User-Agent': 'Mozilla/5.0 <script>alert(1)</script>',
            'X-Forwarded-For': '<img src=x onerror=alert(1)>',
        }, environ_base={'REMOTE_ADDR': '2001:db8::42'})
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/html')
        self.assertIn('2001:<wbr>db8:<wbr>:<wbr>42', html)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', html)
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertNotIn('<img src=x', html)
        self.assertIn('Unavailable (local address, disabled, or lookup failed)', html)

    def test_geolocation_and_dns_in_browser_text_and_json(self):
        geo = {
            'city': 'Example City', 'region': 'Example Region', 'country': 'Example Country',
            'flag_emoji': '', 'latitude': 52, 'longitude': 4, 'timezone': 'Europe/Amsterdam',
            'isp': 'Example ISP', 'org': 'Example Organization',
        }
        with patch.object(server, 'get_ip_geolocation', return_value=geo), \
                patch.object(server, 'get_reverse_dns', return_value='gateway.example.test'):
            html = self.client.get('/', headers={'User-Agent': 'Mozilla/5.0'}).get_data(as_text=True)
            self.assertIn('Example Organization', html)
            self.assertIn('gateway.example.test', html)
            text = self.client.get('/').get_data(as_text=True)
            self.assertIn('ISP: Example ISP', text)
            self.assertIn('Reverse DNS: gateway.example.test', text)
            data = self.client.get('/json').json
            self.assertEqual(data['geolocation'], geo)
            self.assertEqual(data['reverse_dns'], 'gateway.example.test')

    def test_disabled_lookups_do_not_use_network(self):
        with patch.object(server.requests, 'get') as http, \
                patch.object(server.socket, 'gethostbyaddr') as dns:
            self.assertIsNone(server.get_ip_geolocation('203.0.113.42'))
            self.assertIsNone(server.get_reverse_dns('203.0.113.42'))
            http.assert_not_called()
            dns.assert_not_called()

    def test_failed_lookups_return_none_and_restore_socket_timeout(self):
        with patch.dict(os.environ, {'ENABLE_GEOLOCATION': 'true', 'ENABLE_REVERSE_DNS': 'true'}), \
                patch.object(server.requests, 'get', side_effect=server.requests.Timeout), \
                patch.object(server.socket, 'gethostbyaddr', side_effect=socket.herror), \
                patch.object(server.socket, 'setdefaulttimeout') as timeout:
            self.assertIsNone(server.get_ip_geolocation('203.0.113.42'))
            self.assertIsNone(server.get_reverse_dns('203.0.113.42'))
            self.assertEqual(timeout.call_args_list[-1].args, (None,))

    def test_diagnostic_routes_and_missing_route(self):
        self.assertEqual(self.client.get('/health').json['status'], 'healthy')
        debug = self.client.get('/debug').json
        self.assertFalse(debug['enable_reverse_dns'])
        self.assertFalse(debug['enable_geolocation'])
        self.assertFalse(debug['trust_proxy'])
        self.assertEqual(self.client.get('/not-a-route').status_code, 404)

    def test_version_metadata_in_container_without_git(self):
        with patch.object(server.subprocess, 'check_output', side_effect=FileNotFoundError), \
                patch.dict(os.environ, {'APP_VERSION': 'v0.9.1', 'GIT_COMMIT': 'abcdef123456', 'BUILD_DATE': '2026-11-16'}):
            self.assertEqual(self.client.get('/version').json, {
                'version': 'v0.9.1', 'commit': 'abcdef1', 'build_date': '2026-11-16',
            })


if __name__ == '__main__':
    unittest.main()
