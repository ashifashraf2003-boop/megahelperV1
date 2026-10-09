// Neon PostgreSQL Connection & Local Fallback Handler
try { require('dotenv').config(); } catch (e) {}
const { neon } = require('@neondatabase/serverless');
const fs = require('fs');
const path = require('path');

// Default Neon PostgreSQL connection string provided by user
const NEON_DEFAULT_URL = 'postgresql://neondb_owner:npg_mXZcLPwn6Eb8@ep-red-frog-b774w9rg-pooler.c-13.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require';

// Read database URL from environment with user's Neon connection fallback
const getDbUrl = () => {
  return process.env.DATABASE_URL || process.env.POSTGRES_URL || process.env.NEON_DATABASE_URL || NEON_DEFAULT_URL;
};

// Local JSON storage fallback when DATABASE_URL is not yet configured
const LOCAL_STORAGE_DIR = path.join(process.cwd(), 'data');
const LOCAL_STORAGE_FILE = path.join(LOCAL_STORAGE_DIR, 'saved_profiles.json');

const ensureLocalStorage = () => {
  try {
    if (!fs.existsSync(LOCAL_STORAGE_DIR)) {
      fs.mkdirSync(LOCAL_STORAGE_DIR, { recursive: true });
    }
    if (!fs.existsSync(LOCAL_STORAGE_FILE)) {
      fs.writeFileSync(LOCAL_STORAGE_FILE, JSON.stringify([], null, 2), 'utf-8');
    }
  } catch (e) {
    console.error('Local storage init error:', e.message);
  }
};

// Initialize Table in Neon PostgreSQL
let isTableInitialized = false;
async function initNeonTable(sql) {
  if (isTableInitialized) return;
  try {
    await sql`
      CREATE TABLE IF NOT EXISTS saved_profiles (
        id SERIAL PRIMARY KEY,
        phone_number VARCHAR(50) NOT NULL,
        phone_formatted VARCHAR(50),
        carrier VARCHAR(100),
        line_type VARCHAR(50),
        region VARCHAR(100),
        local_format VARCHAR(50),
        timezone VARCHAR(100),
        country VARCHAR(100),
        ip_address VARCHAR(100),
        location VARCHAR(150),
        fraud_score INT,
        trust_score INT,
        connection_type VARCHAR(100),
        threat_flags VARCHAR(200),
        dob VARCHAR(50),
        age INT,
        headline TEXT,
        post_bio TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
      );
    `;
    isTableInitialized = true;
  } catch (err) {
    console.error('Error creating Neon table:', err.message);
  }
}

// Get Database Client or null
function getSql() {
  const dbUrl = getDbUrl();
  if (dbUrl) {
    try {
      return neon(dbUrl);
    } catch (e) {
      console.error('Neon connection error:', e.message);
    }
  }
  return null;
}

// 1. Fetch all profiles
async function getAllProfiles() {
  const sql = getSql();
  if (sql) {
    try {
      await initNeonTable(sql);
      const rows = await sql`SELECT * FROM saved_profiles ORDER BY created_at DESC;`;
      return { source: 'neon', profiles: rows };
    } catch (err) {
      console.error('Neon query error, falling back to local storage:', err.message);
    }
  }

  // Fallback to local storage
  ensureLocalStorage();
  try {
    const data = fs.readFileSync(LOCAL_STORAGE_FILE, 'utf-8');
    const profiles = JSON.parse(data || '[]');
    return { source: 'local', profiles };
  } catch (e) {
    return { source: 'local', profiles: [] };
  }
}

// 2. Save a profile
async function saveProfile(profile) {
  const sql = getSql();
  if (sql) {
    try {
      await initNeonTable(sql);
      const rows = await sql`
        INSERT INTO saved_profiles (
          phone_number, phone_formatted, carrier, line_type, region,
          local_format, timezone, country, ip_address, location,
          fraud_score, trust_score, connection_type, threat_flags,
          dob, age, headline, post_bio
        ) VALUES (
          ${profile.phone_number || ''},
          ${profile.phone_formatted || ''},
          ${profile.carrier || 'Unknown'},
          ${profile.line_type || 'MOBILE'},
          ${profile.region || ''},
          ${profile.local_format || ''},
          ${profile.timezone || ''},
          ${profile.country || 'United States'},
          ${profile.ip_address || ''},
          ${profile.location || ''},
          ${parseInt(profile.fraud_score) || 0},
          ${parseInt(profile.trust_score) || 100},
          ${profile.connection_type || 'Standard'},
          ${profile.threat_flags || ''},
          ${profile.dob || ''},
          ${parseInt(profile.age) || 0},
          ${profile.headline || ''},
          ${profile.post_bio || ''}
        )
        RETURNING *;
      `;
      return { success: true, source: 'neon', profile: rows[0] };
    } catch (err) {
      console.error('Neon insert error, using local fallback:', err.message);
    }
  }

  // Local fallback
  ensureLocalStorage();
  try {
    const data = fs.readFileSync(LOCAL_STORAGE_FILE, 'utf-8');
    const list = JSON.parse(data || '[]');
    const newRecord = {
      id: Date.now(),
      ...profile,
      created_at: new Date().toISOString()
    };
    list.unshift(newRecord);
    fs.writeFileSync(LOCAL_STORAGE_FILE, JSON.stringify(list, null, 2), 'utf-8');
    return { success: true, source: 'local', profile: newRecord };
  } catch (err) {
    throw new Error('Failed to save locally: ' + err.message);
  }
}

// 3. Delete a profile
async function deleteProfile(id) {
  const sql = getSql();
  if (sql) {
    try {
      await initNeonTable(sql);
      await sql`DELETE FROM saved_profiles WHERE id = ${parseInt(id)};`;
      return { success: true, source: 'neon' };
    } catch (err) {
      console.error('Neon delete error:', err.message);
    }
  }

  // Local fallback
  ensureLocalStorage();
  try {
    const data = fs.readFileSync(LOCAL_STORAGE_FILE, 'utf-8');
    let list = JSON.parse(data || '[]');
    list = list.filter(item => String(item.id) !== String(id));
    fs.writeFileSync(LOCAL_STORAGE_FILE, JSON.stringify(list, null, 2), 'utf-8');
    return { success: true, source: 'local' };
  } catch (err) {
    throw new Error('Failed to delete locally: ' + err.message);
  }
}

module.exports = {
  getDbUrl,
  getAllProfiles,
  saveProfile,
  deleteProfile
};
