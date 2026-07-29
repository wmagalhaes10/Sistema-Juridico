import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "@/components/layout/AppLayout";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AuthProvider } from "@/contexts/AuthContext";
import { ClientesPage } from "@/pages/ClientesPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { FinanceiroPage } from "@/pages/FinanceiroPage";
import { LoginPage } from "@/pages/LoginPage";
import { ProcessoDetailPage } from "@/pages/ProcessoDetailPage";
import { ProcessosPage } from "@/pages/ProcessosPage";
import { PublicacoesPage } from "@/pages/PublicacoesPage";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<DashboardPage />} />
            <Route path="/clientes" element={<ClientesPage />} />
            <Route path="/processos" element={<ProcessosPage />} />
            <Route path="/processos/:id" element={<ProcessoDetailPage />} />
            <Route path="/publicacoes" element={<PublicacoesPage />} />
            <Route path="/financeiro" element={<FinanceiroPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
