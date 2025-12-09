import EventEmitter from 'eventemitter3';
import { LiveRoomEvent, KeywordPayload } from '../interfaces/liveRoom';

export type BaseEventMap = {
  'live:event': LiveRoomEvent;
  'live:keyword': KeywordPayload;
};

type Listener<T> = (payload: T) => void;

export class EventBus<TEvents extends Record<string, unknown> = BaseEventMap> {
  private readonly emitter = new EventEmitter();

  emit<TKey extends keyof TEvents>(event: TKey, payload: TEvents[TKey]): void {
    this.emitter.emit(event as string, payload);
  }

  on<TKey extends keyof TEvents>(event: TKey, listener: Listener<TEvents[TKey]>): void {
    this.emitter.on(event as string, listener as Listener<unknown>);
  }

  off<TKey extends keyof TEvents>(event: TKey, listener: Listener<TEvents[TKey]>): void {
    this.emitter.off(event as string, listener as Listener<unknown>);
  }
}
