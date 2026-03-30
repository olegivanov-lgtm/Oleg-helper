import { loadConfig } from './config.js';

interface App {
  start: () => void;
}

export function createApp(): App {
  const config = loadConfig();

  return {
    start() {
      process.stdout.write(`Oleg-helper v${config.version} started\n`);
    },
  };
}
