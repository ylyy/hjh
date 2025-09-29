// Content script: captures copied text, waits for next click into an editable target,
// requests background to generate an answer, then types it slowly (~10s per line).

(() => {
  const STATE = {
    lastCopiedText: '',
    pendingClickResolve: null,
    isTyping: false,
  };

  function isEditableTarget(target) {
    if (!target) return false;
    const tag = (target.tagName || '').toLowerCase();
    if (tag === 'textarea') return true;
    if (tag === 'input') {
      const type = (target.type || '').toLowerCase();
      return ['text', 'search', 'email', 'url', 'password', 'tel', 'number'].includes(type) || !type;
    }
    const contentEditable = target.getAttribute && target.getAttribute('contenteditable');
    return contentEditable === '' || contentEditable === 'true';
  }

  function getActiveEditable(target) {
    if (isEditableTarget(target)) return target;
    if (isEditableTarget(document.activeElement)) return document.activeElement;
    return null;
  }

  async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async function typeInto(target, text, perCharMs) {
    // For inputs/textarea, we can set selection and value; for contenteditable, insert text nodes
    const isContentEditable = !!(target.isContentEditable);
    for (let i = 0; i < text.length; i++) {
      const ch = text[i];
      if (isContentEditable) {
        document.execCommand('insertText', false, ch);
      } else {
        const start = target.selectionStart ?? target.value.length;
        const end = target.selectionEnd ?? target.value.length;
        const before = target.value.slice(0, start);
        const after = target.value.slice(end);
        target.value = before + ch + after;
        const newPos = start + 1;
        target.setSelectionRange?.(newPos, newPos);
        target.dispatchEvent(new Event('input', { bubbles: true }));
        target.dispatchEvent(new Event('change', { bubbles: true }));
      }
      await sleep(perCharMs);
    }
  }

  async function typeLines(target, text, secondsPerLine) {
    const lines = text.replace(/\r\n/g, '\n').split('\n');
    if (!lines.length) return;
    const perCharMsBase = 25; // baseline speed; we will stretch line timing to ~secondsPerLine
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const startTime = Date.now();
      // type the line
      await typeInto(target, line, perCharMsBase);
      // newline between lines
      await typeInto(target, '\n', perCharMsBase);
      // Ensure total time per line ~= secondsPerLine
      const elapsed = (Date.now() - startTime) / 1000;
      const remaining = Math.max(0, secondsPerLine - elapsed);
      if (remaining > 0) await sleep(remaining * 1000);
    }
  }

  // Listen for copy events to capture the problem statement
  document.addEventListener('copy', () => {
    try {
      const selection = document.getSelection?.()?.toString?.() || '';
      if (selection.trim()) {
        STATE.lastCopiedText = selection.trim();
        // Visual hint (non-intrusive)
        console.debug('[AI Copy → Click → Type] Captured copied text, click into an input to answer.');
      }
    } catch (e) {
      // ignore
    }
  }, true);

  // Next click into an editable field triggers generation and typing
  document.addEventListener('mousedown', async (ev) => {
    if (!STATE.lastCopiedText || STATE.isTyping) return;
    const target = ev.target;
    const editable = getActiveEditable(target);
    if (!editable) return;

    // Prevent re-entry while we work
    STATE.isTyping = true;
    try {
      editable.focus?.();
      const prompt = STATE.lastCopiedText;
      const response = await chrome.runtime.sendMessage({
        type: 'generate',
        payload: { prompt }
      });
      if (response && response.ok && response.text) {
        await typeLines(editable, response.text, response.secondsPerLine || 10);
      } else {
        console.warn('[AI Copy → Click → Type] Generation failed:', response?.error);
      }
    } catch (err) {
      console.error('[AI Copy → Click → Type] Error:', err);
    } finally {
      // Reset so a new copy-then-click flow is required
      STATE.lastCopiedText = '';
      STATE.isTyping = false;
    }
  }, true);
})();

