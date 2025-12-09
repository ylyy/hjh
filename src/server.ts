import cors from 'cors';
import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import { loadConfig } from './config/env';
import { EventBus, BaseEventMap } from './core/events/eventBus';
import { MockAiStoryAdapter } from './core/adapters/aiStoryAdapter';
import { NovelStoryGame, NovelChunkBroadcast } from './games/novel/novelStoryGame';
import { PuzzleVoteGame, PuzzleSnapshot } from './games/puzzle/puzzleVoteGame';
import { DouyinLiveGateway } from './infra/douyin/liveRoomClient';
import { LivePipelineService, KeywordRule } from './services/livePipelineService';
import { buildAdminRouter } from './routes/adminRoutes';
import { logger } from './utils/logger';

export type BackendEventMap = BaseEventMap & {
  'game:novel:chunk': NovelChunkBroadcast;
  'game:puzzle:update': PuzzleSnapshot;
};

const config = loadConfig();
const bus = new EventBus<BackendEventMap>();

const gateway = new DouyinLiveGateway({
  roomId: config.DOUYIN_ROOM_ID,
  ...(config.DOUYIN_DEVICE_ID ? { deviceId: config.DOUYIN_DEVICE_ID } : {}),
});

const defaultRules: KeywordRule[] = [
  {
    id: 'novel-hashtag',
    pattern: /#(小说|改编|剧情)[^\s]*/i,
    targets: ['chat', 'gift'],
    requiresGift: false,
    minDiamond: config.STORY_MIN_GIFTS,
    description: '送礼附带 #小说/#改编 触发剧情改编',
  },
  {
    id: 'puzzle-vote',
    pattern: /#?(vote|投票)\s*(?<option>[A-Z0-9])/i,
    targets: ['chat', 'gift'],
    requiresGift: false,
    description: '弹幕/礼物携带 #vote A/B/C 表示投票',
  },
];

if (config.KEYWORD_REGEX) {
  defaultRules.push({
    id: 'custom-env-regex',
    pattern: new RegExp(config.KEYWORD_REGEX, 'i'),
    targets: ['chat', 'gift'],
    requiresGift: false,
    description: '来自环境变量 KEYWORD_REGEX 的自定义规则',
  });
}

const pipeline = new LivePipelineService<BackendEventMap>(gateway, bus, { rules: defaultRules });
const novelGame = new NovelStoryGame<BackendEventMap>(new MockAiStoryAdapter(), {
  keywordRuleId: 'novel-hashtag',
  minGiftDiamonds: config.STORY_MIN_GIFTS,
  defaultStyle: '互动弹幕小说',
});
const puzzleGame = new PuzzleVoteGame<BackendEventMap>({
  keywordRuleId: 'puzzle-vote',
  windowSeconds: config.PUZZLE_WINDOW_SECONDS,
  options: config.PUZZLE_OPTIONS.map((option) => option.toUpperCase()),
  giftWeightMultiplier: 0.2,
});

pipeline.registerPlugin(novelGame, config.DOUYIN_ROOM_ID);
pipeline.registerPlugin(puzzleGame, config.DOUYIN_ROOM_ID);
pipeline.start();

const app = express();
app.use(cors());
app.use(express.json());
app.use('/api', buildAdminRouter<BackendEventMap>({ pipeline, plugins: [novelGame, puzzleGame], gateway }));

const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: '*',
  },
});

bus.on('live:event', (event) => io.emit('live:event', event));
bus.on('game:novel:chunk', (chunk) => io.emit('novel:chunk', chunk));
bus.on('game:puzzle:update', (snapshot) => io.emit('puzzle:update', snapshot));

const port = config.PORT;
httpServer.listen(port, () => {
  logger.info('AIGC 后台已启动', { port, roomId: config.DOUYIN_ROOM_ID });
});
