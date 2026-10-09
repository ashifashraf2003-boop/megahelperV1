import http.server
import socket
import socketserver
import os
import re
import urllib.parse
import urllib.request
import json
import webbrowser

PORT = int(os.environ.get("PORT", 3000))
VERIPHONE_KEY = os.environ.get("VERIPHONE_KEY", "0D1A2E6A82624C26B3190D3ED6B6AECD")
AI_STUDIO_KEY = os.environ.get("AI_STUDIO_KEY", "")

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        # Scamalytics IP Fraud Check Proxy (Free, no key required)
        if parsed.path in ('/api/scamalytics', '/api/ipqs'):
            ip = params.get('ip', ['8.8.8.8'])[0]
            url = f"https://scamalytics.com/ip/{ip}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=12) as resp:
                    html = resp.read().decode('utf-8', errors='ignore')

                # Parse Fraud Score
                score_m = re.search(r'Fraud Score:\s*(\d+)', html)
                score = int(score_m.group(1)) if score_m else 0

                # Parse Risk Level
                risk_m = re.search(r'<div class="panel_title[^"]*">([^<]+)</div>', html)
                risk = risk_m.group(1).strip() if risk_m else ("Low Risk" if score < 25 else "Medium Risk" if score < 75 else "High Risk")

                def get_field(lbl):
                    m = re.search(rf'<th>{re.escape(lbl)}</th>\s*<td>(?:<a[^>]*>)?([^<]+)', html, re.I)
                    return m.group(1).strip() if m else ""

                def get_flag(lbl):
                    m = re.search(rf'<th>{re.escape(lbl)}</th>\s*<td>\s*<div class="risk[^"]*">([^<]*)</div>', html, re.I)
                    return m.group(1).strip().lower() == "yes" if m else False

                isp = get_field("ISP Name") or get_field("Organization Name") or "N/A"
                country_name = get_field("Country Name") or "United States"
                country_code = get_field("Country Code") or "US"
                state = get_field("State / Province") or ""
                city = get_field("City") or ""
                conn_type = get_field("Connection type") or "Standard"
                is_vpn = get_flag("VPN")
                is_tor = get_flag("Tor Exit Node")
                is_datacenter = get_flag("Datacenter")
                is_proxy = get_flag("Public Proxy") or get_flag("Web Proxy") or is_datacenter

                # Fallback to ip-api if location is missing
                if not city or not state:
                    try:
                        req_geo = urllib.request.Request(f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,regionName,city,isp", headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req_geo, timeout=5) as gresp:
                            geo = json.loads(gresp.read().decode('utf-8'))
                            if geo.get("status") == "success":
                                if not city: city = geo.get("city", "")
                                if not state: state = geo.get("regionName", "")
                                if isp == "N/A": isp = geo.get("isp", "N/A")
                                if not country_code: country_code = geo.get("countryCode", "US")
                    except Exception:
                        pass

                data = {
                    "success": True,
                    "ip": ip,
                    "fraud_score": score,
                    "trust_score": max(0, 100 - score),
                    "risk_level": risk,
                    "isp": isp,
                    "ISP": isp,
                    "organization": isp,
                    "country": country_name,
                    "country_name": country_name,
                    "country_code": country_code,
                    "region": state,
                    "city": city,
                    "connection_type": conn_type,
                    "proxy": is_proxy,
                    "vpn": is_vpn,
                    "tor": is_tor
                }
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except Exception as e:
                # Fallback to ip-api.com if Scamalytics is unreachable
                try:
                    req_geo = urllib.request.Request(f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,regionName,city,isp,proxy", headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req_geo, timeout=5) as gresp:
                        geo = json.loads(gresp.read().decode('utf-8'))
                        data = {
                            "success": True,
                            "ip": ip,
                            "fraud_score": 0,
                            "trust_score": 100,
                            "risk_level": "Low Risk",
                            "isp": geo.get("isp", "N/A"),
                            "ISP": geo.get("isp", "N/A"),
                            "country": geo.get("country", "United States"),
                            "country_name": geo.get("country", "United States"),
                            "country_code": geo.get("countryCode", "US"),
                            "region": geo.get("regionName", ""),
                            "city": geo.get("city", ""),
                            "connection_type": "Standard",
                            "proxy": geo.get("proxy", False),
                            "vpn": False,
                            "tor": False
                        }
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(data).encode('utf-8'))
                        return
                except Exception:
                    pass

                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'message': str(e)}).encode())
            return

        # Veriphone Carrier Verification API Proxy
        elif parsed.path == '/api/verify':
            phone = params.get('phone', [''])[0]
            key = params.get('key', [VERIPHONE_KEY])[0] or VERIPHONE_KEY
            url = f"https://api.veriphone.io/v2/verify?key={key}&phone={urllib.parse.quote(phone)}"
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = resp.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())
            return

        # Google AI Studio Gemini API Proxy
        elif parsed.path == '/api/gemini':
            key = params.get('key', [AI_STUDIO_KEY])[0] or AI_STUDIO_KEY
            model = params.get('model', ['gemini-flash-latest'])[0]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            try:
                content_len = int(self.headers.get('Content-Length', 0))
                post_body = self.rfile.read(content_len) if content_len > 0 else b'{}'
                req = urllib.request.Request(url, data=post_body, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, method='POST')
                with urllib.request.urlopen(req, timeout=12) as resp:
                    data = resp.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(data)
            except urllib.error.HTTPError as he:
                self.send_response(he.code)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(he.read())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
            return

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/gemini':
            return self.do_GET()
        super().do_POST()

if __name__ == '__main__':
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)
    
    local_ip = get_local_ip()
    print("=" * 60)
    print("📱 USA Phone Validator & Proxy Automation Server Started!")
    print(f"👉 PC Browser:     http://localhost:{PORT}")
    print(f"👉 Mobile Phone:   http://{local_ip}:{PORT}")
    print("=" * 60)
    print("Instructions for Android Phone:")
    print("1. Make sure your phone and PC are connected to the SAME Wi-Fi.")
    print(f"2. Open Chrome on your phone and go to: http://{local_ip}:{PORT}")
    print("3. Tap Chrome menu (3 dots) -> 'Install App' or 'Add to Home screen'.")
    print("4. It will install directly as an App / APK on your phone!")
    print("=" * 60)

    # Open browser on PC
    webbrowser.open(f"http://localhost:{PORT}")

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
