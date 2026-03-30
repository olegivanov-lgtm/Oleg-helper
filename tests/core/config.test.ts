import { describe, it, expect } from 'vitest';
import { loadConfig } from '../../src/core/config.js';

describe('loadConfig', () => {
  it('returns default config values', () => {
    const config = loadConfig();
    expect(config.version).toBe('0.1.0');
    expect(config.env).toBe('development');
  });
});
