import { useQuery } from "@tanstack/react-query";
import { FileText, LayoutDashboard, LogOut, Scale, Users, Wallet } from "lucide-react";
import { NavLink } from "react-router-dom";

import { useAuth } from "@/contexts/AuthContext";
import { cn } from "@/lib/utils";
import { getResumoPublicacoes } from "@/services/publicacaoService";

const ITENS_NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/clientes", label: "Clientes", icon: Users, end: false },
  { to: "/processos", label: "Processos", icon: Scale, end: false },
  { to: "/publicacoes", label: "Publicações", icon: FileText, end: false },
  { to: "/financeiro", label: "Financeiro", icon: Wallet, end: false },
];

export function Sidebar() {
  const { usuario, logout } = useAuth();

  const { data: resumoPublicacoes } = useQuery({
    queryKey: ["publicacoes-resumo"],
    queryFn: getResumoPublicacoes,
    refetchInterval: 5 * 60 * 1000,
    retry: false,
  });

  const naoTratadas = resumoPublicacoes?.nao_tratadas ?? 0;

  return (
    <aside className="flex h-screen w-64 flex-col border-r bg-card">
      <div className="border-b px-6 py-4">
        <h1 className="text-lg font-semibold">Sistema Jurídico</h1>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {ITENS_NAV.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              )
            }
          >
            <Icon className="h-4 w-4" />
            <span className="flex-1">{label}</span>
            {to === "/publicacoes" && naoTratadas > 0 && (
              <span className="rounded-full bg-destructive px-2 py-0.5 text-xs font-semibold text-destructive-foreground">
                {naoTratadas > 99 ? "99+" : naoTratadas}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="border-t px-3 py-4">
        <div className="mb-2 px-3 text-sm">
          <p className="font-medium">{usuario?.nome}</p>
          <p className="text-xs text-muted-foreground">
            {usuario?.super_admin ? "Administrador" : "Funcionário"}
          </p>
        </div>
        <button
          type="button"
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
        >
          <LogOut className="h-4 w-4" />
          Sair
        </button>
      </div>
    </aside>
  );
}
