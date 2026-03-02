export default async function handler(req, res) {
  const { messages } = req.body;
  const SYSTEM_PROMPT = `אתה העוזר של Men Zone, קליניקה להסרת שיער בלייזר לגברים בראש העין (יהושע בן נון 60). שעות פעילות: א'-ה' 18:00-22:00. סגור בשבת. טכנולוגיה: Photon Ice Gold. חוקים: ענה בעברית בלבד, קצר ולעניין. ללא אמפתיה. אל תבטיח תוצאות מהטיפול הראשון. השתמש במושגים "טיפול מסור" ו"תמיד לקראתך". שאלות על מחיר או מבצעים: הפנה לוואטסאפ https://wa.me/972555633598. לקביעת תור: https://lee.co.il/b/C0ucE?tab=meetings`;

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-3-haiku-20240307',
        max_tokens: 512,
        system: SYSTEM_PROMPT,
        messages: messages
      })
    });

    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
