import { api } from "@/lib/api";
import type { UsuarioBasico } from "@/types/user";

export async function listUsuariosBasico(): Promise<UsuarioBasico[]> {
  const response = await api.get<UsuarioBasico[]>("/users/basico");
  return response.data;
}
