import { describe, it, expect, beforeEach } from 'vitest';
import { loadConfig } from '../../src/core/config.js';

describe('loadConfig', () => {
  beforeEach(() => {
    process.env.TRELLO_API_KEY = 'test-key';
    process.env.TRELLO_TOKEN = 'test-token';
    process.env.TRELLO_BOARD_ID = 'test-board';
  });

  it('returns config with trello credentials', () => {
    const config = loadConfig();
    expect(config.version).toBe('0.1.0');
    expect(config.env).toBe('test');
    expect(config.trello.apiKey).toBe('test-key');
    expect(config.trello.token).toBe('test-token');
    expect(config.trello.boardId).toBe('test-board');
  });

  it('throws when trello env vars are missing', () => {
    delete process.env.TRELLO_API_KEY;
    expect(() => loadConfig()).toThrow('Missing required Trello env vars');
  });
});
