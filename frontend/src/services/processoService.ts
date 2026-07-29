import { api } from "@/lib/api";
import type {
  Movimentacao,
  MovimentacaoCreateInput,
  Processo,
  ProcessoCreateInput,
  ProcessoListResponse,
  ProcessoUpdateInput,
} from "@/types/processo";

interface ListParams {
  page?: number;
  pageSize?: number;
  busca?: string;
  statusProcesso?: string;
  fase?: string;
}

export async function listProcessos({
  page = 1,
  pageSize = 20,
  busca,
  statusProcesso,
  fase,
}: ListParams): Promise<ProcessoListResponse> {
  const response = await api.get<ProcessoListResponse>("/processos", {
    params: {
      page,
      page_size: pageSize,
      busca: busca || undefined,
      status_processo: statusProcesso || undefined,
      fase: fase || undefined,
    },
  });
  return response.data;
}

export async function getProcesso(id: string): Promise<Processo> {
  const response = await api.get<Processo>(`/processos/${id}`);
  return response.data;
}

export async function createProcesso(data: ProcessoCreateInput): Promise<Processo> {
  const response = await api.post<Processo>("/processos", data);
  return response.data;
}

export async function updateProcesso(id: string, data: ProcessoUpdateInput): Promise<Processo> {
  const response = await api.put<Processo>(`/processos/${id}`, data);
  return response.data;
}

export async function deleteProcesso(id: string): Promise<void> {
  await api.delete(`/processos/${id}`);
}

export async function listMovimentacoes(processoId: string): Promise<Movimentacao[]> {
  const response = await api.get<Movimentacao[]>(`/processos/${processoId}/movimentacoes`);
  return response.data;
}

export async function createMovimentacao(
  processoId: string,
  data: MovimentacaoCreateInput,
): Promise<Movimentacao> {
  const response = await api.post<Movimentacao>(`/processos/${processoId}/movimentacoes`, data);
  return response.data;
}

export async function sincronizarDatajud(processoId: string): Promise<Movimentacao[]> {
  const response = await api.post<Movimentacao[]>(`/processos/${processoId}/sincronizar-datajud`);
  return response.data;
}
