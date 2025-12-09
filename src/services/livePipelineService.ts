import { DouyinLiveGateway } from '../infra/douyin/liveRoomClient';
import { BaseEventMap, EventBus } from '../core/events/eventBus';
import { GamePlugin } from '../core/interfaces/gamePlugin';
import { ChatMessageEvent, GiftEvent, KeywordPayload, LiveRoomEvent } from '../core/interfaces/liveRoom';
import { logger } from '../utils/logger';

export type KeywordTarget = 'chat' | 'gift';

export interface KeywordRule {
  id: string;
  pattern: RegExp;
  targets: KeywordTarget[];
  requiresGift?: boolean;
  minDiamond?: number;
  description?: string;
}

export interface PipelineOptions {
  rules: KeywordRule[];
}

export class LivePipelineService<TEvents extends BaseEventMap = BaseEventMap> {
  private readonly plugins: GamePlugin<TEvents>[] = [];
  private readonly activeRules: Map<string, KeywordRule> = new Map();
  private readonly handleGatewayEvent = (event: LiveRoomEvent) => this.handleEvent(event);

  constructor(
    private readonly gateway: DouyinLiveGateway,
    private readonly bus: EventBus<TEvents>,
    private readonly options: PipelineOptions
  ) {
    options.rules.forEach((rule) => this.activeRules.set(rule.id, rule));
  }

  start(): void {
    logger.info('LivePipeline 启动');
    this.gateway.onEvent(this.handleGatewayEvent);
    this.gateway.start();
  }

  stop(): void {
    this.gateway.offEvent(this.handleGatewayEvent);
    this.gateway.stop();
  }

  registerPlugin(plugin: GamePlugin<TEvents>, roomId: string): void {
    plugin.bootstrap({ bus: this.bus, roomId });
    this.plugins.push(plugin);
    logger.info('插件已注册', { name: plugin.name });
  }

  upsertRule(rule: KeywordRule): void {
    this.activeRules.set(rule.id, rule);
  }

  removeRule(ruleId: string): void {
    this.activeRules.delete(ruleId);
  }

  listRules(): KeywordRule[] {
    return Array.from(this.activeRules.values());
  }

  private handleEvent(event: LiveRoomEvent): void {
    this.bus.emit('live:event', event);
    this.plugins.forEach((plugin) => plugin.handleEvent(event));
    this.extractKeywords(event);
  }

  private extractKeywords(event: LiveRoomEvent): void {
    const rules = Array.from(this.activeRules.values());
    rules.forEach((rule) => {
      if (event.type === 'chat' && rule.targets.includes('chat')) {
        this.dispatchKeyword(rule, event);
      }
      if (event.type === 'gift' && rule.targets.includes('gift')) {
        if (rule.requiresGift && event.diamondCount < (rule.minDiamond ?? 1)) {
          return;
        }
        this.dispatchKeyword(rule, event);
      }
    });
  }

  private dispatchKeyword(rule: KeywordRule, event: ChatMessageEvent | GiftEvent): void {
    const text = event.type === 'chat' ? event.text : event.message ?? '';
    if (!text) {
      return;
    }

    const match = text.match(rule.pattern);
    if (!match) {
      return;
    }

    const keywordMatch: KeywordPayload['match'] = {
      pattern: rule.pattern,
      matchedText: match[0],
    };

    if (match.groups) {
      const groups = Object.fromEntries(
        Object.entries(match.groups).filter(
          (entry): entry is [string, string] => typeof entry[1] === 'string'
        )
      );
      if (Object.keys(groups).length > 0) {
        keywordMatch.groups = groups;
      }
    }

    const payload: KeywordPayload = {
      ruleId: rule.id,
      event,
      match: keywordMatch,
    };

    this.bus.emit('live:keyword', payload);
  }
}
