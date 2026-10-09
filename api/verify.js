// Veriphone Line Verification API Endpoint
const { requireAccess } = require('./access');

module.exports = async function handler(req, res) {
  if (!requireAccess(req, res)) return;

  const phone = req.query?.phone || '';
  const key = process.env.VERIPHONE_KEY || "0D1A2E6A82624C26B3190D3ED6B6AECD";

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
