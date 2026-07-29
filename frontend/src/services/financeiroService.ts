import { api } from "@/lib/api";
import type {
  ContratoCreateInput,
  ContratoHonorario,
  Despesa,
  DespesaCreateInput,
  Parcela,
  RelatorioDespesas,
  RelatorioReceitas,
  SaldoProcesso,
} from "@/types/financeiro";

export async function listContratos(
  params: { clienteId?: string; processoId?: string } = {},
): Promise<ContratoHonorario[]> {
  const response = await api.get<ContratoHonorario[]>("/contratos-honorarios", {
    params: { cliente_id: params.clienteId, processo_id: params.processoId },
  });
  return response.data;
}

export async function createContrato(data: ContratoCreateInput): Promise<ContratoHonorario> {
  const response = await api.post<ContratoHonorario>("/contratos-honorarios", data);
  return response.data;
}

export async function registrarPagamento(parcelaId: string): Promise<Parcela> {
  const response = await api.post<Parcela>(`/parcelas/${parcelaId}/pagamento`);
  return response.data;
}

export async function baixarRecibo(parcelaId: string, numeroParcela: number): Promise<void> {
  const response = await api.get(`/parcelas/${parcelaId}/recibo`, { responseType: "blob" });
  const url = window.URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = `recibo_parcela_${numeroParcela}.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export async function listDespesas(params: { processoId?: string } = {}): Promise<Despesa[]> {
  const response = await api.get<Despesa[]>("/despesas", { params: { processo_id: params.processoId } });
  return response.data;
}

export async function createDespesa(processoId: string, data: DespesaCreateInput): Promise<Despesa> {
  const response = await api.post<Despesa>(`/processos/${processoId}/despesas`, data);
  return response.data;
}

export async function getSaldoProcesso(processoId: string): Promise<SaldoProcesso> {
  const response = await api.get<SaldoProcesso>(`/processos/${processoId}/saldo`);
  return response.data;
}

export async function getRelatorioReceitas(
  params: { clienteId?: string; processoId?: string; dataInicio?: string; dataFim?: string } = {},
): Promise<RelatorioReceitas> {
  const response = await api.get<RelatorioReceitas>("/relatorios/receitas", {
    params: {
      cliente_id: params.clienteId,
      processo_id: params.processoId,
      data_inicio: params.dataInicio,
      data_fim: params.dataFim,
    },
  });
  return response.data;
}

export async function getRelatorioDespesas(
  params: { processoId?: string; dataInicio?: string; dataFim?: string } = {},
): Promise<RelatorioDespesas> {
  const response = await api.get<RelatorioDespesas>("/relatorios/despesas", {
    params: { processo_id: params.processoId, data_inicio: params.dataInicio, data_fim: params.dataFim },
  });
  return response.data;
}
