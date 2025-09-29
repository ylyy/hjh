// Background service worker: calls the AI API using stored settings.

const DEFAULT_MODEL = 'gpt-4o-mini';
const DEFAULT_SECONDS_PER_LINE = 10;

async function getSettings() {
  return new Promise((resolve) => {
    chrome.storage.sync.get(
      {
        apiKey: '',
        model: DEFAULT_MODEL,
        systemPrompt: 'You are an expert coding assistant. Provide concise, correct solutions with minimal explanation. Return plain text suitable for pasting. Avoid markdown fences unless necessary.',
        secondsPerLine: DEFAULT_SECONDS_PER_LINE
      },
      (result) => resolve(result)
    );
  });
}

async function callOpenAI({ apiKey, model, systemPrompt, prompt }) {
  const url = 'https://api.openai.com/v1/chat/completions';
  const body = {
    model,
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: prompt }
    ],
    temperature: 0.2,
    max_tokens: 2048
  };
  const resp = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify(body)
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`OpenAI error ${resp.status}: ${text}`);
  }
  const data = await resp.json();
  const content = data.choices?.[0]?.message?.content || '';
  return content.trim();
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === 'generate') {
    (async () => {
      try {
        const settings = await getSettings();
        if (!settings.apiKey) {
          sendResponse({ ok: false, error: 'Missing API key. Set it in the extension options.' });
          return;
        }
        const text = await callOpenAI({
          apiKey: settings.apiKey,
          model: settings.model || DEFAULT_MODEL,
          systemPrompt: settings.systemPrompt,
          prompt: message.payload?.prompt || ''
        });
        sendResponse({ ok: true, text, secondsPerLine: settings.secondsPerLine || DEFAULT_SECONDS_PER_LINE });
      } catch (err) {
        sendResponse({ ok: false, error: String(err?.message || err) });
      }
    })();
    return true; // keep the message channel open for async reply
  }
});

