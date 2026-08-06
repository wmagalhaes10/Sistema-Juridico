export type TipoPrazo = "peremptorio" | "dilatorio" | "recursal";
export type StatusPrazo = "pendente" | "cumprido" | "perdido";

export interface ProcessoResumo {
  id: string;
  numero_cnj: string;
}

export interface Prazo {
  id: string;
  processo_id: string;
  data_prazo: string;
  tipo: TipoPrazo;
  status: StatusPrazo;
  descricao: string | null;
  responsavel_id: string | null;
  movimentacao_origem_id: string | null;
  processo?: ProcessoResumo | null;
}

export interface PrazoListResponse {
  items: Prazo[];
  total: number;
  page: number;
  page_size: number;
}

export interface DashboardPrazos {
  inicio: string;
  fim: string;
  total_pendentes: number;
  vencidos: number;
  prazos: Prazo[];
}

export interface PrazoCreateInput {
  data_prazo: string;
  tipo: TipoPrazo;
  descricao?: string;
  responsavel_id?: string;
}

export interface PrazoUpdateInput {
  data_prazo?: string;
  tipo?: TipoPrazo;
  status?: StatusPrazo;
  descricao?: string;
}
