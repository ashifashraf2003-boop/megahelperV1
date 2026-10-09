// Scamalytics Free IP Reputation & Geolocation Endpoint
module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const ip = req.query?.ip || '104.28.194.5';

  try {
    let score = 0;
    let risk = 'Low Risk';
    let isp = 'N/A';
    let org = 'N/A';
    let asn = 'N/A';
    let country_name = 'United States';
    let country_code = 'US';
    let state = '';
    let city = '';
    let zip_code = '';
    let ip_timezone = '';
    let conn_type = 'Standard';
    let is_vpn = false;
    let is_tor = false;
    let is_proxy = false;
    let is_datacenter = false;

    // 1. Fetch Scamalytics HTML
    const scamUrl = `https://scamalytics.com/ip/${ip}`;
    try {
      const sResp = await fetch(scamUrl, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
      });
      if (sResp.ok) {
        const html = await sResp.text();

        // Parse Fraud Score
        const scoreM = html.match(/Fraud Score:\s*(\d+)/i) || html.match(/score">(\d+)<\/span>/i);
        if (scoreM) {
          score = parseInt(scoreM[1], 10);
        }

        // Parse Risk Level
        const riskM = html.match(/<div class="panel_title[^"]*">([^<]+)<\/div>/i);
        if (riskM) {
          risk = riskM[1].trim();
        } else {
          risk = score < 25 ? 'Low Risk' : (score < 75 ? 'Medium Risk' : 'High Risk');
        }

        const getField = (label) => {
          const m = new RegExp(`<th>${label}<\/th>\\s*<td>(?:<a[^>]*>)?([^<]+)`, 'i').exec(html);
          return m ? m[1].trim() : '';
        };

        const getFlag = (label) => {
          const m = new RegExp(`<th>${label}<\/th>\\s*<td>\\s*<div class="risk[^"]*">([^<]*)<\/div>`, 'i').exec(html);
          return m ? m[1].trim().toLowerCase() === 'yes' : false;
        };

        isp = getField('ISP Name') || getField('Organization Name') || isp;
        country_name = getField('Country Name') || country_name;
        country_code = getField('Country Code') || country_code;
        state = getField('State / Province') || state;
        city = getField('City') || city;
        conn_type = getField('Connection type') || conn_type;

        is_vpn = getFlag('VPN');
        is_tor = getFlag('Tor Exit Node');
        is_datacenter = getFlag('Datacenter');
        is_proxy = getFlag('Public Proxy') || getFlag('Web Proxy') || is_datacenter;
      }
    } catch (err) {
      console.warn('Scamalytics direct fetch error:', err.message);
    }

    // 2. Fetch IP-API details for high-precision ASN, Org, Zip & Timezone
    try {
      const geoResp = await fetch(`http://ip-api.com/json/${ip}?fields=status,country,countryCode,regionName,city,zip,timezone,isp,org,as`);
      if (geoResp.ok) {
        const geo = await geoResp.json();
        if (geo.status === 'success') {
          if (!city) city = geo.city || '';
          if (!state) state = geo.regionName || '';
          if (!country_code) country_code = geo.countryCode || 'US';
          zip_code = geo.zip || '';
          ip_timezone = geo.timezone || '';
          asn = geo.as || '';
          org = geo.org || '';
          if (isp === 'N/A' || !isp) isp = geo.isp || 'N/A';
        }
      }
    } catch (e) {}

    return res.status(200).json({
      success: true,
      ip,
      fraud_score: score,
      trust_score: Math.max(0, 100 - score),
      risk_level: risk,
      isp,
      org,
      asn,
      country: country_name,
      country_code,
      region: state,
      city,
      zip: zip_code,
      timezone: ip_timezone,
      connection_type: conn_type,
      proxy: is_proxy,
      vpn: is_vpn,
      tor: is_tor,
      datacenter: is_datacenter
    });
  } catch (error) {
    return res.status(500).json({ success: false, message: error.message });
  }
};
