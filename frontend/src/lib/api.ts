import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "@/lib/tokenStorage";
import type { TokenResponse } from "@/types/auth";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.set("Authorization", `Bearer ${token}`);
  }
  return config;
});

let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    throw new Error("Sem refresh token disponível");
  }

  const response = await axios.post<TokenResponse>(`${api.defaults.baseURL}/auth/refresh`, {
    refresh_token: refreshToken,
  });
  setTokens(response.data.access_token, response.data.refresh_token);
  return response.data.access_token;
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry && getRefreshToken()) {
      originalRequest._retry = true;
      try {
        refreshPromise ??= refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
        const novoToken = await refreshPromise;
        originalRequest.headers.set("Authorization", `Bearer ${novoToken}`);
        return api(originalRequest);
      } catch {
        clearTokens();
        window.location.href = "/login";
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  },
);
