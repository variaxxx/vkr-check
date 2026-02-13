export interface ApiResponse<T = any> {
  status: number;
  message: string;
  data: T | null;
}

export interface FindManyApiResponse<T = any> {
  total: number;
  count: number;
  items: T[];
}
