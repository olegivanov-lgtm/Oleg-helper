export interface AppConfig {
  version: string;
  env: string;
}

export function loadConfig(): AppConfig {
  return {
    version: '0.1.0',
    env: process.env.NODE_ENV ?? 'development',
  };
}
