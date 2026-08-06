import { api } from "@/lib/api";
import type { StatusTarefa, Tarefa, TarefaCreateInput, TarefaUpdateInput } from "@/types/tarefa";

interface ListParams {
  responsavelId?: string;
  status?: StatusTarefa;
  processoId?: string;
}

export async function listTarefas(params: ListParams = {}): Promise<Tarefa[]> {
  const response = await api.get<Tarefa[]>("/tarefas", {
    params: {
      responsavel_id: params.responsavelId,
      status_tarefa: params.status,
      processo_id: params.processoId,
    },
  });
  return response.data;
}

export async function createTarefa(data: TarefaCreateInput): Promise<Tarefa> {
  const response = await api.post<Tarefa>("/tarefas", data);
  return response.data;
}

export async function updateTarefa(id: string, data: TarefaUpdateInput): Promise<Tarefa> {
  const response = await api.patch<Tarefa>(`/tarefas/${id}`, data);
  return response.data;
}

export async function deleteTarefa(id: string): Promise<void> {
  await api.delete(`/tarefas/${id}`);
}
