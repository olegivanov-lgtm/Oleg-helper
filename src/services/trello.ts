import https from 'node:https';
import type { TrelloBoard, TrelloCard, TrelloList, ServiceResult } from '../types/index.js';

interface TrelloConfig {
  apiKey: string;
  token: string;
  boardId: string;
}

export class TrelloService {
  private apiKey: string;
  private token: string;
  private boardId: string;
  private baseUrl = 'api.trello.com';

  constructor(config: TrelloConfig) {
    this.apiKey = config.apiKey;
    this.token = config.token;
    this.boardId = config.boardId;
  }

  private request<T>(path: string, method = 'GET', body?: Record<string, string>): Promise<T> {
    const separator = path.includes('?') ? '&' : '?';
    const authParams = `key=${this.apiKey}&token=${this.token}`;
    const fullPath = `/1${path}${separator}${authParams}`;

    return new Promise((resolve, reject) => {
      const options: https.RequestOptions = {
        hostname: this.baseUrl,
        path: fullPath,
        method,
        headers: { 'Content-Type': 'application/json' },
      };

      const req = https.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => (data += chunk));
        res.on('end', () => {
          if (res.statusCode && res.statusCode >= 400) {
            reject(new Error(`Trello API error ${res.statusCode}: ${data}`));
            return;
          }
          resolve(JSON.parse(data) as T);
        });
      });

      req.on('error', reject);

      if (body) {
        req.write(JSON.stringify(body));
      }
      req.end();
    });
  }

  async getBoard(): Promise<ServiceResult<TrelloBoard>> {
    try {
      const board = await this.request<TrelloBoard>(
        `/boards/${this.boardId}?fields=id,name,desc,url`,
      );
      return { success: true, data: board };
    } catch (e) {
      return { success: false, error: (e as Error).message };
    }
  }

  async getLists(): Promise<ServiceResult<TrelloList[]>> {
    try {
      const lists = await this.request<TrelloList[]>(
        `/boards/${this.boardId}/lists?fields=id,name`,
      );
      return { success: true, data: lists };
    } catch (e) {
      return { success: false, error: (e as Error).message };
    }
  }

  async getCards(listId?: string): Promise<ServiceResult<TrelloCard[]>> {
    try {
      const path = listId
        ? `/lists/${listId}/cards?fields=id,name,desc,idList,due,labels,url`
        : `/boards/${this.boardId}/cards?fields=id,name,desc,idList,due,labels,url`;
      const cards = await this.request<TrelloCard[]>(path);
      return { success: true, data: cards };
    } catch (e) {
      return { success: false, error: (e as Error).message };
    }
  }

  async createCard(listId: string, name: string, desc = ''): Promise<ServiceResult<TrelloCard>> {
    try {
      const card = await this.request<TrelloCard>(
        `/cards?idList=${listId}&name=${encodeURIComponent(name)}&desc=${encodeURIComponent(desc)}`,
        'POST',
      );
      return { success: true, data: card };
    } catch (e) {
      return { success: false, error: (e as Error).message };
    }
  }

  async moveCard(cardId: string, listId: string): Promise<ServiceResult<TrelloCard>> {
    try {
      const card = await this.request<TrelloCard>(
        `/cards/${cardId}?idList=${listId}`,
        'PUT',
      );
      return { success: true, data: card };
    } catch (e) {
      return { success: false, error: (e as Error).message };
    }
  }
}
