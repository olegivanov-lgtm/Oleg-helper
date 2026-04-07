export interface ServiceResult<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface TrelloList {
  id: string;
  name: string;
}

export interface TrelloLabel {
  id: string;
  name: string;
  color: string;
}

export interface TrelloCard {
  id: string;
  name: string;
  desc: string;
  idList: string;
  due: string | null;
  labels: TrelloLabel[];
  url: string;
}

export interface TrelloBoard {
  id: string;
  name: string;
  desc: string;
  url: string;
}
