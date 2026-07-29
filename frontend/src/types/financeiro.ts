export type TipoContrato = "fixo" | "exito" | "misto";
export type StatusParcela = "pago" | "pendente" | "atrasado";
export type TipoDespesa = "custas" | "diligencia" | "pericia" | "outros";

export interface Parcela {
  id: string;
  contrato_id: string;
  numero_parcela: number;
  valor: string;
  data_vencimento: string;
  data_pagamento: string | null;
  status: StatusParcela;
}

export interface ContratoHonorario {
  id: string;
  cliente_id: string;
  processo_id: string | null;
  tipo: TipoContrato;
  valor_contratado: string;
  numero_parcelas: number;
  data_assinatura: string | null;
  observacoes: string | null;
  parcelas: Parcela[];
}

export interface ContratoCreateInput {
  cliente_id: string;
  processo_id?: string;
  tipo: TipoContrato;
  valor_contratado: string;
  numero_parcelas: number;
  data_assinatura?: string;
  observacoes?: string;
}

export interface Despesa {
  id: string;
  processo_id: string;
  tipo: TipoDespesa;
  descricao: string | null;
  valor: string;
  data_despesa: string;
}

export interface DespesaCreateInput {
  tipo: TipoDespesa;
  descricao?: string;
  valor: string;
  data_despesa: string;
}

export interface SaldoProcesso {
  processo_id: string;
  total_receitas: string;
  total_despesas: string;
  saldo: string;
}

export interface RelatorioReceitas {
  total: string;
  quantidade_parcelas: number;
}

export interface RelatorioDespesas {
  total: string;
  quantidade: number;
}
