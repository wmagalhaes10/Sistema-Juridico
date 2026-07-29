import { api } from "@/lib/api";
import type { Publicacao, PublicacaoListResponse, PublicacoesResumo, StatusPublicacao } from "@/types/publicacao";

export async function listPublicacoes(
  params: { page?: number; pageSize?: number; status?: StatusPublicacao } = {},
): Promise<PublicacaoListResponse> {
  const response = await api.get<PublicacaoListResponse>("/publicacoes", {
    params: {
      page: params.page ?? 1,
      page_size: params.pageSize ?? 20,
      status_publicacao: params.status,
    },
  });
  return response.data;
}

export async function getResumoPublicacoes(): Promise<PublicacoesResumo> {
  const response = await api.get<PublicacoesResumo>("/publicacoes/resumo");
  return response.data;
}

export async function sincronizarPublicacoes(): Promise<Publicacao[]> {
  const response = await api.post<Publicacao[]>("/publicacoes/sincronizar");
  return response.data;
}

export async function atualizarStatusPublicacao(
  publicacaoId: string,
  status: StatusPublicacao,
): Promise<Publicacao> {
  const response = await api.patch<Publicacao>(`/publicacoes/${publicacaoId}`, { status });
  return response.data;
}
