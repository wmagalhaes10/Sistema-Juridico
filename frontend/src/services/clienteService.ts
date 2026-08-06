import { api } from "@/lib/api";
import type { Cliente, ClienteCreateInput, ClienteListResponse, ClienteUpdateInput } from "@/types/cliente";

interface ListParams {
  page?: number;
  pageSize?: number;
  busca?: string;
}

export async function listClientes({ page = 1, pageSize = 20, busca }: ListParams): Promise<ClienteListResponse> {
  const response = await api.get<ClienteListResponse>("/clientes", {
    params: { page, page_size: pageSize, busca: busca || undefined },
  });
  return response.data;
}

export async function createCliente(data: ClienteCreateInput): Promise<Cliente> {
  const response = await api.post<Cliente>("/clientes", data);
  return response.data;
}

export async function updateCliente(id: string, data: ClienteUpdateInput): Promise<Cliente> {
  const response = await api.put<Cliente>(`/clientes/${id}`, data);
  return response.data;
}

export async function deleteCliente(id: string): Promise<void> {
  await api.delete(`/clientes/${id}`);
}
