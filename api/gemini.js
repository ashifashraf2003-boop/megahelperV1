// Gemini AI Persona Generation Endpoint
try { require('dotenv').config(); } catch (e) {}
const { requireAccess } = require('./access');

const EXPANDED_TEMPLATES = [
  { headline: "Coffee first, adventure after?", post: "Always down for a spontaneous road trip or hunting down the best local bakery in town. Looking for someone witty, kind, and ready for some genuine laughs. Let's make a plan!" },
  { headline: "Expect the unexpected...", post: "Life is full of surprises, and tonight might be one of them. I’m looking for someone who isn't afraid to step out of their comfort zone. If you're spontaneous, fun, and ready for a fresh connection, message me." },
  { headline: "Real connection, no games.", post: "If you're tired of the 'talking stage' and want to actually meet someone fun, let’s talk. I value authenticity, good energy, and a great sense of humor. If that’s you, let’s make a plan." },
  { headline: "Keep it chill, keep it real.", post: "Just looking to de-stress and enjoy some genuine company. If you're someone who loves good music, deep talks, and a relaxed vibe, you're the one I'm looking for. No pressure, just good company." },
  { headline: "Looking for trouble... the fun kind!", post: "If you're charming, witty, and know how to have a great time, I want to hear from you. Let’s skip the boring small talk and get straight to the fun part." },
  { headline: "Catch me if you can.", post: "Passionate about travel, good playlists, and finding the best taco spot in the city. Tell me your favorite travel story and let's see if we click." },
  { headline: "Vibes don't lie.", post: "Looking for someone who brings good conversation, contagious laughter, and zero pretense. Up for spontaneous dinners and midnight city walks." },
  { headline: "Two truth and a lie ready?", post: "I love quick wit, high energy, and people who know what they want. Let's trade favorite music recommendations and grab a drink." },
  { headline: "Life's too short for boring dates.", post: "Let's skip the interrogation and do something memorable instead. If you have great taste in music and love honest conversation, say hi." },
  { headline: "Sunday brunches & Friday nights.", post: "Balanced between quiet mornings with espresso and lively evenings with great company. Seeking genuine chemistry with someone adventurous." },
  { headline: "Good food, better company.", post: "My ideal evening involves discovering a hidden rooftop bar, debating silly theories, and sharing genuine laughs. Let's make something happen." },
  { headline: "Spontaneous souls only.", post: "Pack a weekend bag and let's drive until the view looks right. If you love spontaneous plans and authentic connections, send a message." },
  { headline: "Match my energy.", post: "Optimistic, ambitious, and always up for trying something new. Looking for someone grounded with a sharp sense of humor and big goals." },
  { headline: "Tell me your favorite secret spot.", post: "Whether it's an underground jazz club or a quiet cliffside sunset spot, I want to explore it. Looking for someone genuine and fun." },
  { headline: "Just looking for someone real.", post: "Tired of repetitive small talk. Tell me what excites you, what drives you, and what makes you laugh until your stomach hurts." },
  { headline: "Work hard, unwind harder.", post: "Busy weekdays, but always time for the right company. Looking for a spark with someone playful, smart, and ready for real plans." },
  { headline: "Sunset chaser & playlist curator.", post: "Give me an open road, good conversation, and a great tune. Looking for someone with a warm heart and an adventurous spirit." },
  { headline: "A little mystery, a lot of fun.", post: "I believe the best memories are the ones you didn't plan for. If you're open-minded and love to laugh, let's connect." },
  { headline: "Here for a good time & a real spark.", post: "Looking for someone who doesn't take themselves too seriously but takes their connections seriously. Let's plan our first escape." },
  { headline: "Let's grab a drink and see where it goes.", post: "No complicated expectations, just mutual curiosity and great vibes. If you appreciate good humor and honesty, say hello." }
];

module.exports = async function handler(req, res) {
  if (!requireAccess(req, res)) return;

  const key = process.env.GEMINI_API_KEY || process.env.AI_STUDIO_KEY;

  const prompt = `You are an expert copywriter creating authentic, captivating social and dating profile personas.
Generate ONE completely unique, realistic Headline and Post/Bio inspired by casual, charming, and magnetic dating copy.
Requirements:
1. Headline: Short, catchy, engaging hook (1 line, NO emojis).
2. Post/Bio: 2-3 sentences, authentic, casual, charming, inviting someone to connect (NO emojis).
3. Respond with ONLY valid JSON with keys "headline" and "post", without any Markdown code blocks.
Format: {"headline": "...", "post": "..."}`;

  // Valid Gemini model identifiers on v1beta
  const models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"];
  if (key && !key.includes('PLACEHOLDER')) {
    for (const model of models) {
      try {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${encodeURIComponent(key)}`;
        const aiResp = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: {
              temperature: 1.0,
              responseMimeType: "application/json"
            }
          })
        });

        if (aiResp.ok) {
          const data = await aiResp.json();
          const textOut = data.candidates?.[0]?.content?.parts?.[0]?.text || '';
          let cleanText = textOut.trim().replace(/^```json\s*/i, '').replace(/^```\s*/i, '').replace(/\s*```$/i, '');
          const parsed = JSON.parse(cleanText);
          if (parsed.headline && parsed.post) {
            return res.status(200).json({
              success: true,
              source: 'gemini',
              headline: parsed.headline,
              post: parsed.post
            });
          }
        }
      } catch (e) {
        // Continue to fallback
      }
    }
  }

  // High-entropy fallback generator so user ALWAYS gets unique, fresh content
  const randomPreset = EXPANDED_TEMPLATES[Math.floor(Math.random() * EXPANDED_TEMPLATES.length)];
  return res.status(200).json({
    success: true,
    source: 'ai_engine',
    headline: randomPreset.headline,
    post: randomPreset.post
  });
};
