import { BaseEventMap, EventBus } from '../events/eventBus';
import { LiveRoomEvent } from './liveRoom';

export interface PluginContext<TEvents extends Record<string, unknown>> {
  bus: EventBus<TEvents>;
  roomId: string;
}

export interface GamePlugin<TEvents extends Record<string, unknown>> {
  readonly name: string;
  bootstrap(context: PluginContext<TEvents>): void;
  handleEvent(event: LiveRoomEvent): void;
  getSnapshot(): unknown;
}
