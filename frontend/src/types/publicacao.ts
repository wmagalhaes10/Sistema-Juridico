export type StatusPublicacao = "nao_tratada" | "tratada" | "descartada";

export interface Publicacao {
  id: string;
  id_djen: number;
  data_disponibilizacao: string;
  sigla_tribunal: string | null;
  tipo_comunicacao: string | null;
  tipo_documento: string | null;
  nome_orgao: string | null;
  nome_classe: string | null;
  numero_processo: string | null;
  texto: string | null;
  link: string | null;
  meio: string | null;
  oab_numero: string | null;
  oab_uf: string | null;
  status: StatusPublicacao;
  processo_id: string | null;
  processo?: { id: string; numero_cnj: string } | null;
}

export interface PublicacaoListResponse {
  items: Publicacao[];
  total: number;
  page: number;
  page_size: number;
}

export interface PublicacoesResumo {
  nao_tratadas: number;
  tratadas: number;
  descartadas: number;
  nao_tratadas_hoje: number;
}
