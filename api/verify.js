// Veriphone Line Verification API Endpoint
const DEFAULT_KEY = "0D1A2E6A82624C26B3190D3ED6B6AECD";

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const phone = req.query?.phone || '';
  const key = req.query?.key || process.env.VERIPHONE_KEY || DEFAULT_KEY;

  if (!phone) {
    return res.status(400).json({ status: 'error', message: 'Phone number is required.' });
  }

  try {
    const url = `https://api.veriphone.io/v2/verify?key=${encodeURIComponent(key)}&phone=${encodeURIComponent(phone)}`;
    const response = await fetch(url);
    const data = await response.json();
    return res.status(response.status).json(data);
  } catch (error) {
    return res.status(500).json({ status: 'error', message: error.message });
  }
};
