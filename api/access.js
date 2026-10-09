const crypto = require('crypto');

const SESSION_COOKIE = 'usa_phone_access';
const SESSION_TTL_SECONDS = 60 * 60 * 8;

function allowedIps() {
  return (process.env.ACCESS_ALLOWED_IPS || '')
    .split(',')
    .map((ip) => ip.trim())
    .filter(Boolean);
}

function clientIp(req) {
  const forwarded = req.headers?.['x-forwarded-for'];
  const rawIp = Array.isArray(forwarded) ? forwarded[0] : (forwarded || req.headers?.['x-real-ip'] || req.socket?.remoteAddress || '');
  return String(rawIp).split(',')[0].trim().replace(/^::ffff:/, '');
}

function ipIsAllowed(req) {
  const ips = allowedIps();
  return ips.length > 0 && ips.includes(clientIp(req));
}

function parseCookies(req) {
  return String(req.headers?.cookie || '')
    .split(';')
    .reduce((cookies, entry) => {
      const index = entry.indexOf('=');
      if (index > 0) cookies[entry.slice(0, index).trim()] = decodeURIComponent(entry.slice(index + 1).trim());
      return cookies;
    }, {});
}

function sign(value) {
  const secret = process.env.ACCESS_SESSION_SECRET || '';
  if (!secret) return '';
  return crypto.createHmac('sha256', secret).update(value).digest('base64url');
}

function isValidSession(req) {
  const token = parseCookies(req)[SESSION_COOKIE];
  if (!token || !process.env.ACCESS_SESSION_SECRET) return false;

  const separator = token.lastIndexOf('.');
  if (separator < 1) return false;
  const payload = token.slice(0, separator);
  const signature = token.slice(separator + 1);
  const expected = sign(payload);
  if (!expected || signature.length !== expected.length) return false;

  try {
    if (!crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected))) return false;
    const data = JSON.parse(Buffer.from(payload, 'base64url').toString('utf8'));
    return data.exp > Math.floor(Date.now() / 1000);
  } catch (_) {
    return false;
  }
}

function createSessionCookie() {
  const expiresAt = Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS;
  const payload = Buffer.from(JSON.stringify({ exp: expiresAt, nonce: crypto.randomBytes(16).toString('hex') })).toString('base64url');
  const secure = process.env.NODE_ENV === 'production' ? '; Secure' : '';
  return `${SESSION_COOKIE}=${payload}.${sign(payload)}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${SESSION_TTL_SECONDS}${secure}`;
}

function clearSessionCookie() {
  const secure = process.env.NODE_ENV === 'production' ? '; Secure' : '';
  return `${SESSION_COOKIE}=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0${secure}`;
}

function passwordIsValid(candidate) {
  const expected = process.env.ACCESS_PASSWORD || '';
  if (!expected || typeof candidate !== 'string' || candidate.length !== expected.length) return false;
  return crypto.timingSafeEqual(Buffer.from(candidate), Buffer.from(expected));
}

function reject(res, statusCode = 403) {
  return res.status(statusCode).json({ success: false, message: 'Access denied.' });
}

function requireAccess(req, res) {
  if (!ipIsAllowed(req)) {
    reject(res);
    return false;
  }
  if (!isValidSession(req)) {
    reject(res, 401);
    return false;
  }
  return true;
}

module.exports = {
  clientIp,
  ipIsAllowed,
  isValidSession,
  createSessionCookie,
  clearSessionCookie,
  passwordIsValid,
  requireAccess,
  reject
};
