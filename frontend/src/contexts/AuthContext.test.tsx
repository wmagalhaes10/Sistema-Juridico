import { act, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { login as loginMock, me as meMock } from "@/services/authService";

vi.mock("@/services/authService", () => ({
  login: vi.fn(),
  me: vi.fn(),
}));

function TestConsumer() {
  const { usuario, carregando, login, logout } = useAuth();
  if (carregando) return <div>carregando</div>;
  return (
    <div>
      <span data-testid="usuario">{usuario ? usuario.nome : "sem-usuario"}</span>
      <button onClick={() => login("a@a.com", "123")}>entrar</button>
      <button onClick={logout}>sair</button>
    </div>
  );
}

describe("AuthContext", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it("inicia sem usuário quando não há token salvo", async () => {
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => expect(screen.getByTestId("usuario")).toHaveTextContent("sem-usuario"));
    expect(meMock).not.toHaveBeenCalled();
  });

  it("faz login e popula o usuário, persistindo os tokens", async () => {
    vi.mocked(loginMock).mockResolvedValue({
      access_token: "token-acesso",
      refresh_token: "token-refresh",
      token_type: "bearer",
    });
    vi.mocked(meMock).mockResolvedValue({
      id: "1",
      nome: "Wagner",
      email: "wagner@example.com",
      oab: null,
      super_admin: true,
      permissoes: [],
      ativo: true,
    });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => expect(screen.getByTestId("usuario")).toHaveTextContent("sem-usuario"));

    await act(async () => {
      screen.getByText("entrar").click();
    });

    await waitFor(() => expect(screen.getByTestId("usuario")).toHaveTextContent("Wagner"));
    expect(localStorage.getItem("sj_access_token")).toBe("token-acesso");
    expect(localStorage.getItem("sj_refresh_token")).toBe("token-refresh");
  });

  it("restaura a sessão automaticamente quando já existe token salvo", async () => {
    localStorage.setItem("sj_access_token", "token-existente");
    localStorage.setItem("sj_refresh_token", "refresh-existente");
    vi.mocked(meMock).mockResolvedValue({
      id: "1",
      nome: "Advogada Ana",
      email: "ana@example.com",
      oab: "123456",
      super_admin: false,
      permissoes: [],
      ativo: true,
    });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => expect(screen.getByTestId("usuario")).toHaveTextContent("Advogada Ana"));
  });

  it("limpa o token salvo se a sessão restaurada for inválida", async () => {
    localStorage.setItem("sj_access_token", "token-expirado");
    vi.mocked(meMock).mockRejectedValue(new Error("401"));

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => expect(screen.getByTestId("usuario")).toHaveTextContent("sem-usuario"));
    expect(localStorage.getItem("sj_access_token")).toBeNull();
  });

  it("logout limpa o usuário e os tokens", async () => {
    localStorage.setItem("sj_access_token", "token-acesso");
    localStorage.setItem("sj_refresh_token", "token-refresh");
    vi.mocked(meMock).mockResolvedValue({
      id: "1",
      nome: "Wagner",
      email: "wagner@example.com",
      oab: null,
      super_admin: true,
      permissoes: [],
      ativo: true,
    });

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );

    await waitFor(() => expect(screen.getByTestId("usuario")).toHaveTextContent("Wagner"));

    await act(async () => {
      screen.getByText("sair").click();
    });

    expect(screen.getByTestId("usuario")).toHaveTextContent("sem-usuario");
    expect(localStorage.getItem("sj_access_token")).toBeNull();
    expect(localStorage.getItem("sj_refresh_token")).toBeNull();
  });
});
