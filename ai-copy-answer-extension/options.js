document.addEventListener('DOMContentLoaded', () => {
  const apiKeyEl = document.getElementById('apiKey');
  const modelEl = document.getElementById('model');
  const systemPromptEl = document.getElementById('systemPrompt');
  const secondsPerLineEl = document.getElementById('secondsPerLine');
  const saveBtn = document.getElementById('save');
  const statusEl = document.getElementById('status');

  function setStatus(text, kind = 'success') {
    statusEl.textContent = text;
    statusEl.className = kind;
  }

  chrome.storage.sync.get(
    {
      apiKey: '',
      model: 'gpt-4o-mini',
      systemPrompt: 'You are an expert coding assistant. Provide concise, correct solutions with minimal explanation. Return plain text suitable for pasting. Avoid markdown fences unless necessary.',
      secondsPerLine: 10
    },
    (cfg) => {
      apiKeyEl.value = cfg.apiKey || '';
      modelEl.value = cfg.model || 'gpt-4o-mini';
      systemPromptEl.value = cfg.systemPrompt || '';
      secondsPerLineEl.value = cfg.secondsPerLine || 10;
    }
  );

  saveBtn.addEventListener('click', () => {
    const apiKey = apiKeyEl.value.trim();
    if (!apiKey) {
      setStatus('API key is required', 'error');
      return;
    }
    const model = modelEl.value.trim() || 'gpt-4o-mini';
    const systemPrompt = systemPromptEl.value.trim();
    const secondsPerLine = Math.max(1, Math.min(60, parseInt(secondsPerLineEl.value, 10) || 10));
    chrome.storage.sync.set({ apiKey, model, systemPrompt, secondsPerLine }, () => {
      setStatus('Saved');
      setTimeout(() => setStatus(''), 1500);
    });
  });
});

