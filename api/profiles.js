const { getAllProfiles, saveProfile, deleteProfile, getDbUrl } = require('./db');

module.exports = async function handler(req, res) {
  // CORS Headers
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  try {
    // 1. GET: Fetch all saved profiles
    if (req.method === 'GET') {
      const result = await getAllProfiles();
      return res.status(200).json({
        success: true,
        source: result.source,
        hasNeonDb: !!getDbUrl(),
        count: result.profiles.length,
        profiles: result.profiles
      });
    }

    // 2. POST: Save profile to database
    if (req.method === 'POST') {
      let body = req.body;
      if (typeof body === 'string') {
        try { body = JSON.parse(body); } catch (e) {}
      }

      if (!body || !body.phone_number) {
        return res.status(400).json({ success: false, message: 'Phone number is required.' });
      }

      const saved = await saveProfile(body);
      return res.status(200).json({
        success: true,
        message: saved.source === 'neon' ? 'Saved to Neon PostgreSQL!' : 'Saved to local storage (Neon DB URL not configured)',
        source: saved.source,
        profile: saved.profile
      });
    }

    // 3. DELETE: Remove profile by ID
    if (req.method === 'DELETE') {
      const id = req.query?.id || req.body?.id;
      if (!id) {
        return res.status(400).json({ success: false, message: 'Profile ID is required for deletion.' });
      }

      await deleteProfile(id);
      return res.status(200).json({ success: true, message: 'Profile deleted successfully.' });
    }

    return res.status(405).json({ success: false, message: 'Method Not Allowed' });
  } catch (error) {
    console.error('API /api/profiles error:', error);
    return res.status(500).json({ success: false, message: error.message });
  }
};
