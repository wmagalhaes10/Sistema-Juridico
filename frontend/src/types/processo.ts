export type FaseProcessual = "conhecimento" | "recursal" | "execucao";
export type StatusProcesso = "ativo" | "suspenso" | "arquivado" | "encerrado";
export type OrigemMovimentacao = "datajud" | "escavador" | "manual";

export interface ClienteResumo {
  id: string;
  nome_razao_social: string;
}

export interface Processo {
  id: string;
  numero_cnj: string;
  vara: string | null;
  tribunal: string | null;
  comarca: string | null;
  tipo_acao: string | null;
  fase_processual: FaseProcessual;
  polo_ativo: string | null;
  polo_passivo: string | null;
  status: StatusProcesso;
  data_distribuicao: string | null;
  valor_causa: string | null;
  cliente_id: string;
  advogado_responsavel_id: string | null;
  ultima_consulta_datajud: string | null;
  cliente?: ClienteResumo | null;
}

export interface ProcessoListResponse {
  items: Processo[];
  total: number;
  page: number;
  page_size: number;
}

export interface ProcessoCreateInput {
  numero_cnj: string;
  cliente_id: string;
  vara?: string;
  tribunal?: string;
  comarca?: string;
  tipo_acao?: string;
  fase_processual?: FaseProcessual;
  polo_ativo?: string;
  polo_passivo?: string;
  data_distribuicao?: string;
  valor_causa?: string;
}

export interface ProcessoUpdateInput {
  vara?: string;
  tribunal?: string;
  comarca?: string;
  tipo_acao?: string;
  fase_processual?: FaseProcessual;
  polo_ativo?: string;
  polo_passivo?: string;
  status?: StatusProcesso;
  data_distribuicao?: string;
  valor_causa?: string;
}

export interface Movimentacao {
  id: string;
  processo_id: string;
  data_movimentacao: string;
  descricao: string;
  origem: OrigemMovimentacao;
}

export interface MovimentacaoCreateInput {
  data_movimentacao: string;
  descricao: string;
}
