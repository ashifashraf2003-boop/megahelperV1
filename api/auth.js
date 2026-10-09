const {
  clientIp,
  ipIsAllowed,
  isValidSession,
  createSessionCookie,
  clearSessionCookie,
  passwordIsValid
} = require('./access');

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  if (!ipIsAllowed(req)) {
    return res.status(403).json({ success: false, message: 'Access denied.' });
  }

  if (req.method === 'GET') {
    return res.status(200).json({ success: true, authenticated: isValidSession(req), ip: clientIp(req) });
  }

  if (req.method === 'POST') {
    const action = req.body?.action;
    if (action === 'logout') {
      res.setHeader('Set-Cookie', clearSessionCookie());
      return res.status(200).json({ success: true });
    }

    if (!passwordIsValid(req.body?.password)) {
      return res.status(401).json({ success: false, message: 'Access denied.' });
    }

    res.setHeader('Set-Cookie', createSessionCookie());
    return res.status(200).json({ success: true });
  }

  return res.status(405).json({ success: false, message: 'Method not allowed.' });
};
