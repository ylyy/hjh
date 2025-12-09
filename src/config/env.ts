import dotenv from 'dotenv';
import { z } from 'zod';

dotenv.config();

const configSchema = z.object({
  PORT: z.coerce.number().default(4000),
  DOUYIN_ROOM_ID: z.string().min(1, '房间号不能为空'),
  DOUYIN_DEVICE_ID: z.string().optional(),
  KEYWORD_REGEX: z
    .string()
    .optional()
    .transform(
      (value) => value ?? '#(小说|改编)|#(vote|投票)\\s*(?<option>[A-Z]|\\d+)'
    ),
  STORY_MIN_GIFTS: z.coerce.number().default(1),
  PUZZLE_WINDOW_SECONDS: z.coerce.number().default(30),
  PUZZLE_OPTIONS: z
    .string()
    .default('A,B,C')
    .transform((value) => value.split(',').map((option) => option.trim()).filter(Boolean)),
  AIGC_STORY_API_KEY: z.string().optional(),
  AIGC_STORY_BASE_URL: z.string().optional(),
});

export type AppConfig = z.infer<typeof configSchema>;

let cachedConfig: AppConfig | null = null;

export const loadConfig = (): AppConfig => {
  if (cachedConfig) {
    return cachedConfig;
  }

  const parsed = configSchema.safeParse(process.env);
  if (!parsed.success) {
    throw new Error(`配置解析失败: ${parsed.error.message}`);
  }

  cachedConfig = parsed.data;
  return cachedConfig;
};
