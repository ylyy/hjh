import EventEmitter from 'eventemitter3';
import axios from 'axios';
import { LiveRoomEvent } from '../../core/interfaces/liveRoom';
import { logger } from '../../utils/logger';

export interface DouyinGatewayConfig {
  roomId: string;
  deviceId?: string;
  pollIntervalMs?: number;
}

const DEFAULT_POLL_INTERVAL = 2500;

export class DouyinLiveGateway {
  private readonly emitter = new EventEmitter();
  private readonly config: DouyinGatewayConfig;
  private timer?: NodeJS.Timeout;
  private running = false;

  constructor(config: DouyinGatewayConfig) {
    this.config = { ...config, pollIntervalMs: config.pollIntervalMs ?? DEFAULT_POLL_INTERVAL };
  }

  start(): void {
    if (this.running) {
      return;
    }

    logger.info('启动抖音采集任务', { roomId: this.config.roomId });
    this.running = true;
    this.scheduleNextPoll();
  }

  stop(): void {
    this.running = false;
    if (this.timer) {
      clearTimeout(this.timer);
    }
    logger.info('已停止抖音采集任务', { roomId: this.config.roomId });
  }

  onEvent(listener: (payload: LiveRoomEvent) => void): void {
    this.emitter.on('event', listener);
  }

  offEvent(listener: (payload: LiveRoomEvent) => void): void {
    this.emitter.off('event', listener);
  }

  /**
   * 方便离线调试或自动化测试直接写入事件
   */
  ingestSimulatedEvent(event: LiveRoomEvent): void {
    this.emitter.emit('event', event);
  }

  private scheduleNextPoll(): void {
    if (!this.running) {
      return;
    }

    this.timer = setTimeout(async () => {
      try {
        const events = await this.fetchLiveEvents();
        events.forEach((event) => this.emitter.emit('event', event));
      } catch (error) {
        logger.error('抖音采集失败', {
          roomId: this.config.roomId,
          error: error instanceof Error ? error.message : String(error),
        });
      } finally {
        this.scheduleNextPoll();
      }
    }, this.config.pollIntervalMs);
  }

  private async fetchLiveEvents(): Promise<LiveRoomEvent[]> {
    if (!this.config.deviceId) {
      // 未配置真实设备ID时直接返回空，避免误调用
      return [];
    }

    const params = new URLSearchParams({
      device_platform: 'web',
      aid: '6383',
      room_id: this.config.roomId,
      device_id: this.config.deviceId,
    });

    const url = `https://live.douyin.com/webcast/room/web/enter/?${params.toString()}`;
    const response = await axios.get(url, {
      headers: {
        Cookie: `device_id=${this.config.deviceId}`,
      },
    });

    // TODO: 解析 Douyin 返回的数据，这里先返回空数组，避免耦合具体协议
    logger.debug('收到抖音原始数据', { size: JSON.stringify(response.data).length });
    return [];
  }
}
