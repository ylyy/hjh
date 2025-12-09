import { AiStoryAdapter, StoryChunk, StoryPrompt } from '../../core/adapters/aiStoryAdapter';
import { BaseEventMap } from '../../core/events/eventBus';
import { GamePlugin, PluginContext } from '../../core/interfaces/gamePlugin';
import { KeywordPayload } from '../../core/interfaces/liveRoom';
import { logger } from '../../utils/logger';

interface Contribution {
  id: string;
  userId: string;
  nickname: string;
  keywords: string[];
  seed: string;
  giftValue: number;
}

export interface NovelChunkBroadcast extends StoryChunk {
  contributor: Contribution;
  queueLength: number;
}

export type NovelEvents = {
  'game:novel:chunk': NovelChunkBroadcast;
};

export type NovelEventMap = BaseEventMap & NovelEvents;

export interface NovelGameConfig {
  keywordRuleId: string;
  minGiftDiamonds: number;
  defaultStyle: string;
  requireGiftToTrigger?: boolean;
}

export class NovelStoryGame<
  TEvents extends BaseEventMap & NovelEvents = BaseEventMap & NovelEvents
> implements GamePlugin<TEvents> {
  readonly name = 'novel-story';

  private context?: PluginContext<TEvents>;
  private readonly adapter: AiStoryAdapter;
  private readonly config: NovelGameConfig;
  private readonly queue: Contribution[] = [];
  private readonly story: StoryChunk[] = [];
  private processing = false;

  constructor(adapter: AiStoryAdapter, config: NovelGameConfig) {
    this.adapter = adapter;
    this.config = config;
  }

  bootstrap(context: PluginContext<TEvents>): void {
    this.context = context;
    context.bus.on('live:keyword', this.handleKeyword);
  }

  handleEvent(): void {
    // Novel 模块主要依赖 Keyword 事件，普通 live:event 在这里暂时不处理
  }

  getSnapshot(): unknown {
    return {
      story: this.story,
      queue: this.queue,
      processing: this.processing,
    };
  }

  private handleKeyword = async (payload: KeywordPayload): Promise<void> => {
    if (payload.ruleId !== this.config.keywordRuleId) {
      return;
    }

    const { event } = payload;

    if (this.config.requireGiftToTrigger && event.type !== 'gift') {
      return;
    }

    if (event.type === 'gift' && event.diamondCount < this.config.minGiftDiamonds) {
      return;
    }

    const giftValue = event.type === 'gift' ? event.diamondCount : 0;

    const contribution: Contribution = {
      id: `${event.user.id}-${Date.now()}`,
      userId: event.user.id,
      nickname: event.user.nickname,
      keywords: this.extractKeywords(payload.match.matchedText),
      seed: event.type === 'gift' ? event.message ?? '' : event.text,
      giftValue,
    };

    this.queue.push(contribution);
    void this.flushQueue();
  };

  private extractKeywords(text: string): string[] {
    return text
      .replace(/[#，。,.!！?？]/g, ' ')
      .split(/\s+/)
      .map((item) => item.trim())
      .filter(Boolean);
  }

  private async flushQueue(): Promise<void> {
    if (!this.context || this.processing || this.queue.length === 0) {
      return;
    }

    const next = this.queue.shift();
    if (!next) {
      return;
    }

    this.processing = true;
    try {
      const prompt: StoryPrompt = {
        roomId: this.context.roomId,
        protagonist: next.nickname,
        style: this.config.defaultStyle,
        seed: next.seed || '直播间互动',
        keywords: next.keywords,
      };

      const chunk = await this.adapter.generateChunk(prompt);
      this.story.push(chunk);
      if (this.story.length > 20) {
        this.story.shift();
      }

      const broadcast: NovelChunkBroadcast = {
        ...chunk,
        contributor: next,
        queueLength: this.queue.length,
      };

      this.context.bus.emit('game:novel:chunk', broadcast);
      logger.info('生成新的小说片段', { contributor: next.nickname });
    } catch (error) {
      logger.error('小说生成失败', {
        error: error instanceof Error ? error.message : String(error),
      });
    } finally {
      this.processing = false;
      if (this.queue.length > 0) {
        void this.flushQueue();
      }
    }
  }
}
