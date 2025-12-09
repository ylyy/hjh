export interface StoryPrompt {
  roomId: string;
  protagonist: string;
  style: string;
  seed: string;
  keywords: string[];
}

export interface StoryChunk {
  id: string;
  title: string;
  content: string;
  suggestedNextPrompt?: string;
}

export interface AiStoryAdapter {
  generateChunk(prompt: StoryPrompt): Promise<StoryChunk>;
}

export class MockAiStoryAdapter implements AiStoryAdapter {
  async generateChunk(prompt: StoryPrompt): Promise<StoryChunk> {
    const now = new Date().toISOString();
    return {
      id: now,
      title: `${prompt.style} · ${prompt.keywords.join('/')}`,
      content: `【${prompt.protagonist}】踏入新的章节：${prompt.seed}，线索来自 ${prompt.keywords.join('、')}。`,
      suggestedNextPrompt: '结合新的弹幕提示继续推进剧情。',
    };
  }
}
