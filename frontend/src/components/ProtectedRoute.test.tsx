import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AuthProvider } from "@/contexts/AuthContext";
import { me as meMock } from "@/services/authService";

vi.mock("@/services/authService", () => ({
  login: vi.fn(),
  me: vi.fn(),
}));

function renderComRota(caminhoInicial: string) {
  return render(
    <MemoryRouter initialEntries={[caminhoInicial]}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<div>tela de login</div>} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <div>conteúdo protegido</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe("ProtectedRoute", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it("redireciona para /login quando não há usuário autenticado", async () => {
    renderComRota("/");

    await waitFor(() => expect(screen.getByText("tela de login")).toBeInTheDocument());
    expect(screen.queryByText("conteúdo protegido")).not.toBeInTheDocument();
  });

  it("renderiza o conteúdo protegido quando o usuário está autenticado", async () => {
    localStorage.setItem("sj_access_token", "token-valido");
    vi.mocked(meMock).mockResolvedValue({
      id: "1",
      nome: "Wagner",
      email: "wagner@example.com",
      oab: null,
      super_admin: true,
      permissoes: [],
      ativo: true,
    });

    renderComRota("/");

    await waitFor(() => expect(screen.getByText("conteúdo protegido")).toBeInTheDocument());
  });
});
