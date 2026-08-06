import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import { ArrowLeft, Pencil, Plus, RefreshCw } from "lucide-react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { MovimentacaoFormDialog } from "@/components/processos/MovimentacaoFormDialog";
import { ProcessoFormDialog } from "@/components/processos/ProcessoFormDialog";
import { PrazoFormDialog } from "@/components/prazos/PrazoFormDialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatarData, formatarMoeda, formatarNumeroCnj } from "@/lib/format";
import { getSaldoProcesso } from "@/services/financeiroService";
import {
  createMovimentacao,
  getProcesso,
  listMovimentacoes,
  sincronizarDatajud,
  updateProcesso,
} from "@/services/processoService";
import { createPrazo, listPrazosDoProcesso, updatePrazo } from "@/services/prazoService";
import type { ProcessoUpdateInput } from "@/types/processo";
import type { PrazoCreateInput, StatusPrazo } from "@/types/prazo";

function extrairErro(erro: unknown): string {
  const axiosErro = erro as AxiosError<{ detail?: string }>;
  return axiosErro.response?.data?.detail ?? "Ocorreu um erro. Tente novamente.";
}

const STATUS_PRAZO_LABEL: Record<StatusPrazo, string> = {
  pendente: "Pendente",
  cumprido: "Cumprido",
  perdido: "Perdido",
};

export function ProcessoDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [dialogEditar, setDialogEditar] = useState(false);
  const [dialogMovimentacao, setDialogMovimentacao] = useState(false);
  const [dialogPrazo, setDialogPrazo] = useState(false);
  const [erroForm, setErroForm] = useState<string | null>(null);

  const { data: processo } = useQuery({
    queryKey: ["processo", id],
    queryFn: () => getProcesso(id as string),
    enabled: Boolean(id),
  });

  const { data: movimentacoes } = useQuery({
    queryKey: ["movimentacoes", id],
    queryFn: () => listMovimentacoes(id as string),
    enabled: Boolean(id),
  });

  const { data: prazos } = useQuery({
    queryKey: ["prazos-processo", id],
    queryFn: () => listPrazosDoProcesso(id as string),
    enabled: Boolean(id),
  });

  const { data: saldo } = useQuery({
    queryKey: ["saldo-processo", id],
    queryFn: () => getSaldoProcesso(id as string),
    enabled: Boolean(id),
  });

  const atualizarMutation = useMutation({
    mutationFn: ({ data }: { data: ProcessoUpdateInput }) => updateProcesso(id as string, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["processo", id] });
      setDialogEditar(false);
      setErroForm(null);
    },
    onError: (erro) => setErroForm(extrairErro(erro)),
  });

  const sincronizarMutation = useMutation({
    mutationFn: () => sincronizarDatajud(id as string),
    onSuccess: (novasMovimentacoes) => {
      queryClient.invalidateQueries({ queryKey: ["movimentacoes", id] });
      queryClient.invalidateQueries({ queryKey: ["prazos-processo", id] });
      queryClient.invalidateQueries({ queryKey: ["processo", id] });
      window.alert(`${novasMovimentacoes.length} nova(s) movimentação(ões) importada(s).`);
    },
    onError: (erro) => window.alert(extrairErro(erro)),
  });

  const movimentacaoMutation = useMutation({
    mutationFn: (data: { data_movimentacao: string; descricao: string }) =>
      createMovimentacao(id as string, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["movimentacoes", id] });
      setDialogMovimentacao(false);
    },
    onError: (erro) => window.alert(extrairErro(erro)),
  });

  const prazoMutation = useMutation({
    mutationFn: ({ data }: { processoId: string; data: PrazoCreateInput }) => createPrazo(id as string, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["prazos-processo", id] });
      setDialogPrazo(false);
    },
    onError: (erro) => window.alert(extrairErro(erro)),
  });

  const marcarStatusMutation = useMutation({
    mutationFn: ({ prazoId, status }: { prazoId: string; status: StatusPrazo }) =>
      updatePrazo(prazoId, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["prazos-processo", id] }),
    onError: (erro) => window.alert(extrairErro(erro)),
  });

  if (!processo) {
    return <p className="text-muted-foreground">Carregando...</p>;
  }

  return (
    <div className="space-y-6">
      <Button variant="ghost" size="sm" onClick={() => navigate("/processos")}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        Voltar
      </Button>

      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">{formatarNumeroCnj(processo.numero_cnj)}</h2>
          <p className="text-muted-foreground">
            {processo.cliente?.nome_razao_social} · {processo.tribunal} {processo.vara ? `· ${processo.vara}` : ""}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => sincronizarMutation.mutate()} disabled={sincronizarMutation.isPending}>
            <RefreshCw className="mr-2 h-4 w-4" />
            {sincronizarMutation.isPending ? "Sincronizando..." : "Sincronizar DataJud"}
          </Button>
          <Button
            variant="outline"
            onClick={() => {
              setErroForm(null);
              setDialogEditar(true);
            }}
          >
            <Pencil className="mr-2 h-4 w-4" />
            Editar
          </Button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Fase</CardTitle>
          </CardHeader>
          <CardContent className="capitalize">{processo.fase_processual}</CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Status</CardTitle>
          </CardHeader>
          <CardContent className="capitalize">{processo.status}</CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Receitas</CardTitle>
          </CardHeader>
          <CardContent>{saldo ? formatarMoeda(saldo.total_receitas) : "-"}</CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Saldo</CardTitle>
          </CardHeader>
          <CardContent>{saldo ? formatarMoeda(saldo.saldo) : "-"}</CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Prazos</CardTitle>
          <Button size="sm" onClick={() => setDialogPrazo(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Novo prazo
          </Button>
        </CardHeader>
        <CardContent className="space-y-2">
          {(prazos?.length ?? 0) === 0 && <p className="text-sm text-muted-foreground">Nenhum prazo cadastrado.</p>}
          {prazos?.map((prazo) => (
            <div key={prazo.id} className="flex items-center justify-between border-b py-2 last:border-0">
              <div>
                <p className="font-medium">
                  {formatarData(prazo.data_prazo)} · <span className="capitalize">{prazo.tipo}</span>
                </p>
                {prazo.descricao && <p className="text-sm text-muted-foreground">{prazo.descricao}</p>}
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={prazo.status === "cumprido" ? "success" : prazo.status === "perdido" ? "destructive" : "secondary"}>
                  {STATUS_PRAZO_LABEL[prazo.status]}
                </Badge>
                {prazo.status === "pendente" && (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => marcarStatusMutation.mutate({ prazoId: prazo.id, status: "cumprido" })}
                    >
                      Cumprido
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => marcarStatusMutation.mutate({ prazoId: prazo.id, status: "perdido" })}
                    >
                      Perdido
                    </Button>
                  </>
                )}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Movimentações</CardTitle>
          <Button size="sm" onClick={() => setDialogMovimentacao(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Nova movimentação
          </Button>
        </CardHeader>
        <CardContent className="space-y-2">
          {(movimentacoes?.length ?? 0) === 0 && (
            <p className="text-sm text-muted-foreground">Nenhuma movimentação registrada.</p>
          )}
          {movimentacoes?.map((mov) => (
            <div key={mov.id} className="border-b py-2 last:border-0">
              <div className="flex items-center justify-between">
                <p className="font-medium">{mov.descricao}</p>
                <Badge variant="outline" className="capitalize">
                  {mov.origem}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">{formatarData(mov.data_movimentacao)}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      <p className="text-sm text-muted-foreground">
        Para lançar despesas ou contratos de honorários vinculados a este processo, use a{" "}
        <Link to="/financeiro" className="underline">
          tela Financeiro
        </Link>
        .
      </p>

      <ProcessoFormDialog
        open={dialogEditar}
        onOpenChange={setDialogEditar}
        processo={processo}
        erro={erroForm}
        enviando={atualizarMutation.isPending}
        onSubmitCreate={async () => {}}
        onSubmitUpdate={async (_id, dataInput) => {
          await atualizarMutation.mutateAsync({ data: dataInput });
        }}
      />

      <MovimentacaoFormDialog
        open={dialogMovimentacao}
        onOpenChange={setDialogMovimentacao}
        enviando={movimentacaoMutation.isPending}
        onSubmit={async (dataInput) => {
          await movimentacaoMutation.mutateAsync(dataInput);
        }}
      />

      <PrazoFormDialog
        open={dialogPrazo}
        onOpenChange={setDialogPrazo}
        processoId={id}
        enviando={prazoMutation.isPending}
        onSubmit={async (processoId, dataInput) => {
          await prazoMutation.mutateAsync({ processoId, data: dataInput });
        }}
      />
    </div>
  );
}
