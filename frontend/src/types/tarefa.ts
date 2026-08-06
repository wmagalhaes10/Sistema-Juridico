export type StatusTarefa = "pendente" | "concluida";

export interface UsuarioResumo {
  id: string;
  nome: string;
}

export interface ProcessoResumoTarefa {
  id: string;
  numero_cnj: string;
}

export interface Tarefa {
  id: string;
  titulo: string;
  descricao: string | null;
  data_vencimento: string | null;
  status: StatusTarefa;
  processo_id: string | null;
  responsavel_id: string | null;
  criado_por_id: string;
  responsavel?: UsuarioResumo | null;
  processo?: ProcessoResumoTarefa | null;
}

export interface TarefaCreateInput {
  titulo: string;
  descricao?: string;
  data_vencimento?: string;
  responsavel_id?: string;
  processo_id?: string;
}

export interface TarefaUpdateInput {
  titulo?: string;
  descricao?: string;
  data_vencimento?: string;
  responsavel_id?: string;
  status?: StatusTarefa;
}
