import { BaseEventMap } from '../../core/events/eventBus';
import { GamePlugin, PluginContext } from '../../core/interfaces/gamePlugin';
import { KeywordPayload, LiveRoomEvent } from '../../core/interfaces/liveRoom';
import { logger } from '../../utils/logger';

interface VoteRecord {
  id: string;
  option: string;
  weight: number;
  voter: string;
  source: 'chat' | 'gift' | 'panel';
  timestamp: number;
}

export interface PuzzleSnapshot {
  windowSeconds: number;
  options: { option: string; total: number }[];
  leadingOption?: string;
  totalWeight: number;
  lastUpdated: number | null;
}

export type PuzzleEvents = {
  'game:puzzle:update': PuzzleSnapshot;
};

export type PuzzleEventMap = BaseEventMap & PuzzleEvents;

export interface PuzzleGameConfig {
  keywordRuleId: string;
  windowSeconds: number;
  options: string[];
  giftWeightMultiplier: number;
}

export class PuzzleVoteGame<
  TEvents extends BaseEventMap & PuzzleEvents = BaseEventMap & PuzzleEvents
> implements GamePlugin<TEvents> {
  readonly name = 'puzzle-vote';

  private context?: PluginContext<TEvents>;
  private readonly config: PuzzleGameConfig;
  private readonly votes: VoteRecord[] = [];

  constructor(config: PuzzleGameConfig) {
    this.config = config;
  }

  bootstrap(context: PluginContext<TEvents>): void {
    this.context = context;
    context.bus.on('live:keyword', this.handleKeyword);
  }

  handleEvent(event: LiveRoomEvent): void {
    if (event.type === 'vote') {
      this.recordVote({
        id: event.referenceId,
        option: event.option.toUpperCase(),
        weight: event.weight,
        voter: event.user.nickname,
        source: event.source,
        timestamp: event.timestamp,
      });
    }
  }

  getSnapshot(): PuzzleSnapshot {
    const { map, total } = this.computeWindow();
    const options = this.config.options.map((option) => ({
      option,
      total: map.get(option) ?? 0,
    }));
    const leading = options.reduce(
      (prev, current) => (current.total > prev.total ? current : prev),
      { option: '', total: 0 }
    );

    const lastVote = this.votes.length ? this.votes[this.votes.length - 1] : undefined;

    const snapshot: PuzzleSnapshot = {
      windowSeconds: this.config.windowSeconds,
      options,
      totalWeight: total,
      lastUpdated: lastVote ? lastVote.timestamp : null,
    };

    if (leading.option) {
      snapshot.leadingOption = leading.option;
    }

    return snapshot;
  }

  private handleKeyword = (payload: KeywordPayload): void => {
    if (payload.ruleId !== this.config.keywordRuleId) {
      return;
    }

    const optionFromRegex = payload.match.groups?.option ?? payload.match.matchedText;
    if (!optionFromRegex) {
      return;
    }

    const option = optionFromRegex.trim().toUpperCase();
    if (!this.config.options.includes(option)) {
      return;
    }

    const event = payload.event;
    const weightBase = event.type === 'gift' ? 1 + event.diamondCount * this.config.giftWeightMultiplier : 1;

    this.recordVote({
      id: `${event.user.id}-${Date.now()}`,
      option,
      voter: event.user.nickname,
      weight: weightBase,
      source: event.type === 'gift' ? 'gift' : 'chat',
      timestamp: Date.now(),
    });
  };

  private recordVote(record: VoteRecord): void {
    this.votes.push(record);
    this.gc();
    this.broadcast();
    logger.debug('记录投票', { option: record.option, weight: record.weight, voter: record.voter });
  }

  private gc(): void {
    const threshold = Date.now() - this.config.windowSeconds * 1000;
    while (this.votes.length > 0) {
      const head = this.votes[0];
      if (!head || head.timestamp >= threshold) {
        break;
      }
      this.votes.shift();
    }
  }

  private computeWindow(): { map: Map<string, number>; total: number } {
    this.gc();
    const map = new Map<string, number>();
    let total = 0;
    this.votes.forEach((vote) => {
      map.set(vote.option, (map.get(vote.option) ?? 0) + vote.weight);
      total += vote.weight;
    });
    return { map, total };
  }

  private broadcast(): void {
    if (!this.context) {
      return;
    }

    this.context.bus.emit('game:puzzle:update', this.getSnapshot());
  }
}
