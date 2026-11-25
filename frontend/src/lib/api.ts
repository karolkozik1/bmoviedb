const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Genre = { id: number; name: string };

export type Movie = {
  id: number;
  title: string;
  original_title: string | null;
  description: string | null;
  release_year: number | null;
  duration_minutes: number | null;
  rating: number | null;
  average_rating: number | null;
  rating_count: number;
  genres: Genre[];
};

export type User = { id: number; username: string; email: string };
export type Rating = { id: number; rating: number };
export type Review = {
  id: number;
  user_id: number;
  content: string | null;
  status: string;
  created_at: string;
};

type RequestOptions = Omit<RequestInit, "headers"> & {
  token?: string | null;
  headers?: HeadersInit;
};

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { token, headers: extraHeaders, ...requestOptions } = options;
  const headers = new Headers(extraHeaders);
  if (requestOptions.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_URL}${path}`, {
    ...requestOptions,
    headers,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = body?.detail;
    throw new Error(
      typeof detail === "string"
        ? detail
        : `Request failed (${response.status})`,
    );
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
