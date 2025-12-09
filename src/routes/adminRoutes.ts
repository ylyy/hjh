import { Router } from 'express';
import { LivePipelineService, KeywordRule, KeywordTarget } from '../services/livePipelineService';
import { GamePlugin } from '../core/interfaces/gamePlugin';
import { BaseEventMap } from '../core/events/eventBus';
import { DouyinLiveGateway } from '../infra/douyin/liveRoomClient';
import { LiveRoomEvent } from '../core/interfaces/liveRoom';
import { logger } from '../utils/logger';

interface AdminRouteDeps<TEvents extends BaseEventMap> {
  pipeline: LivePipelineService<TEvents>;
  plugins: GamePlugin<TEvents>[];
  gateway: DouyinLiveGateway;
}

const parsePattern = (pattern: string): RegExp => {
  try {
    return new RegExp(pattern, 'i');
  } catch (error) {
    logger.warn('正则解析失败，尝试默认转义', { pattern });
    return new RegExp(pattern.replace(/\\/g, '\\\\'), 'i');
  }
};

export const buildAdminRouter = <TEvents extends BaseEventMap>({
  pipeline,
  plugins,
  gateway,
}: AdminRouteDeps<TEvents>): Router => {
  const router = Router();

  router.get('/health', (_req, res) => {
    res.json({ status: 'ok', timestamp: Date.now() });
  });

  router.get('/rules', (_req, res) => {
    const payload = pipeline.listRules().map((rule) => ({ ...rule, pattern: rule.pattern.source }));
    res.json(payload);
  });

  router.post('/rules', (req, res) => {
    const payload = req.body as Partial<KeywordRule> & { pattern: string };
    if (!payload.id || !payload.pattern) {
      return res.status(400).json({ message: 'id 与 pattern 必填' });
    }

    const rawTargets = Array.isArray(payload.targets) ? payload.targets : ['chat'];
    const targets = rawTargets.filter((target): target is KeywordTarget => target === 'chat' || target === 'gift');
    if (targets.length === 0) {
      targets.push('chat');
    }

    const rule: KeywordRule = {
      id: payload.id,
      pattern: parsePattern(payload.pattern),
      targets,
      requiresGift: payload.requiresGift ?? false,
    };

    if (typeof payload.minDiamond === 'number') {
      rule.minDiamond = payload.minDiamond;
    }
    if (typeof payload.description === 'string') {
      rule.description = payload.description;
    }

    pipeline.upsertRule(rule);
    res.json({ message: 'ok' });
  });

  router.delete('/rules/:id', (req, res) => {
    pipeline.removeRule(req.params.id);
    res.json({ message: 'ok' });
  });

  router.get('/state', (_req, res) => {
    const snapshots = plugins.map((plugin) => ({
      plugin: plugin.name,
      snapshot: plugin.getSnapshot(),
    }));
    res.json({ snapshots });
  });

  router.post('/simulate', (req, res) => {
    const event = req.body as LiveRoomEvent;
    if (!event || !event.type) {
      return res.status(400).json({ message: '事件数据不合法' });
    }

    gateway.ingestSimulatedEvent({ ...event, timestamp: event.timestamp ?? Date.now() });
    res.json({ message: 'queued' });
  });

  return router;
};
