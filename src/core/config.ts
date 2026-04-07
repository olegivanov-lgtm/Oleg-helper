import 'dotenv/config';

export interface AppConfig {
  version: string;
  env: string;
  trello: {
    apiKey: string;
    token: string;
    boardId: string;
  };
}

export function loadConfig(): AppConfig {
  const apiKey = process.env.TRELLO_API_KEY;
  const token = process.env.TRELLO_TOKEN;
  const boardId = process.env.TRELLO_BOARD_ID;

  if (!apiKey || !token || !boardId) {
    throw new Error('Missing required Trello env vars: TRELLO_API_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID');
  }

  return {
    version: '0.1.0',
    env: process.env.NODE_ENV ?? 'development',
    trello: { apiKey, token, boardId },
  };
}
