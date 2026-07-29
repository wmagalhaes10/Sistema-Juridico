export type TipoPessoa = "fisica" | "juridica";

export interface Cliente {
  id: string;
  tipo_pessoa: TipoPessoa;
  cpf_cnpj: string;
  nome_razao_social: string;
  endereco: string | null;
  telefone: string | null;
  email: string | null;
  oab_responsavel: string | null;
}

export interface ClienteListResponse {
  items: Cliente[];
  total: number;
  page: number;
  page_size: number;
}

export interface ClienteCreateInput {
  tipo_pessoa: TipoPessoa;
  cpf_cnpj: string;
  nome_razao_social: string;
  endereco?: string;
  telefone?: string;
  email?: string;
  oab_responsavel?: string;
}

export interface ClienteUpdateInput {
  nome_razao_social?: string;
  endereco?: string;
  telefone?: string;
  email?: string;
  oab_responsavel?: string;
}
