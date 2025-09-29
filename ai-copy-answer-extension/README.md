AI Copy → Click → Type

Overview

This Chrome extension lets you:
- Copy a problem statement (e.g., a coding exercise)
- Click into any text field / editor on a web page
- It calls an AI model to produce an answer and types it in slowly (~10s/line)

Install (Developer Mode)

1. Build step: none — this is plain JS.
2. Go to chrome://extensions and enable Developer mode.
3. Click "Load unpacked" and select this folder.
4. Open Options for the extension and paste your OpenAI API key, adjust settings.

Usage

1. Copy a question or prompt on any page (Ctrl/Cmd+C).
2. Click into a text input/textarea/contenteditable area.
3. The extension generates an answer and types it in line by line.

Settings

- API Key: OpenAI API key used to call the model.
- Model: e.g., gpt-4o-mini.
- Seconds per line: default 10 seconds per line. The script types characters steadily and adds a delay so each line roughly takes this long.
- System prompt: controls AI style; defaults to concise, correct answers in plain text.

Privacy & Notes

- Copied text is not stored persistently; it stays in-memory in the content script until the next click.
- The generated answer is produced via the OpenAI API using your key.
- Works on most sites with standard inputs and contenteditable editors.

Troubleshooting

- If nothing happens after clicking into a field, check the Options page for a valid API key and that the page matches the content script (this extension runs on all URLs by default).
- Some editors intercept typing events differently. Try a plain textarea if needed.

