export type ModuloSistema = "clientes" | "processos" | "prazos" | "financeiro" | "tarefas" | "publicacoes";

export interface Permissao {
  id: string;
  modulo: ModuloSistema;
  pode_visualizar: boolean;
  pode_editar: boolean;
  pode_excluir: boolean;
}

export interface Usuario {
  id: string;
  nome: string;
  email: string;
  oab: string | null;
  super_admin: boolean;
  ativo: boolean;
  permissoes: Permissao[];
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
