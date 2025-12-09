export type EngagementLevel = 'viewer' | 'follower' | 'supporter' | 'vip';

export interface UserProfile {
  id: string;
  nickname: string;
  avatar?: string;
  engagement: EngagementLevel;
}

export interface BaseLiveEvent {
  roomId: string;
  timestamp: number;
  user: UserProfile;
}

export interface ChatMessageEvent extends BaseLiveEvent {
  type: 'chat';
  messageId: string;
  text: string;
  viaGift: boolean;
  raw: unknown;
}

export interface GiftEvent extends BaseLiveEvent {
  type: 'gift';
  giftId: string;
  giftName: string;
  diamondCount: number;
  comboCount?: number;
  message?: string;
  raw: unknown;
}

export interface VoteEvent extends BaseLiveEvent {
  type: 'vote';
  option: string;
  weight: number;
  source: 'chat' | 'gift' | 'panel';
  referenceId: string;
  raw: unknown;
}

export type LiveRoomEvent = ChatMessageEvent | GiftEvent | VoteEvent;

export interface KeywordMatch {
  pattern: RegExp;
  matchedText: string;
  groups?: Record<string, string>;
}

export interface KeywordPayload {
  ruleId: string;
  event: ChatMessageEvent | GiftEvent;
  match: KeywordMatch;
}
