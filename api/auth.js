const {
  clientIp,
  ipIsAllowed,
  isValidSession,
  createSessionCookie,
  clearSessionCookie,
  credentialsAreValid
} = require('./access');

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  // GET: Check authentication status
  if (req.method === 'GET') {
    const isIpMatch = ipIsAllowed(req);
    const hasValidSession = isValidSession(req);

    // If IP matches -> Auto-authenticated! Also issue 8-hr session cookie for seamless edge requests
    if (isIpMatch) {
      res.setHeader('Set-Cookie', createSessionCookie());
      return res.status(200).json({
        success: true,
        authenticated: true,
        autoByIp: true,
        ip: clientIp(req)
      });
    }

    // If valid session cookie already exists -> Authenticated
    if (hasValidSession) {
      return res.status(200).json({
        success: true,
        authenticated: true,
        autoByIp: false,
        ip: clientIp(req)
      });
    }

    // IP does not match and no active session -> Must login with username & password
    return res.status(200).json({
      success: true,
      authenticated: false,
      autoByIp: false,
      ip: clientIp(req)
    });
  }

  // POST: Login / Logout
  if (req.method === 'POST') {
    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch (_) {}
    }

    const action = body?.action;
    if (action === 'logout') {
      res.setHeader('Set-Cookie', clearSessionCookie());
      return res.status(200).json({ success: true, message: 'Logged out successfully.' });
    }

    const { username, password } = body || {};

    if (!credentialsAreValid(username, password)) {
      return res.status(401).json({ success: false, message: 'Invalid username or password.' });
    }

    // Credentials valid -> issue 8-hour session cookie
    res.setHeader('Set-Cookie', createSessionCookie());
    return res.status(200).json({
      success: true,
      message: 'Login successful (8-hour session active).'
    });
  }

  return res.status(405).json({ success: false, message: 'Method not allowed.' });
};
