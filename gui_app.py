import csv
import json
import os
import random
import re
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import requests

# Default API Keys
VERIPHONE_KEY_DEFAULT = os.environ.get("VERIPHONE_KEY", "0D1A2E6A82624C26B3190D3ED6B6AECD")
AI_STUDIO_KEY_DEFAULT = os.environ.get("AI_STUDIO_KEY", "")

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# ----------------- US AREA CODE MAPPINGS -----------------
US_STATE_AREA_CODES = {
    "alabama": ["205", "251", "256", "334", "938"],
    "alaska": ["907"],
    "arizona": ["480", "520", "602", "623", "928"],
    "arkansas": ["479", "501", "870"],
    "california": ["209", "213", "310", "323", "408", "415", "510", "530", "559", "562", "619", "626", "650", "661", "707", "714", "760", "805", "818", "831", "858", "909", "916", "925", "949", "951"],
    "colorado": ["303", "719", "970", "720"],
    "connecticut": ["203", "860", "475", "959"],
    "delaware": ["302"],
    "district of columbia": ["202"],
    "florida": ["239", "305", "321", "352", "386", "407", "561", "727", "772", "786", "813", "850", "863", "904", "941", "954"],
    "georgia": ["229", "404", "478", "678", "706", "770", "912", "470"],
    "hawaii": ["808"],
    "idaho": ["208", "986"],
    "illinois": ["217", "309", "312", "618", "630", "708", "773", "815", "847", "872", "224", "331"],
    "indiana": ["219", "260", "317", "574", "765", "812", "463"],
    "iowa": ["319", "515", "563", "641", "712"],
    "kansas": ["316", "620", "785", "913"],
    "kentucky": ["270", "502", "606", "859", "364"],
    "louisiana": ["225", "318", "337", "504", "985"],
    "maine": ["207"],
    "maryland": ["240", "301", "410", "443", "667"],
    "massachusetts": ["339", "351", "413", "508", "617", "774", "781", "857", "978"],
    "michigan": ["231", "248", "269", "313", "517", "586", "616", "734", "810", "906", "947", "989"],
    "minnesota": ["218", "320", "507", "612", "651", "763", "952"],
    "mississippi": ["228", "601", "662", "769"],
    "missouri": ["314", "417", "573", "636", "660", "816"],
    "montana": ["406"],
    "nebraska": ["308", "402", "531"],
    "nevada": ["702", "775", "725"],
    "new hampshire": ["603"],
    "new jersey": ["201", "551", "609", "732", "848", "856", "862", "908", "973"],
    "new mexico": ["505", "575"],
    "new york": ["212", "315", "347", "516", "518", "585", "607", "631", "646", "716", "718", "845", "914", "917", "929", "838", "332"],
    "north carolina": ["252", "336", "704", "828", "910", "919", "980", "984"],
    "north dakota": ["701"],
    "ohio": ["216", "234", "330", "419", "440", "513", "567", "614", "740", "937", "380"],
    "oklahoma": ["405", "539", "580", "918"],
    "oregon": ["458", "503", "541", "971"],
    "pennsylvania": ["215", "267", "272", "412", "484", "570", "610", "717", "724", "814", "878"],
    "rhode island": ["401"],
    "south carolina": ["803", "843", "864", "854"],
    "south dakota": ["605"],
    "tennessee": ["423", "615", "731", "865", "901", "931", "629"],
    "texas": ["210", "214", "254", "281", "325", "361", "409", "430", "432", "469", "512", "713", "737", "806", "817", "830", "832", "903", "915", "936", "940", "956", "972", "979"],
    "utah": ["385", "435", "801"],
    "vermont": ["802"],
    "virginia": ["276", "434", "540", "571", "703", "757", "804"],
    "washington": ["206", "253", "360", "425", "509", "564"],
    "west virginia": ["304", "681"],
    "wisconsin": ["262", "414", "534", "608", "715", "920"],
    "wyoming": ["307"]
}

US_STATE_ABBR_MAP = {
    "al": "alabama", "ak": "alaska", "az": "arizona", "ar": "arkansas", "ca": "california",
    "co": "colorado", "ct": "connecticut", "de": "delaware", "dc": "district of columbia", "fl": "florida",
    "ga": "georgia", "hi": "hawaii", "id": "idaho", "il": "illinois", "in": "indiana",
    "ia": "iowa", "ks": "kansas", "ky": "kentucky", "la": "louisiana", "me": "maine",
    "md": "maryland", "ma": "massachusetts", "mi": "michigan", "mn": "minnesota", "ms": "mississippi",
    "mo": "missouri", "mt": "montana", "ne": "nebraska", "nv": "nevada", "nh": "new hampshire",
    "nj": "new jersey", "nm": "new mexico", "ny": "new york", "nc": "north carolina", "nd": "north dakota",
    "oh": "ohio", "ok": "oklahoma", "or": "oregon", "pa": "pennsylvania", "ri": "rhode island",
    "sc": "south carolina", "sd": "south dakota", "tn": "tennessee", "tx": "texas", "ut": "utah",
    "vt": "vermont", "va": "virginia", "wa": "washington", "wv": "west virginia", "wi": "wisconsin",
    "wy": "wyoming"
}

US_CITY_AREA_CODES = {
    "new york": ["212", "646", "718", "917", "347", "929", "332"],
    "manhattan": ["212", "646", "917"],
    "brooklyn": ["718", "347", "929"],
    "queens": ["718", "347", "929"],
    "bronx": ["718", "347"],
    "los angeles": ["213", "310", "323", "424", "818"],
    "chicago": ["312", "773", "872"],
    "houston": ["713", "832", "281"],
    "phoenix": ["602", "480", "623"],
    "philadelphia": ["215", "267", "445"],
    "san antonio": ["210", "726"],
    "san diego": ["619", "858"],
    "dallas": ["214", "469", "972"],
    "san jose": ["408", "669"],
    "austin": ["512", "737"],
    "jacksonville": ["904"],
    "fort worth": ["817", "682"],
    "columbus": ["614", "380"],
    "charlotte": ["704", "980"],
    "san francisco": ["415", "628"],
    "indianapolis": ["317", "463"],
    "seattle": ["206"],
    "denver": ["303", "720"],
    "washington": ["202"],
    "boston": ["617", "857"],
    "el paso": ["915"],
    "nashville": ["615", "629"],
    "detroit": ["313"],
    "oklahoma city": ["405"],
    "portland": ["503", "971"],
    "las vegas": ["702", "725"],
    "memphis": ["901"],
    "louisville": ["502"],
    "baltimore": ["410", "443", "667"],
    "milwaukee": ["414"],
    "albuquerque": ["505"],
    "tucson": ["520"],
    "fresno": ["559"],
    "sacramento": ["916", "279"],
    "atlanta": ["404", "678", "470"],
    "omaha": ["402", "531"],
    "colorado springs": ["719"],
    "raleigh": ["919", "984"],
    "miami": ["305", "786"],
    "oakland": ["510"],
    "minneapolis": ["612"],
    "tampa": ["813"],
    "orlando": ["407", "321"],
    "cleveland": ["216"]
}

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def normalize_phone(raw):
    raw = str(raw).strip()
    digits = re.sub(r'\D', '', raw)
    if len(digits) == 10:
        return "+1" + digits
    elif len(digits) == 11 and digits.startswith("1"):
        return "+" + digits
    if not raw.startswith("+"):
        return "+1" + digits
    return raw

def generate_nanp_number(area_code):
    """Generate structurally valid NANP phone number: +1 <AreaCode><NXX><XXXX>"""
    clean_area = re.sub(r'\D', '', str(area_code))
    if len(clean_area) != 3 or clean_area[0] in ('0', '1'):
        clean_area = "214"

    nxx_first = random.randint(2, 9)
    nxx_mid = random.randint(0, 9)
    nxx_last = random.randint(0, 9)
    if nxx_mid == 1 and nxx_last == 1:
        nxx_last = random.choice([0, 2, 3, 4, 5, 6, 7, 8, 9])

    if nxx_first == 5 and nxx_mid == 5 and nxx_last == 5:
        line_num = random.randint(2000, 9999)
    else:
        line_num = random.randint(1000, 9999)

    return f"+1{clean_area}{nxx_first}{nxx_mid}{nxx_last}{line_num}"

def get_area_codes_for_location(state, city):
    """Find US Area codes given state and/or city."""
    city_clean = (city or "").strip().lower()
    state_clean = (state or "").strip().lower()

    if city_clean in US_CITY_AREA_CODES:
        return US_CITY_AREA_CODES[city_clean]
    for c_key, codes in US_CITY_AREA_CODES.items():
        if c_key in city_clean or city_clean in c_key:
            return codes

    if state_clean in US_STATE_ABBR_MAP:
        state_clean = US_STATE_ABBR_MAP[state_clean]

    if state_clean in US_STATE_AREA_CODES:
        return US_STATE_AREA_CODES[state_clean]
    for s_key, codes in US_STATE_AREA_CODES.items():
        if s_key in state_clean or state_clean in s_key:
            return codes

    return ["214", "213", "212", "305", "681"]

def parse_proxy(raw):
    """Extract IP and proxy config from various proxy input formats."""
    raw = (raw or "").strip()
    if not raw:
        return None

    # Plain IP
    ip_match = re.match(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$", raw)
    if ip_match:
        return {"ip": ip_match.group(1), "proxy_url": None, "raw": raw}

    # Format: ip:port:user:pass
    m = re.match(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+):([^:]+):(.+)$", raw)
    if m:
        ip, port, user, pwd = m.groups()
        return {"ip": ip, "proxy_url": f"http://{user}:{pwd}@{ip}:{port}", "raw": raw}

    # Format: user:pass@ip:port
    m = re.match(r"^([^:]+):([^@]+)@(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)$", raw)
    if m:
        user, pwd, ip, port = m.groups()
        return {"ip": ip, "proxy_url": f"http://{user}:{pwd}@{ip}:{port}", "raw": raw}

    # Format: ip:port
    m = re.match(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)$", raw)
    if m:
        ip, port = m.groups()
        return {"ip": ip, "proxy_url": f"http://{ip}:{port}", "raw": raw}

    # Format with scheme: http://user:pass@ip:port or socks5://...
    if "://" in raw:
        m_ip = re.search(r"@?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)", raw)
        ip = m_ip.group(1) if m_ip else ""
        return {"ip": ip, "proxy_url": raw, "raw": raw}

    return {"ip": raw, "proxy_url": None, "raw": raw}

def get_month_num(month_str):
    if month_str in MONTH_NAMES:
        return MONTH_NAMES.index(month_str) + 1
    try:
        m = int(month_str)
        if 1 <= m <= 12:
            return m
    except ValueError:
        pass
    return 5

def calculate_age_year_month(year, month_num):
    today = date.today()
    age = today.year - year
    if (today.month, today.day) < (month_num, 15):
        age -= 1
    return max(0, age)

def load_post_examples():
    """Loads and parses persona examples from postexample.txt."""
    candidates = [
        resource_path("postexample.txt"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "postexample.txt"),
        r"E:\New folder\usa-phone-checker\postexample.txt"
    ]
    filepath = None
    for p in candidates:
        if os.path.exists(p):
            filepath = p
            break
            
    examples = []
    if filepath:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            matches = re.findall(r'Heading:\s*(.*?)\s*Body:\s*(.*?)(?=(?:\n[১-৯0-9]+\.|\nHeading:|$))', text, re.DOTALL)
            for h, b in matches:
                h_clean = h.strip().replace("\n", " ")
                b_clean = b.strip().replace("\n", " ")
                if h_clean and b_clean:
                    examples.append({"headline": h_clean, "post": b_clean})
        except Exception:
            pass

    if not examples:
        examples = [
            {"headline": "🌙 Expect the unexpected... ✨", "post": "Life is full of surprises, and tonight might be one of them. I’m looking for someone who isn't afraid to step out of their comfort zone. If you're spontaneous, fun, and ready for a fresh connection, send me a message and let's see where the night takes us. 🌌🔥"},
            {"headline": "🔥 Real connection, no games.", "post": "If you're tired of the 'talking stage' and want to actually meet someone fun, let’s talk. I value authenticity, good energy, and a great sense of humor. If that’s you, let’s make a plan. 🥂😉"},
            {"headline": "🧘 Keep it chill, keep it real. 🍷", "post": "Just looking to de-stress and enjoy some genuine company. If you're someone who loves good music, deep talks, and a relaxed vibe, you're the one I'm looking for. No pressure, just good company. ✨😊"},
            {"headline": "😉 I’m looking for trouble... (the fun kind!)", "post": "If you're charming, witty, and know how to have a great time, I want to hear from you. Let’s skip the boring introduction and get straight to the fun part. Are you in? 😈✨"},
            {"headline": "🌃 City lights and great conversation. 🎶", "post": "There's something special about the city at night. Looking for a partner to share that vibe with—whether it’s a late-night bite, a drive, or just hanging out. If you're open to a great night out, let's connect! 🚀🥂"}
        ]
    return examples

def generate_varied_persona_from_pool(examples):
    """Generates an authentic persona variation from postexample.txt."""
    if not examples:
        return {"headline": "✨ Seeking genuine energy. ✨", "post": "Looking for someone cool to spend the night with. Authentic vibes only! 🥂"}
    chosen = random.choice(examples)
    return {"headline": chosen["headline"], "post": chosen["post"]}

def call_gemini_ai_studio(api_key, examples):
    """Calls Google AI Studio Gemini API to write a brand new unique headline & post inspired by postexample.txt."""
    api_key = (api_key or "").strip()
    if not api_key:
        return False, None, "No API Key provided"

    sample_pool = random.sample(examples, min(4, len(examples))) if examples else []
    sample_texts = [f"Example {i+1}:\nHeading: {s['headline']}\nBody: {s['post']}" for i, s in enumerate(sample_pool)]
    examples_str = "\n\n".join(sample_texts)

    prompt = (
        "You are an expert copywriter creating authentic, captivating social and dating profile personas.\n"
        "Generate ONE completely unique, realistic Headline and Post/Bio inspired by the tone, style, and emoji flair of these examples:\n\n"
        f"{examples_str}\n\n"
        "Requirements:\n"
        "1. Headline: Short, catchy, engaging hook with emojis (1 line).\n"
        "2. Post/Bio: 2-4 sentences, authentic, casual, charming, inviting someone to connect with matching emojis.\n"
        "3. Make it fresh, unique, not an exact duplicate.\n"
        "4. Respond with ONLY valid JSON with keys 'headline' and 'post', without any Markdown formatting or code fences.\n"
        "Format: {\"headline\": \"...\", \"post\": \"...\"}"
    )

    models = ["gemini-3.5-flash-lite", "gemini-3.5-flash"]
    last_err = "Request failed"
    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 1.0,
                "responseMimeType": "application/json"
            }
        }
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=12)
            if r.status_code == 200:
                res_data = r.json()
                text_out = res_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                text_clean = text_out.strip()
                if text_clean.startswith("```"):
                    text_clean = re.sub(r"^```(?:json)?\s*", "", text_clean)
                    text_clean = re.sub(r"\s*```$", "", text_clean)
                parsed = json.loads(text_clean)
                if "headline" in parsed and "post" in parsed:
                    return True, parsed, "Success (Gemini AI)"
            elif r.status_code == 402:
                return False, None, "AI Studio: Prepayment credits depleted (HTTP 402)"
            elif r.status_code == 429:
                return False, None, "AI Studio: Rate limit exceeded (HTTP 429)"
            else:
                last_err = f"AI Studio HTTP {r.status_code}"
        except Exception as e:
            last_err = str(e)
            continue
            
    return False, None, last_err

# ----------------- SCAMALYTICS & IP INTELLIGENCE LOOKUP -----------------
def fetch_scamalytics_ip(ip_address):
    """
    Fetch comprehensive IP fraud score, risk level, ISP, ASN, Postal Code, Timezone,
    and security flags from Scamalytics (free, no API key required) and ip-api.com.
    """
    score = 0
    risk = "Low Risk"
    isp = "N/A"
    org = "N/A"
    asn = "N/A"
    country_name = "United States"
    country_code = "US"
    state = ""
    city = ""
    zip_code = ""
    ip_timezone = ""
    conn_type = "Standard"
    is_vpn = False
    is_tor = False
    is_proxy = False
    is_datacenter = False

    url = f"https://scamalytics.com/ip/{ip_address}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            html = r.text

            score_m = re.search(r'Fraud Score:\s*(\d+)', html)
            if score_m:
                score = int(score_m.group(1))
            else:
                score_alt = re.search(r'score">(\d+)</span>', html)
                if score_alt:
                    score = int(score_alt.group(1))

            risk_m = re.search(r'<div class="panel_title[^"]*">([^<]+)</div>', html)
            if risk_m:
                risk = risk_m.group(1).strip()
            else:
                risk = "Low Risk" if score < 25 else ("Medium Risk" if score < 75 else "High Risk")

            def get_field(label):
                m = re.search(rf'<th>{re.escape(label)}</th>\s*<td>(?:<a[^>]*>)?([^<]+)', html, re.I)
                return m.group(1).strip() if m else ""

            def get_flag(label):
                m = re.search(rf'<th>{re.escape(label)}</th>\s*<td>\s*<div class="risk[^"]*">([^<]*)</div>', html, re.I)
                if m:
                    return m.group(1).strip().lower() == "yes"
                return False

            isp = get_field("ISP Name") or get_field("Organization Name") or isp
            country_name = get_field("Country Name") or country_name
            country_code = get_field("Country Code") or country_code
            state = get_field("State / Province") or state
            city = get_field("City") or city
            conn_type = get_field("Connection type") or conn_type

            is_vpn = get_flag("VPN")
            is_tor = get_flag("Tor Exit Node")
            is_datacenter = get_flag("Datacenter")
            is_proxy = get_flag("Public Proxy") or get_flag("Web Proxy") or is_datacenter
    except Exception as e:
        print(f"Scamalytics lookup error: {e}")

    try:
        r_geo = requests.get(
            f"http://ip-api.com/json/{ip_address}?fields=status,country,countryCode,regionName,city,zip,timezone,isp,org,as",
            timeout=5
        )
        if r_geo.status_code == 200:
            geo = r_geo.json()
            if geo.get("status") == "success":
                if not city: city = geo.get("city", "")
                if not state: state = geo.get("regionName", "")
                if not country_code: country_code = geo.get("countryCode", "US")
                zip_code = geo.get("zip", "")
                ip_timezone = geo.get("timezone", "")
                asn = geo.get("as", "")
                org = geo.get("org", "")
                if isp == "N/A" or not isp:
                    isp = geo.get("isp", "N/A")
    except Exception:
        pass

    return {
        "success": True,
        "ip": ip_address,
        "fraud_score": score,
        "trust_score": max(0, 100 - score),
        "risk_level": risk,
        "isp": isp,
        "org": org,
        "asn": asn,
        "country": country_name,
        "country_code": country_code,
        "region": state,
        "city": city,
        "zip": zip_code,
        "timezone": ip_timezone,
        "connection_type": conn_type,
        "proxy": is_proxy,
        "vpn": is_vpn,
        "tor": is_tor,
        "datacenter": is_datacenter
    }

# ----------------- MAIN GUI APPLICATION -----------------
class PhoneValidatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("USA Phone Validator & Proxy Automation")
        self.root.geometry("1080x640")
        self.root.minsize(980, 580)
        self.root.configure(bg="#ffffff")

        # Set window icon
        icon_p = resource_path("app_icon.ico")
        if os.path.exists(icon_p):
            try:
                self.root.iconbitmap(icon_p)
            except Exception:
                pass

        # Persona Templates & AI state
        self.persona_examples = load_post_examples()
        self.is_ai_generating = False

        # State Variables
        self.veriphone_key_var = tk.StringVar(value=VERIPHONE_KEY_DEFAULT)
        self.ai_key_var = tk.StringVar(value=AI_STUDIO_KEY_DEFAULT)
        
        # Proxy Automation Variables
        self.proxy_input_var = tk.StringVar(value="104.28.194.5")
        self.auto_area_var = tk.StringVar(value="")
        self.dob_year_var = tk.StringVar(value="1990")
        self.dob_month_var = tk.StringVar(value="May")
        self.dob_var = tk.StringVar(value="May 1990")
        init_age = calculate_age_year_month(1990, 5) or 35
        self.age_var = tk.StringVar(value=str(init_age))
        default_head = self.persona_examples[0]["headline"] if self.persona_examples else "🌙 Expect the unexpected... ✨"
        self.headline_var = tk.StringVar(value=default_head)

        # Flags & State
        self.is_proxy_running = False
        self.last_valid_mobile = None
        self.last_proxy_details = {}

        self.setup_styles()
        self.build_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # White & Orange Combobox Style
        style.configure(
            "TCombobox",
            fieldbackground="#f8fafc",
            background="#ffffff",
            foreground="#0f172a",
            selectbackground="#ea580c",
            selectforeground="#ffffff",
            bordercolor="#cbd5e1",
            arrowcolor="#0f172a"
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", "#f8fafc"), ("focus", "#ffffff")],
            foreground=[("readonly", "#0f172a"), ("focus", "#0f172a")],
            selectbackground=[("readonly", "#ea580c")]
        )

        # Orange Progressbar
        style.configure(
            "Horizontal.TProgressbar",
            background="#ea580c",
            troughcolor="#f1f5f9",
            bordercolor="#e2e8f0"
        )

    def build_ui(self):
        # ---------------- TOP HEADER (WHITE & MINIMAL) ----------------
        header = tk.Frame(self.root, bg="#ffffff", height=46, padx=16, pady=8)
        header.pack(fill=tk.X, side=tk.TOP)

        title_lbl = tk.Label(
            header,
            text="📱 USA Phone Validator & Proxy Automation",
            font=("Segoe UI", 12, "bold"),
            fg="#0f172a",
            bg="#ffffff"
        )
        title_lbl.pack(side=tk.LEFT)

        btn_settings = tk.Button(
            header,
            text="⚙️ API Keys",
            font=("Segoe UI", 9, "bold"),
            bg="#fff7ed",
            fg="#ea580c",
            activebackground="#ffedd5",
            activeforeground="#c2410c",
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=3,
            command=self.open_api_settings_dialog
        )
        btn_settings.pack(side=tk.RIGHT)

        # Divider line
        divider = tk.Frame(self.root, bg="#e2e8f0", height=1)
        divider.pack(fill=tk.X, side=tk.TOP)

        # ---------------- MAIN 2-COLUMN LAYOUT ----------------
        main_container = tk.Frame(self.root, bg="#ffffff", padx=12, pady=10)
        main_container.pack(fill=tk.BOTH, expand=True)

        # LEFT COLUMN (Input & Enriched Scamalytics Detection - Compact, NO scrollbar needed)
        left_col = tk.Frame(main_container, bg="#ffffff", width=360, padx=8, pady=8, highlightbackground="#e2e8f0", highlightthickness=1)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 6))
        left_col.pack_propagate(False)

        self.build_left_panel(left_col)

        # RIGHT COLUMN (Unified Single Search Box & Persona Tools)
        right_col = tk.Frame(main_container, bg="#ffffff", padx=8, pady=8, highlightbackground="#e2e8f0", highlightthickness=1)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0))

        self.build_right_panel(right_col)

    def open_api_settings_dialog(self):
        """Clean modal dialog for configuring Veriphone & AI Studio API Keys."""
        dlg = tk.Toplevel(self.root)
        dlg.title("API Key Settings")
        dlg.geometry("460x220")
        dlg.configure(bg="#ffffff")
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text="⚙️ API Key Configuration", font=("Segoe UI", 11, "bold"), fg="#0f172a", bg="#ffffff").pack(anchor="w", padx=16, pady=(14, 8))

        frame = tk.Frame(dlg, bg="#ffffff", padx=16)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Veriphone API Key:", font=("Segoe UI", 8, "bold"), fg="#64748b", bg="#ffffff").pack(anchor="w")
        e_veri = tk.Entry(frame, textvariable=self.veriphone_key_var, font=("Consolas", 9), bg="#f8fafc", fg="#0f172a", relief=tk.SOLID, bd=1)
        e_veri.pack(fill=tk.X, pady=(2, 8), ipady=3)

        tk.Label(frame, text="Google AI Studio (Gemini) Key:", font=("Segoe UI", 8, "bold"), fg="#64748b", bg="#ffffff").pack(anchor="w")
        e_ai = tk.Entry(frame, textvariable=self.ai_key_var, font=("Consolas", 9), bg="#f8fafc", fg="#0f172a", relief=tk.SOLID, bd=1)
        e_ai.pack(fill=tk.X, pady=(2, 12), ipady=3)

        btn_save = tk.Button(
            frame,
            text="Save & Close",
            font=("Segoe UI", 9, "bold"),
            bg="#ea580c",
            fg="#ffffff",
            activebackground="#c2410c",
            relief=tk.FLAT,
            cursor="hand2",
            pady=6,
            command=dlg.destroy
        )
        btn_save.pack(fill=tk.X)

    def build_left_panel(self, parent):
        """Constructs Left Panel: Box 1 (Insert Proxy) and Box 2 (Enriched IP Location & Scamalytics Score)."""
        # ================= BOX 1: INSERT PROXY =================
        box_proxy = tk.LabelFrame(
            parent,
            text=" 1. Insert Proxy ",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#ea580c",
            padx=10,
            pady=8
        )
        box_proxy.pack(fill=tk.X, pady=(0, 10))

        tk.Label(box_proxy, text="Proxy / IP Address:", font=("Segoe UI", 8, "bold"), fg="#64748b", bg="#ffffff").pack(anchor="w", pady=(0, 2))

        self.entry_proxy = tk.Entry(
            box_proxy,
            textvariable=self.proxy_input_var,
            font=("Consolas", 10),
            bg="#f8fafc",
            fg="#0f172a",
            relief=tk.SOLID,
            bd=1
        )
        self.entry_proxy.pack(fill=tk.X, pady=(0, 8), ipady=4)
        self.entry_proxy.bind("<Return>", lambda e: self.toggle_proxy_automation())

        # Single Smart Action Button: Start <-> Stop
        self.btn_proxy_run = tk.Button(
            box_proxy,
            text="🚀 Start Automation Engine",
            font=("Segoe UI", 10, "bold"),
            bg="#ea580c",
            fg="#ffffff",
            activebackground="#c2410c",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            pady=8,
            command=self.toggle_proxy_automation
        )
        self.btn_proxy_run.pack(fill=tk.X)

        # ================= BOX 2: ENRICHED LOCATION & SCAMALYTICS FRAUD SCORE =================
        box_detect = tk.LabelFrame(
            parent,
            text=" 2. Scamalytics & IP Intelligence ",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#ea580c",
            padx=10,
            pady=8
        )
        box_detect.pack(fill=tk.BOTH, expand=True)

        # Detection Details Card (Rich Geolocation Details)
        card_det = tk.Frame(box_detect, bg="#f8fafc", padx=10, pady=8, highlightbackground="#e2e8f0", highlightthickness=1)
        card_det.pack(fill=tk.X, pady=(0, 8))

        tk.Label(card_det, text="GEOLOCATION & NETWORK", font=("Segoe UI", 8, "bold"), fg="#ea580c", bg="#f8fafc").pack(anchor="w", pady=(0, 3))
        
        self.lbl_det_ip = tk.Label(card_det, text="IP: —", font=("Segoe UI", 9, "bold"), fg="#0f172a", bg="#f8fafc")
        self.lbl_det_ip.pack(anchor="w", pady=1)

        self.lbl_det_geo = tk.Label(card_det, text="Location: —", font=("Segoe UI", 8), fg="#334155", bg="#f8fafc")
        self.lbl_det_geo.pack(anchor="w", pady=1)

        self.lbl_det_tz = tk.Label(card_det, text="Timezone: —", font=("Segoe UI", 8), fg="#334155", bg="#f8fafc")
        self.lbl_det_tz.pack(anchor="w", pady=1)

        self.lbl_det_isp = tk.Label(card_det, text="ISP: —", font=("Segoe UI", 8), fg="#334155", bg="#f8fafc")
        self.lbl_det_isp.pack(anchor="w", pady=1)

        self.lbl_det_asn = tk.Label(card_det, text="ASN: —", font=("Segoe UI", 8), fg="#334155", bg="#f8fafc")
        self.lbl_det_asn.pack(anchor="w", pady=1)

        self.lbl_det_ac = tk.Label(card_det, text="Area Code: —", font=("Segoe UI", 9, "bold"), fg="#ea580c", bg="#f8fafc")
        self.lbl_det_ac.pack(anchor="w", pady=1)

        # Scamalytics Score Card (Rich Security & Fraud Intelligence)
        card_scam = tk.Frame(box_detect, bg="#f8fafc", padx=10, pady=8, highlightbackground="#e2e8f0", highlightthickness=1)
        card_scam.pack(fill=tk.X)

        tk.Label(card_scam, text="FRAUD & SECURITY REPUTATION", font=("Segoe UI", 8, "bold"), fg="#ea580c", bg="#f8fafc").pack(anchor="w", pady=(0, 3))
        
        self.lbl_fraud_score = tk.Label(card_scam, text="Scamalytics: —", font=("Segoe UI", 10, "bold"), fg="#0f172a", bg="#f8fafc")
        self.lbl_fraud_score.pack(anchor="w", pady=1)

        self.lbl_trust_score = tk.Label(card_scam, text="Trust Score: —", font=("Segoe UI", 9), fg="#64748b", bg="#f8fafc")
        self.lbl_trust_score.pack(anchor="w", pady=1)

        self.lbl_conn_type = tk.Label(card_scam, text="Connection: —", font=("Segoe UI", 8), fg="#334155", bg="#f8fafc")
        self.lbl_conn_type.pack(anchor="w", pady=1)

        self.lbl_fraud_flags = tk.Label(card_scam, text="Threat Flags: —", font=("Segoe UI", 8), fg="#64748b", bg="#f8fafc")
        self.lbl_fraud_flags.pack(anchor="w", pady=1)

    def build_right_panel(self, parent):
        """Constructs Right Panel: Unified Box 3 (Live Search + Valid SIM + 3x2 Metric Grid) and Box 4 (Persona Tools)."""
        # ================= BOX 3: SEARCH, HERO WINNER CARD & LINE DETAILS =================
        box_sim = tk.LabelFrame(
            parent,
            text=" 3. Valid Mobile SIM & Line Details ",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#ea580c",
            padx=12,
            pady=10
        )
        box_sim.pack(fill=tk.X, pady=(0, 10))

        # Status row
        status_row = tk.Frame(box_sim, bg="#ffffff")
        status_row.pack(fill=tk.X, pady=(0, 4))

        self.lbl_loop_status = tk.Label(
            status_row,
            text="Ready. Click Start Automation to begin search.",
            font=("Segoe UI", 9),
            fg="#64748b",
            bg="#ffffff",
            anchor="w"
        )
        self.lbl_loop_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.loop_progress = ttk.Progressbar(box_sim, style="Horizontal.TProgressbar", mode="determinate")
        self.loop_progress.pack(fill=tk.X, pady=(0, 8))

        # Hero Winner Card (Light warm background, clean border)
        self.box_output = tk.Frame(box_sim, bg="#fff7ed", padx=12, pady=10, highlightbackground="#fed7aa", highlightthickness=1)
        self.box_output.pack(fill=tk.X, pady=(0, 8))

        out_top = tk.Frame(self.box_output, bg="#fff7ed")
        out_top.pack(fill=tk.X, pady=(0, 2))

        self.status_title = tk.Label(
            out_top,
            text="WAITING FOR VALID MOBILE SIM",
            font=("Segoe UI", 9, "bold"),
            fg="#ea580c",
            bg="#fff7ed"
        )
        self.status_title.pack(side=tk.LEFT)

        # Copy Number Button (without +1)
        self.btn_copy_winner = tk.Button(
            out_top,
            text="📋 Copy Number (without +1)",
            font=("Segoe UI", 8, "bold"),
            bg="#ea580c",
            fg="#ffffff",
            activebackground="#c2410c",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=3,
            command=self.copy_winner_number
        )
        self.btn_copy_winner.pack(side=tk.RIGHT)

        winner_num_row = tk.Frame(self.box_output, bg="#fff7ed")
        winner_num_row.pack(fill=tk.X, pady=(2, 2))

        self.lbl_out_number = tk.Label(
            winner_num_row,
            text="+1 ___ _______",
            font=("Consolas", 18, "bold"),
            fg="#ea580c",
            bg="#fff7ed"
        )
        self.lbl_out_number.pack(side=tk.LEFT)

        self.lbl_out_carrier_badge = tk.Label(
            winner_num_row,
            text="Carrier: —",
            font=("Segoe UI", 9, "bold"),
            fg="#475569",
            bg="#fff7ed"
        )
        self.lbl_out_carrier_badge.pack(side=tk.LEFT, padx=(12, 0))

        # 3x2 Metric Stats Grid (Each in a subtle micro-card)
        stats_frame = tk.Frame(box_sim, bg="#ffffff")
        stats_frame.pack(fill=tk.X, pady=(2, 2))

        self.labels = {}
        fields = [
            ("CARRIER", "carrier"),
            ("LINE TYPE", "type"),
            ("STATE / REGION", "region"),
            ("LOCAL FORMAT", "local"),
            ("TIMEZONE", "timezone"),
            ("COUNTRY", "country")
        ]

        for i, (title, key) in enumerate(fields):
            r = i // 3
            c = i % 3
            card = tk.Frame(stats_frame, bg="#f8fafc", padx=8, pady=5, highlightbackground="#e2e8f0", highlightthickness=1)
            card.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)
            stats_frame.columnconfigure(c, weight=1)

            tk.Label(card, text=title, font=("Segoe UI", 7, "bold"), fg="#94a3b8", bg="#f8fafc").pack(anchor="w")
            val_lbl = tk.Label(card, text="—", font=("Segoe UI", 9, "bold"), fg="#0f172a", bg="#f8fafc")
            val_lbl.pack(anchor="w", pady=(1, 0))
            self.labels[key] = val_lbl

        # ================= BOX 4: PROFILE & PERSONA STUDIO =================
        box_persona = tk.LabelFrame(
            parent,
            text=" 4. Profile & Persona Tools ",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#ea580c",
            padx=12,
            pady=10
        )
        box_persona.pack(fill=tk.BOTH, expand=True)

        # Row 1: DOB (Year, Month, and Calculated Age Badge - NO Age dropdown)
        dob_row = tk.Frame(box_persona, bg="#ffffff")
        dob_row.pack(fill=tk.X, pady=(0, 8))

        # Year Label & Dropdown
        tk.Label(dob_row, text="Year:", font=("Segoe UI", 9, "bold"), fg="#0f172a", bg="#ffffff").pack(side=tk.LEFT, padx=(0, 4))
        year_values = [str(y) for y in range(1950, 2006)]
        self.combo_dob_year = ttk.Combobox(
            dob_row,
            textvariable=self.dob_year_var,
            values=year_values,
            state="normal",
            width=6,
            font=("Consolas", 9, "bold")
        )
        self.combo_dob_year.pack(side=tk.LEFT, padx=(0, 10))
        self.combo_dob_year.bind("<<ComboboxSelected>>", self.on_dob_dropdown_change)
        self.combo_dob_year.bind("<KeyRelease>", self.on_dob_year_key_typed)
        self.combo_dob_year.bind("<FocusOut>", self.on_dob_year_focus_out)

        # Month Label & Dropdown (January to December)
        tk.Label(dob_row, text="Month:", font=("Segoe UI", 9, "bold"), fg="#0f172a", bg="#ffffff").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_dob_month = ttk.Combobox(
            dob_row,
            textvariable=self.dob_month_var,
            values=MONTH_NAMES,
            state="readonly",
            width=10,
            font=("Segoe UI", 9, "bold")
        )
        self.combo_dob_month.pack(side=tk.LEFT, padx=(0, 12))
        self.combo_dob_month.bind("<<ComboboxSelected>>", self.on_dob_dropdown_change)

        # Calculated Age Display (NO dropdown! Auto calculated badge)
        tk.Label(dob_row, text="Age:", font=("Segoe UI", 9, "bold"), fg="#0f172a", bg="#ffffff").pack(side=tk.LEFT, padx=(0, 4))
        
        age_badge = tk.Frame(dob_row, bg="#fff7ed", padx=8, pady=2, highlightbackground="#fed7aa", highlightthickness=1)
        age_badge.pack(side=tk.LEFT)
        self.lbl_age_display = tk.Label(
            age_badge,
            textvariable=self.age_var,
            font=("Segoe UI", 9, "bold"),
            fg="#ea580c",
            bg="#fff7ed"
        )
        self.lbl_age_display.pack(side=tk.LEFT)
        tk.Label(age_badge, text=" yrs", font=("Segoe UI", 8, "bold"), fg="#9a3412", bg="#fff7ed").pack(side=tk.LEFT)

        # Row 2: Headline (Large font with Segoe UI Emoji support)
        head_row = tk.Frame(box_persona, bg="#ffffff")
        head_row.pack(fill=tk.X, pady=(0, 8))

        tk.Label(head_row, text="Headline:", font=("Segoe UI", 10, "bold"), fg="#0f172a", bg="#ffffff").pack(side=tk.LEFT, padx=(0, 6))
        self.entry_headline = tk.Entry(
            head_row,
            textvariable=self.headline_var,
            font=("Segoe UI Emoji", 11, "bold"),
            bg="#f8fafc",
            fg="#0f172a",
            relief=tk.SOLID,
            bd=1
        )
        self.entry_headline.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), ipady=4)

        btn_copy_head = tk.Button(
            head_row,
            text="📋 Copy",
            font=("Segoe UI", 9, "bold"),
            bg="#ea580c",
            fg="#ffffff",
            activebackground="#c2410c",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=4,
            command=lambda: self.copy_to_clip(self.headline_var.get(), "Headline")
        )
        btn_copy_head.pack(side=tk.RIGHT)

        # Row 3: Post / Bio Box (Large font with Segoe UI Emoji support, fixed balanced height)
        post_header_row = tk.Frame(box_persona, bg="#ffffff")
        post_header_row.pack(fill=tk.X, pady=(0, 2))

        tk.Label(post_header_row, text="Post / Bio:", font=("Segoe UI", 10, "bold"), fg="#0f172a", bg="#ffffff").pack(side=tk.LEFT)
        self.lbl_ai_status = tk.Label(post_header_row, text="✨ Gemini 3.5 Flash Lite Ready", font=("Segoe UI Emoji", 9, "bold"), fg="#ea580c", bg="#ffffff")
        self.lbl_ai_status.pack(side=tk.RIGHT)

        self.txt_post = tk.Text(
            box_persona,
            height=5,
            font=("Segoe UI Emoji", 11),
            bg="#f8fafc",
            fg="#0f172a",
            insertbackground="#0f172a",
            relief=tk.SOLID,
            bd=1,
            wrap=tk.WORD,
            padx=8,
            pady=8
        )
        default_post = self.persona_examples[0]["post"] if self.persona_examples else "Life is full of surprises! Looking for someone fun and authentic to connect with. Let's make a plan! 🥂✨"
        self.txt_post.insert(tk.END, default_post)
        self.txt_post.pack(fill=tk.BOTH, expand=True, pady=(2, 8))

        # Bottom Action Buttons (All Premium Orange with Bold White Text)
        p_act_row = tk.Frame(box_persona, bg="#ffffff")
        p_act_row.pack(fill=tk.X)

        self.btn_ai_gen = tk.Button(
            p_act_row,
            text="✨ AI Generate Post",
            font=("Segoe UI Emoji", 9, "bold"),
            bg="#ea580c",
            fg="#ffffff",
            activebackground="#c2410c",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=5,
            command=self.action_ai_generate_persona
        )
        self.btn_ai_gen.pack(side=tk.LEFT, padx=(0, 6))

        btn_copy_post = tk.Button(
            p_act_row,
            text="📋 Copy Post",
            font=("Segoe UI Emoji", 9, "bold"),
            bg="#ea580c",
            fg="#ffffff",
            activebackground="#c2410c",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=5,
            command=self.copy_post_content
        )
        btn_copy_post.pack(side=tk.LEFT, padx=(0, 6))

        btn_rand_persona = tk.Button(
            p_act_row,
            text="🎲 Preset",
            font=("Segoe UI Emoji", 9, "bold"),
            bg="#ea580c",
            fg="#ffffff",
            activebackground="#c2410c",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=5,
            command=self.action_random_persona
        )
        btn_rand_persona.pack(side=tk.LEFT)

        btn_copy_all = tk.Button(
            p_act_row,
            text="⭐ Copy All Persona Data",
            font=("Segoe UI Emoji", 9, "bold"),
            bg="#c2410c",
            fg="#ffffff",
            activebackground="#9a3412",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=14,
            pady=5,
            command=self.copy_all_persona_data
        )
        btn_copy_all.pack(side=tk.RIGHT)

    # ----------------- PROXY AUTOMATION LOGIC -----------------
    def toggle_proxy_automation(self):
        if self.is_proxy_running:
            self.stop_proxy_automation()
        else:
            self.start_proxy_automation()

    def start_proxy_automation(self):
        raw_proxy = self.proxy_input_var.get().strip()
        if not raw_proxy:
            messagebox.showwarning("Input Required", "Please insert a proxy string or an IP address.")
            return

        self.is_proxy_running = True
        self.btn_proxy_run.config(
            text="⏹️ Stop Automation",
            bg="#dc2626",
            activebackground="#b91c1c"
        )
        self.loop_progress["value"] = 0
        self.loop_progress["maximum"] = 100
        self.lbl_loop_status.config(text="Connecting and querying Scamalytics...", fg="#ea580c")

        threading.Thread(target=self._worker_proxy_automation, args=(raw_proxy,), daemon=True).start()

    def stop_proxy_automation(self):
        self.is_proxy_running = False
        self.btn_proxy_run.config(
            text="🚀 Start Automation Engine",
            bg="#ea580c",
            activebackground="#c2410c"
        )
        self.lbl_loop_status.config(text="Automation stopped.", fg="#dc2626")

    def _finish_proxy_automation(self):
        self.is_proxy_running = False
        self.btn_proxy_run.config(
            text="🚀 Start Automation Engine",
            bg="#ea580c",
            activebackground="#c2410c"
        )

    def _worker_proxy_automation(self, raw_proxy):
        """Automated pipeline: Proxy reputation -> Area Code -> Veriphone loop -> Auto Stop."""
        parsed = parse_proxy(raw_proxy)
        target_ip = parsed.get("ip") if parsed else raw_proxy
        
        self.root.after(0, lambda: self.lbl_loop_status.config(text=f"Querying Scamalytics for IP: {target_ip}...", fg="#ea580c"))
        self.root.after(0, lambda: self.loop_progress.config(value=15))

        veri_key = self.veriphone_key_var.get().strip() or VERIPHONE_KEY_DEFAULT

        # 1. Scamalytics & IP Intelligence Query (Free, no API key required)
        ip_data = fetch_scamalytics_ip(target_ip)

        fraud_score = ip_data.get("fraud_score", 0)
        trust_score = ip_data.get("trust_score", 100)
        risk_level = ip_data.get("risk_level", "Low Risk")
        city = ip_data.get("city", "N/A")
        region = ip_data.get("region", "N/A")
        zip_code = ip_data.get("zip", "")
        ip_timezone = ip_data.get("timezone", "N/A")
        country = ip_data.get("country_code", "US")
        isp = ip_data.get("isp", "N/A")
        org = ip_data.get("org", "")
        asn = ip_data.get("asn", "")
        is_proxy = ip_data.get("proxy", False)
        is_vpn = ip_data.get("vpn", False)
        is_tor = ip_data.get("tor", False)
        is_dc = ip_data.get("datacenter", False)
        conn_type = ip_data.get("connection_type", "Standard")

        self.last_proxy_details = {
            "ip": target_ip,
            "fraud_score": fraud_score,
            "trust_score": trust_score,
            "risk_level": risk_level,
            "city": city,
            "region": region,
            "zip": zip_code,
            "timezone": ip_timezone,
            "country": country,
            "isp": isp,
            "asn": asn,
            "conn_type": conn_type
        }

        # Update GUI with IP & Fraud Score
        def update_score_ui():
            self.lbl_det_ip.config(text=f"IP: {target_ip}")
            loc_str = f"Location: {city}, {region}"
            if zip_code:
                loc_str += f" ({zip_code})"
            loc_str += f" ({country}) 🇺🇸"
            self.lbl_det_geo.config(text=loc_str)
            self.lbl_det_tz.config(text=f"Timezone: {ip_timezone}")
            self.lbl_det_isp.config(text=f"ISP: {isp[:28]}")
            asn_display = asn if asn else (org[:28] if org else "Standard")
            self.lbl_det_asn.config(text=f"ASN: {asn_display[:28]}")

            score_color = "#16a34a" if fraud_score < 30 else ("#d97706" if fraud_score < 75 else "#dc2626")
            self.lbl_fraud_score.config(text=f"Scamalytics: {fraud_score}/100 ({risk_level})", fg=score_color)
            self.lbl_trust_score.config(text=f"Trust Score: {trust_score}%", fg="#16a34a" if trust_score > 70 else "#dc2626")
            self.lbl_conn_type.config(text=f"Connection: {conn_type}")
            
            flags_str = f"Proxy:{is_proxy} | VPN:{is_vpn} | Tor:{is_tor} | Host:{is_dc}"
            self.lbl_fraud_flags.config(text=flags_str)

        self.root.after(0, update_score_ui)

        # 2. Select Area Code by Location
        area_codes = get_area_codes_for_location(region, city)
        chosen_area = area_codes[0] if area_codes else "214"
        self.root.after(0, lambda: self.lbl_det_ac.config(text=f"Area Code: {chosen_area} ({region})"))
        self.root.after(0, lambda: self.auto_area_var.set(chosen_area))
        self.root.after(0, lambda: self.loop_progress.config(value=35))

        # 3. Number Generation & Validity Loop (Stop on Valid Mobile)
        self.root.after(0, lambda: self.lbl_loop_status.config(
            text=f"Testing numbers for area code {chosen_area} until REAL MOBILE SIM is found...",
            fg="#ea580c"
        ))

        max_attempts = 25
        found_winner = False

        for attempt in range(1, max_attempts + 1):
            if not self.is_proxy_running:
                break

            cand_num = generate_nanp_number(chosen_area)
            norm_cand = normalize_phone(cand_num)
            
            prog_val = 35 + int((attempt / max_attempts) * 60)
            self.root.after(0, lambda a=attempt, n=cand_num, pv=prog_val: [
                self.lbl_loop_status.config(text=f"Attempt {a}/{max_attempts}: Testing candidate {n}..."),
                self.loop_progress.config(value=pv)
            ])

            # Call Veriphone API
            try:
                url_veri = "https://api.veriphone.io/v2/verify"
                r = requests.get(url_veri, params={"key": veri_key, "phone": norm_cand}, timeout=10)
                veri_data = r.json()
            except Exception:
                time.sleep(0.5)
                continue

            phone_valid = veri_data.get("phone_valid", False)
            phone_type = (veri_data.get("phone_type") or "").lower()
            carrier = veri_data.get("carrier") or "Unknown Carrier"

            # Check if Valid Mobile SIM
            if phone_valid and phone_type == "mobile":
                found_winner = True
                self.last_valid_mobile = {
                    "phone": veri_data.get("phone") or norm_cand,
                    "carrier": carrier,
                    "region": veri_data.get("phone_region") or region,
                    "type": "mobile",
                    "data": veri_data
                }
                
                self.root.after(0, lambda d=veri_data: self.display_data(d))
                self.root.after(0, lambda num=cand_num, car=carrier, reg=region, fs=fraud_score, ts=trust_score, att=attempt: self._winner_found_ui(num, car, reg, fs, ts, att))
                break
            else:
                self.root.after(0, lambda d=veri_data: self.display_data(d))
                time.sleep(0.5)

        if not found_winner and self.is_proxy_running:
            self.root.after(0, lambda: self.lbl_loop_status.config(text=f"Completed {max_attempts} attempts. Click Start to try another batch.", fg="#dc2626"))
            self.root.after(0, lambda: self.loop_progress.config(value=100))

        self.root.after(0, self._finish_proxy_automation)

    def _winner_found_ui(self, phone, carrier, region, fraud_score, trust_score, attempts):
        """Highlights the winner box when valid mobile number is found and stops."""
        self.lbl_out_number.config(text=phone)
        self.lbl_out_carrier_badge.config(text=f"Carrier: {carrier} | {region}")
        self.status_title.config(text="✅ VALID REAL MOBILE SIM DETECTED", fg="#16a34a")
        self.lbl_loop_status.config(
            text=f"🎉 Found Real Mobile SIM in {attempts} attempts! Automation completed.",
            fg="#16a34a"
        )
        self.loop_progress.config(value=100)
        self.btn_proxy_run.config(
            text="🚀 Start Automation Engine",
            bg="#ea580c",
            activebackground="#c2410c"
        )
        try:
            self.root.bell()
        except Exception:
            pass
        # Automatically generate a unique AI persona for the found number
        self.action_ai_generate_persona(silent=True)

    def display_data(self, data):
        """Updates Carrier & Line Information labels in the 3x2 metric grid."""
        if not hasattr(self, "labels"):
            return
            
        carrier = data.get("carrier") or "N/A"
        ptype = (data.get("phone_type") or "").upper() or "N/A"
        region = data.get("phone_region") or "N/A"
        local = data.get("local_number") or data.get("phone") or "N/A"
        tz = data.get("timezone", [])
        timezone = tz[0] if tz else "N/A"
        country = f"{data.get('country', 'United States')} 🇺🇸"

        self.labels["carrier"].config(text=carrier)
        self.labels["type"].config(text=ptype, fg="#16a34a" if ptype == "MOBILE" else "#0f172a")
        self.labels["region"].config(text=region)
        self.labels["local"].config(text=local)
        self.labels["timezone"].config(text=timezone)
        self.labels["country"].config(text=country)

    # ----------------- PERSONA & DOB HELPERS -----------------
    def on_dob_year_key_typed(self, event=None):
        """Allows direct typing: when 4 digits are entered, immediately syncs DOB and Age."""
        txt = self.dob_year_var.get().strip()
        if len(txt) == 4 and txt.isdigit():
            y = int(txt)
            if 1900 <= y <= 2030:
                self.on_dob_dropdown_change()

    def on_dob_year_focus_out(self, event=None):
        """Expands 2-digit shortcuts (e.g. 85 -> 1985, 02 -> 2002) for super fast input."""
        txt = self.dob_year_var.get().strip()
        if len(txt) == 2 and txt.isdigit():
            val = int(txt)
            expanded = (2000 + val) if val <= 25 else (1900 + val)
            self.dob_year_var.set(str(expanded))
            self.on_dob_dropdown_change()
        elif len(txt) == 4 and txt.isdigit():
            self.on_dob_dropdown_change()

    def on_dob_dropdown_change(self, event=None):
        """Synchronizes Year and Month Name dropboxes and automatically recalculates Age and DOB."""
        try:
            y_str = self.dob_year_var.get().strip()
            if not y_str or not y_str.isdigit():
                return
            y = int(y_str)
            m_name = self.dob_month_var.get() or "May"
            m_num = get_month_num(m_name)

            self.dob_var.set(f"{m_name} {y}")

            # Automatically recalculate age and update displayed label
            age = calculate_age_year_month(y, m_num)
            self.age_var.set(str(age))
        except Exception:
            pass

    def copy_winner_number(self):
        """Copies the winner phone number WITHOUT +1 (pure 10-digit number)."""
        num = self.lbl_out_number.cget("text")
        if num and "___" not in num:
            digits = re.sub(r'\D', '', num)
            if len(digits) == 11 and digits.startswith("1"):
                clean_num = digits[1:]
            elif len(digits) == 10:
                clean_num = digits
            else:
                clean_num = re.sub(r'^\+?1', '', num).strip()
            self.copy_to_clip(clean_num, "Number (without +1)")
        else:
            messagebox.showinfo("Empty", "No valid mobile number generated yet.")

    def copy_post_content(self):
        content = self.txt_post.get("1.0", tk.END).strip()
        if content:
            self.copy_to_clip(content, "Post / Bio")

    def action_random_persona(self):
        """Fills random realistic persona presets loaded from postexample.txt."""
        if not self.persona_examples:
            self.persona_examples = load_post_examples()
        chosen = random.choice(self.persona_examples)
        self.headline_var.set(chosen["headline"])
        self.txt_post.delete("1.0", tk.END)
        self.txt_post.insert(tk.END, chosen["post"])
        if hasattr(self, "lbl_ai_status"):
            self.lbl_ai_status.config(text="🎲 Preset loaded", fg="#ea580c")

    def action_ai_generate_persona(self, silent=False):
        """Generates a unique persona headline & post using Google AI Studio Gemini API with postexample.txt fallback."""
        if self.is_ai_generating:
            return
            
        self.is_ai_generating = True
        if hasattr(self, "btn_ai_gen"):
            self.btn_ai_gen.config(state=tk.DISABLED, text="⏳ Generating AI...")
        if hasattr(self, "lbl_ai_status"):
            self.lbl_ai_status.config(text="✨ Connecting to Gemini...", fg="#ea580c")

        def worker():
            api_key = self.ai_key_var.get().strip()
            success, result, msg = call_gemini_ai_studio(api_key, self.persona_examples)
            
            if success and result:
                headline = result.get("headline", "")
                post = result.get("post", "")
                status_text = "✨ AI Generated (Gemini 3.5 Flash Lite)"
                status_color = "#16a34a"
            else:
                fallback_res = generate_varied_persona_from_pool(self.persona_examples)
                headline = fallback_res["headline"]
                post = fallback_res["post"]
                if "402" in msg:
                    status_text = "✨ Templates (AI Studio 402)"
                    status_color = "#d97706"
                else:
                    status_text = "✨ From templates"
                    status_color = "#64748b"

            def update_ui():
                if headline:
                    self.headline_var.set(headline)
                if post:
                    self.txt_post.delete("1.0", tk.END)
                    self.txt_post.insert(tk.END, post)
                if hasattr(self, "lbl_ai_status"):
                    self.lbl_ai_status.config(text=status_text, fg=status_color)
                if hasattr(self, "btn_ai_gen"):
                    self.btn_ai_gen.config(state=tk.NORMAL, text="✨ AI Generate Post")
                self.is_ai_generating = False

            self.root.after(0, update_ui)

        threading.Thread(target=worker, daemon=True).start()

    def copy_all_persona_data(self):
        """Generates structured persona block matching the user's diagram and copies to clipboard."""
        raw_phone = self.lbl_out_number.cget("text")
        digits = re.sub(r'\D', '', raw_phone)
        phone_no_plus = digits[1:] if (len(digits) == 11 and digits.startswith("1")) else digits

        carrier = self.last_proxy_details.get("isp", "N/A")
        if self.last_valid_mobile:
            carrier = self.last_valid_mobile.get("carrier", carrier)

        proxy_ip = self.last_proxy_details.get("ip", self.proxy_input_var.get().strip())
        location = f"{self.last_proxy_details.get('city', '')}, {self.last_proxy_details.get('region', '')} ({self.last_proxy_details.get('country', 'US')})".strip()
        fraud = f"{self.last_proxy_details.get('fraud_score', '—')}/100"
        trust = f"{self.last_proxy_details.get('trust_score', '—')}%"
        dob = self.dob_var.get()
        age = self.age_var.get()
        headline = self.headline_var.get()
        post = self.txt_post.get("1.0", tk.END).strip()

        block = f"""=== PERSONA & PROXY PROFILE ===
Phone Number: {phone_no_plus} ({raw_phone})
Line Type: Real Mobile SIM ({carrier})
Proxy IP: {proxy_ip}
Location: {location}
Proxy IP Fraud Score: {fraud} | Trust Score: {trust}
Date of Birth: {dob} (Age: {age})
Headline: {headline}
Post / Bio:
{post}
==============================="""
        
        self.copy_to_clip(block, "Full Persona Profile")

    def copy_to_clip(self, text, label=""):
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Copied", f"Copied {label} to clipboard:\n\n{text[:120]}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = PhoneValidatorApp(root)
        root.mainloop()
    except Exception as e:
        with open("crash_log.txt", "w", encoding="utf-8") as f:
            import traceback
            traceback.print_exc(file=f)
