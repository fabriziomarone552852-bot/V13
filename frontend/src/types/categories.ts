export interface Category {
  id: number;
  category_name: string;
  colore: string | null;
  user_id: number | null;
  genre: number;
}

export const CategoryGenre = {
  TASKS: 1,
  EVENTS: 2,
  COMMON: 3,
  MOOD: 4,
} as const;

export type CategoryGenre = typeof CategoryGenre[keyof typeof CategoryGenre];

export interface CategoryCreatePayload {
  category_name: string;
  colore?: string | null;
  genre?: number;
}