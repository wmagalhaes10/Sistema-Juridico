import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import { Plus } from "lucide-react";

import { ContratoFormDialog } from "@/components/financeiro/ContratoFormDialog";
import { DespesaFormDialog } from "@/components/financeiro/DespesaFormDialog";
import { ParcelasDialog } from "@/components/financeiro/ParcelasDialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatarData, formatarMoeda } from "@/lib/format";
import {
  createContrato,
  createDespesa,
  getRelatorioDespesas,
  getRelatorioReceitas,
  listContratos,
  listDespesas,
} from "@/services/financeiroService";
import type { ContratoCreateInput, ContratoHonorario, DespesaCreateInput } from "@/types/financeiro";

function extrairErro(erro: unknown): string {
  const axiosErro = erro as AxiosError<{ detail?: string }>;
  return axiosErro.response?.data?.detail ?? "Ocorreu um erro. Tente novamente.";
}

export function FinanceiroPage() {
  const queryClient = useQueryClient();
  const [dialogContrato, setDialogContrato] = useState(false);
  const [dialogDespesa, setDialogDespesa] = useState(false);
  const [contratoSelecionado, setContratoSelecionado] = useState<ContratoHonorario | null>(null);
  const [erroContrato, setErroContrato] = useState<string | null>(null);
  const [dataInicio, setDataInicio] = useState("");
  const [dataFim, setDataFim] = useState("");

  const { data: contratos } = useQuery({ queryKey: ["contratos"], queryFn: () => listContratos() });
  const { data: despesas } = useQuery({ queryKey: ["despesas"], queryFn: () => listDespesas() });

  const { data: relatorioReceitas } = useQuery({
    queryKey: ["relatorio-receitas", dataInicio, dataFim],
    queryFn: () => getRelatorioReceitas({ dataInicio: dataInicio || undefined, dataFim: dataFim || undefined }),
  });

  const { data: relatorioDespesas } = useQuery({
    queryKey: ["relatorio-despesas", dataInicio, dataFim],
    queryFn: () => getRelatorioDespesas({ dataInicio: dataInicio || undefined, dataFim: dataFim || undefined }),
  });

  const criarContratoMutation = useMutation({
    mutationFn: createContrato,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["contratos"] });
      setDialogContrato(false);
      setErroContrato(null);
    },
    onError: (erro) => setErroContrato(extrairErro(erro)),
  });

  const criarDespesaMutation = useMutation({
    mutationFn: ({ processoId, data }: { processoId: string; data: DespesaCreateInput }) =>
      createDespesa(processoId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["despesas"] });
      setDialogDespesa(false);
    },
    onError: (erro) => window.alert(extrairErro(erro)),
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold tracking-tight">Financeiro</h2>

      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">Receitas no período</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {relatorioReceitas ? formatarMoeda(relatorioReceitas.total) : "-"}
            </div>
            <p className="text-sm text-muted-foreground">
              {relatorioReceitas?.quantidade_parcelas ?? 0} parcela(s) paga(s)
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">Despesas no período</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {relatorioDespesas ? formatarMoeda(relatorioDespesas.total) : "-"}
            </div>
            <p className="text-sm text-muted-foreground">{relatorioDespesas?.quantidade ?? 0} despesa(s)</p>
          </CardContent>
        </Card>
      </div>

      <div className="flex gap-3">
        <div className="space-y-1">
          <Label>De</Label>
          <Input type="date" value={dataInicio} onChange={(e) => setDataInicio(e.target.value)} />
        </div>
        <div className="space-y-1">
          <Label>Até</Label>
          <Input type="date" value={dataFim} onChange={(e) => setDataFim(e.target.value)} />
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Contratos de honorários</CardTitle>
          <Button size="sm" onClick={() => setDialogContrato(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Novo contrato
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Tipo</TableHead>
                <TableHead>Valor</TableHead>
                <TableHead>Parcelas</TableHead>
                <TableHead>Assinatura</TableHead>
                <TableHead className="w-32">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(contratos?.length ?? 0) === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-muted-foreground">
                    Nenhum contrato cadastrado.
                  </TableCell>
                </TableRow>
              )}
              {contratos?.map((contrato) => (
                <TableRow key={contrato.id}>
                  <TableCell className="capitalize">{contrato.tipo}</TableCell>
                  <TableCell>{formatarMoeda(contrato.valor_contratado)}</TableCell>
                  <TableCell>{contrato.numero_parcelas}</TableCell>
                  <TableCell>{contrato.data_assinatura ? formatarData(contrato.data_assinatura) : "-"}</TableCell>
                  <TableCell>
                    <Button variant="outline" size="sm" onClick={() => setContratoSelecionado(contrato)}>
                      Ver parcelas
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Despesas processuais</CardTitle>
          <Button size="sm" onClick={() => setDialogDespesa(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Nova despesa
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Tipo</TableHead>
                <TableHead>Descrição</TableHead>
                <TableHead>Valor</TableHead>
                <TableHead>Data</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(despesas?.length ?? 0) === 0 && (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-muted-foreground">
                    Nenhuma despesa cadastrada.
                  </TableCell>
                </TableRow>
              )}
              {despesas?.map((despesa) => (
                <TableRow key={despesa.id}>
                  <TableCell className="capitalize">{despesa.tipo}</TableCell>
                  <TableCell>{despesa.descricao || "-"}</TableCell>
                  <TableCell>{formatarMoeda(despesa.valor)}</TableCell>
                  <TableCell>{formatarData(despesa.data_despesa)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <ContratoFormDialog
        open={dialogContrato}
        onOpenChange={setDialogContrato}
        erro={erroContrato}
        enviando={criarContratoMutation.isPending}
        onSubmit={async (dataInput: ContratoCreateInput) => {
          await criarContratoMutation.mutateAsync(dataInput);
        }}
      />

      <DespesaFormDialog
        open={dialogDespesa}
        onOpenChange={setDialogDespesa}
        enviando={criarDespesaMutation.isPending}
        onSubmit={async (processoId, dataInput) => {
          await criarDespesaMutation.mutateAsync({ processoId, data: dataInput });
        }}
      />

      <ParcelasDialog contrato={contratoSelecionado} onOpenChange={() => setContratoSelecionado(null)} />
    </div>
  );
}
