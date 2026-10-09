// Gemini 3.5 Flash Lite Persona Generation Endpoint
const DEFAULT_KEY = process.env.AI_STUDIO_KEY || "";

const FALLBACK_TEMPLATES = [
  { headline: "🌙 Expect the unexpected... ✨", post: "Life is full of surprises, and tonight might be one of them. I’m looking for someone who isn't afraid to step out of their comfort zone. If you're spontaneous, fun, and ready for a fresh connection, send me a message and let's see where the night takes us. 🌌🔥" },
  { headline: "🔥 Real connection, no games.", post: "If you're tired of the 'talking stage' and want to actually meet someone fun, let’s talk. I value authenticity, good energy, and a great sense of humor. If that’s you, let’s make a plan. 🥂😉" },
  { headline: "🧘 Keep it chill, keep it real. 🍷", post: "Just looking to de-stress and enjoy some genuine company. If you're someone who loves good music, deep talks, and a relaxed vibe, you're the one I'm looking for. No pressure, just good company. ✨😊" },
  { headline: "😉 I’m looking for trouble... (the fun kind!)", post: "If you're charming, witty, and know how to have a great time, I want to hear from you. Let’s skip the boring introduction and get straight to the fun part. Are you in? 😈✨" },
  { headline: "☕ Coffee first, adventure after? 🚀", post: "Always down for a spontaneous road trip or hunting down the best local bakery in town. Looking for someone witty, kind, and ready for some genuine laughs. Let's make a plan! 🥂✨" }
];

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST,GET,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const key = req.query?.key || process.env.AI_STUDIO_KEY || DEFAULT_KEY;

  const prompt = `You are an expert copywriter creating authentic, captivating social and dating profile personas.
Generate ONE completely unique, realistic Headline and Post/Bio inspired by casual, charming, and magnetic dating copy.
Requirements:
1. Headline: Short, catchy, engaging hook with emojis (1 line).
2. Post/Bio: 2-4 sentences, authentic, casual, charming, inviting someone to connect with matching emojis (e.g. 🌙, ✨, 🥂, 🔥, ☕, 🚀).
3. Respond with ONLY valid JSON with keys "headline" and "post", without any Markdown code blocks.
Format: {"headline": "...", "post": "..."}`;

  const models = ["gemini-3.5-flash-lite", "gemini-3.5-flash"];
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
    } catch (e) {}
  }

  // Graceful fallback to rich persona templates
  const randomPreset = FALLBACK_TEMPLATES[Math.floor(Math.random() * FALLBACK_TEMPLATES.length)];
  return res.status(200).json({
    success: true,
    source: 'template_fallback',
    headline: randomPreset.headline,
    post: randomPreset.post
  });
};
