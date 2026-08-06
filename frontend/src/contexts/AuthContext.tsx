import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import { clearTokens, getAccessToken, setTokens } from "@/lib/tokenStorage";
import { login as loginRequest, me as meRequest } from "@/services/authService";
import type { Usuario } from "@/types/auth";

interface AuthContextValue {
  usuario: Usuario | null;
  carregando: boolean;
  login: (email: string, senha: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    async function carregarUsuario() {
      if (!getAccessToken()) {
        setCarregando(false);
        return;
      }
      try {
        setUsuario(await meRequest());
      } catch {
        clearTokens();
      } finally {
        setCarregando(false);
      }
    }
    void carregarUsuario();
  }, []);

  async function login(email: string, senha: string) {
    const tokens = await loginRequest(email, senha);
    setTokens(tokens.access_token, tokens.refresh_token);
    setUsuario(await meRequest());
  }

  function logout() {
    clearTokens();
    setUsuario(null);
  }

  return <AuthContext.Provider value={{ usuario, carregando, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth deve ser usado dentro de um AuthProvider");
  }
  return context;
}
