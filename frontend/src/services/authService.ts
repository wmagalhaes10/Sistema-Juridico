import { api } from "@/lib/api";
import type { TokenResponse, Usuario } from "@/types/auth";

export async function login(email: string, senha: string): Promise<TokenResponse> {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", senha);

  const response = await api.post<TokenResponse>("/auth/login", body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return response.data;
}

export async function me(): Promise<Usuario> {
  const response = await api.get<Usuario>("/auth/me");
  return response.data;
}
