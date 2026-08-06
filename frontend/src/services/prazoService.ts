import { api } from "@/lib/api";
import type { DashboardPrazos, Prazo, PrazoCreateInput, PrazoListResponse, PrazoUpdateInput } from "@/types/prazo";

export async function getDashboardPrazos(visao: "semanal" | "mensal"): Promise<DashboardPrazos> {
  const response = await api.get<DashboardPrazos>("/prazos/dashboard", { params: { visao } });
  return response.data;
}

export async function listPrazos(
  params: { dataInicio?: string; dataFim?: string; pageSize?: number } = {},
): Promise<PrazoListResponse> {
  const response = await api.get<PrazoListResponse>("/prazos", {
    params: { data_inicio: params.dataInicio, data_fim: params.dataFim, page_size: params.pageSize ?? 200 },
  });
  return response.data;
}

export async function listPrazosDoProcesso(processoId: string): Promise<Prazo[]> {
  const response = await api.get<Prazo[]>(`/processos/${processoId}/prazos`);
  return response.data;
}

export async function createPrazo(processoId: string, data: PrazoCreateInput): Promise<Prazo> {
  const response = await api.post<Prazo>(`/processos/${processoId}/prazos`, data);
  return response.data;
}

export async function updatePrazo(prazoId: string, data: PrazoUpdateInput): Promise<Prazo> {
  const response = await api.patch<Prazo>(`/prazos/${prazoId}`, data);
  return response.data;
}

export async function deletePrazo(prazoId: string): Promise<void> {
  await api.delete(`/prazos/${prazoId}`);
}
