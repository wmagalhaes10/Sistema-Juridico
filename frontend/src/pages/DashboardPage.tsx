import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import { AlertTriangle, CalendarClock, CheckCircle2, Clock, ListTodo, Plus } from "lucide-react";

import { AgendaCalendario } from "@/components/dashboard/AgendaCalendario";
import { PrazoFormDialog } from "@/components/prazos/PrazoFormDialog";
import { TarefaFormDialog } from "@/components/tarefas/TarefaFormDialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatarData, formatarNumeroCnj } from "@/lib/format";
import { createPrazo, getDashboardPrazos } from "@/services/prazoService";
import { createTarefa, listTarefas, updateTarefa } from "@/services/tarefaService";
import type { Prazo, PrazoCreateInput, ProcessoResumo, StatusPrazo } from "@/types/prazo";
import type { TarefaCreateInput } from "@/types/tarefa";

const STATUS_LABEL: Record<StatusPrazo, string> = {
  pendente: "Pendente",
  cumprido: "Cumprido",
  perdido: "Perdido",
};

const TIPO_LABEL: Record<string, string> = {
  peremptorio: "Peremptório",
  dilatorio: "Dilatório",
  recursal: "Recursal",
};

function isVencido(prazo: Prazo): boolean {
  if (prazo.status !== "pendente") return false;
  const hoje = new Date().toISOString().slice(0, 10);
  return prazo.data_prazo < hoje;
}

function extrairErro(erro: unknown): string {
  const axiosErro = erro as AxiosError<{ detail?: string }>;
  return axiosErro.response?.data?.detail ?? "Ocorreu um erro. Tente novamente.";
}

export function DashboardPage() {
  const queryClient = useQueryClient();
  const [visao, setVisao] = useState<"semanal" | "mensal">("semanal");
  const [dialogPrazo, setDialogPrazo] = useState(false);
  const [dialogTarefa, setDialogTarefa] = useState(false);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["dashboard-prazos", visao],
    queryFn: () => getDashboardPrazos(visao),
  });

  const { data: tarefasPendentes } = useQuery({
    queryKey: ["tarefas", "pendente"],
    queryFn: () => listTarefas({ status: "pendente" }),
  });

  const prazoMutation = useMutation({
    mutationFn: ({ processoId, data: prazoData }: { processoId: string; data: PrazoCreateInput }) =>
      createPrazo(processoId, prazoData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard-prazos"] });
      setDialogPrazo(false);
    },
    onError: (erro) => window.alert(extrairErro(erro)),
  });

  const tarefaMutation = useMutation({
    mutationFn: createTarefa,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tarefas"] });
      setDialogTarefa(false);
    },
    onError: (erro) => window.alert(extrairErro(erro)),
  });

  const concluirTarefaMutation = useMutation({
    mutationFn: (tarefaId: string) => updateTarefa(tarefaId, { status: "concluida" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tarefas"] }),
    onError: (erro) => window.alert(extrairErro(erro)),
  });

  const processosUrgentes = Array.from(
    new Map<string, ProcessoResumo>(
      (data?.prazos ?? [])
        .filter((prazo) => isVencido(prazo) && prazo.processo)
        .map((prazo) => [prazo.processo_id, prazo.processo as ProcessoResumo]),
    ).values(),
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Dashboard</h2>
          <p className="text-muted-foreground">
            {data ? `${formatarData(data.inicio)} até ${formatarData(data.fim)}` : "Carregando período..."}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant={visao === "semanal" ? "default" : "outline"} onClick={() => setVisao("semanal")}>
            Semana
          </Button>
          <Button variant={visao === "mensal" ? "default" : "outline"} onClick={() => setVisao("mensal")}>
            Mês
          </Button>
          <div className="mx-1 h-6 w-px bg-border" />
          <Button variant="outline" onClick={() => setDialogPrazo(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Novo prazo
          </Button>
          <Button onClick={() => setDialogTarefa(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Nova tarefa
          </Button>
        </div>
      </div>

      {isError && <p className="text-sm text-destructive">Não foi possível carregar o dashboard.</p>}

      <div className="grid gap-4 sm:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Prazos no período</CardTitle>
            <CalendarClock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data?.total_pendentes ?? "-"}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Vencidos</CardTitle>
            <AlertTriangle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{data?.vencidos ?? "-"}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Processos urgentes</CardTitle>
            <Clock className="h-4 w-4 text-amber-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{processosUrgentes.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Tarefas pendentes</CardTitle>
            <ListTodo className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tarefasPendentes?.length ?? "-"}</div>
          </CardContent>
        </Card>
      </div>

      <AgendaCalendario />

      <Card>
        <CardHeader>
          <CardTitle>Prazos do período</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-sm text-muted-foreground">Carregando...</p>}
          {!isLoading && (data?.prazos.length ?? 0) === 0 && (
            <p className="text-sm text-muted-foreground">Nenhum prazo neste período.</p>
          )}
          <div className="divide-y">
            {data?.prazos.map((prazo) => (
              <div key={prazo.id} className="flex items-center justify-between py-3">
                <div>
                  <p className="font-medium">
                    {prazo.processo ? formatarNumeroCnj(prazo.processo.numero_cnj) : "Processo"}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {TIPO_LABEL[prazo.tipo] ?? prazo.tipo} · {formatarData(prazo.data_prazo)}
                  </p>
                  {prazo.descricao && <p className="text-sm text-muted-foreground">{prazo.descricao}</p>}
                </div>
                <Badge variant={isVencido(prazo) ? "destructive" : prazo.status === "cumprido" ? "success" : "secondary"}>
                  {isVencido(prazo) ? "Vencido" : STATUS_LABEL[prazo.status]}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Tarefas pendentes</CardTitle>
        </CardHeader>
        <CardContent>
          {(tarefasPendentes?.length ?? 0) === 0 && (
            <p className="text-sm text-muted-foreground">Nenhuma tarefa pendente.</p>
          )}
          <div className="divide-y">
            {tarefasPendentes?.map((tarefa) => (
              <div key={tarefa.id} className="flex items-center justify-between py-3">
                <div>
                  <p className="font-medium">{tarefa.titulo}</p>
                  <p className="text-sm text-muted-foreground">
                    {tarefa.responsavel ? tarefa.responsavel.nome : "Sem responsável"}
                    {tarefa.data_vencimento ? ` · ${formatarData(tarefa.data_vencimento)}` : ""}
                    {tarefa.processo ? ` · ${formatarNumeroCnj(tarefa.processo.numero_cnj)}` : ""}
                  </p>
                  {tarefa.descricao && <p className="text-sm text-muted-foreground">{tarefa.descricao}</p>}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => concluirTarefaMutation.mutate(tarefa.id)}
                  disabled={concluirTarefaMutation.isPending}
                >
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  Concluir
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {processosUrgentes.length > 0 && (
        <Card className="border-destructive/50">
          <CardHeader>
            <CardTitle className="text-destructive">Processos urgentes (prazo vencido)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {processosUrgentes.map((processo) => (
              <p key={processo.id} className="font-medium">
                {formatarNumeroCnj(processo.numero_cnj)}
              </p>
            ))}
          </CardContent>
        </Card>
      )}

      <PrazoFormDialog
        open={dialogPrazo}
        onOpenChange={setDialogPrazo}
        enviando={prazoMutation.isPending}
        onSubmit={async (processoId, dataInput) => {
          await prazoMutation.mutateAsync({ processoId, data: dataInput });
        }}
      />

      <TarefaFormDialog
        open={dialogTarefa}
        onOpenChange={setDialogTarefa}
        enviando={tarefaMutation.isPending}
        onSubmit={async (dataInput: TarefaCreateInput) => {
          await tarefaMutation.mutateAsync(dataInput);
        }}
      />
    </div>
  );
}
