import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatarData, formatarNumeroCnj } from "@/lib/format";
import { cn } from "@/lib/utils";
import { listPrazos } from "@/services/prazoService";
import { listTarefas } from "@/services/tarefaService";
import type { Prazo } from "@/types/prazo";
import type { Tarefa } from "@/types/tarefa";

const DIAS_SEMANA = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];

function paraChaveISO(data: Date): string {
  const ano = data.getFullYear();
  const mes = String(data.getMonth() + 1).padStart(2, "0");
  const dia = String(data.getDate()).padStart(2, "0");
  return `${ano}-${mes}-${dia}`;
}

function gerarDiasDoMes(referencia: Date): Date[] {
  const ano = referencia.getFullYear();
  const mes = referencia.getMonth();
  const primeiroDia = new Date(ano, mes, 1);
  const ultimoDia = new Date(ano, mes + 1, 0);

  const inicio = new Date(primeiroDia);
  inicio.setDate(inicio.getDate() - inicio.getDay());
  const fim = new Date(ultimoDia);
  fim.setDate(fim.getDate() + (6 - fim.getDay()));

  const dias: Date[] = [];
  const cursor = new Date(inicio);
  while (cursor <= fim) {
    dias.push(new Date(cursor));
    cursor.setDate(cursor.getDate() + 1);
  }
  return dias;
}

export function AgendaCalendario() {
  const hoje = new Date();
  const [referencia, setReferencia] = useState(() => new Date(hoje.getFullYear(), hoje.getMonth(), 1));
  const [diaSelecionado, setDiaSelecionado] = useState(() => paraChaveISO(hoje));

  const dias = useMemo(() => gerarDiasDoMes(referencia), [referencia]);
  const inicioMes = paraChaveISO(dias[0]);
  const fimMes = paraChaveISO(dias[dias.length - 1]);

  const { data: prazosResp } = useQuery({
    queryKey: ["agenda-prazos", inicioMes, fimMes],
    queryFn: () => listPrazos({ dataInicio: inicioMes, dataFim: fimMes, pageSize: 200 }),
  });

  const { data: tarefas } = useQuery({
    queryKey: ["agenda-tarefas"],
    queryFn: () => listTarefas(),
  });

  const itensPorDia = useMemo(() => {
    const mapa = new Map<string, { prazos: Prazo[]; tarefas: Tarefa[] }>();

    for (const prazo of prazosResp?.items ?? []) {
      const chave = prazo.data_prazo.slice(0, 10);
      if (!mapa.has(chave)) mapa.set(chave, { prazos: [], tarefas: [] });
      mapa.get(chave)?.prazos.push(prazo);
    }

    for (const tarefa of tarefas ?? []) {
      if (!tarefa.data_vencimento) continue;
      const chave = tarefa.data_vencimento.slice(0, 10);
      if (chave < inicioMes || chave > fimMes) continue;
      if (!mapa.has(chave)) mapa.set(chave, { prazos: [], tarefas: [] });
      mapa.get(chave)?.tarefas.push(tarefa);
    }

    return mapa;
  }, [prazosResp, tarefas, inicioMes, fimMes]);

  const itensDoDiaSelecionado = itensPorDia.get(diaSelecionado);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="capitalize">
          {referencia.toLocaleDateString("pt-BR", { month: "long", year: "numeric" })}
        </CardTitle>
        <div className="flex items-center gap-1">
          <Button
            variant="outline"
            size="icon"
            onClick={() => setReferencia((r) => new Date(r.getFullYear(), r.getMonth() - 1, 1))}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setReferencia(new Date(hoje.getFullYear(), hoje.getMonth(), 1));
              setDiaSelecionado(paraChaveISO(hoje));
            }}
          >
            Hoje
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={() => setReferencia((r) => new Date(r.getFullYear(), r.getMonth() + 1, 1))}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-7 gap-1 text-center text-xs font-medium text-muted-foreground">
          {DIAS_SEMANA.map((dia) => (
            <div key={dia} className="py-1">
              {dia}
            </div>
          ))}
        </div>
        <div className="grid grid-cols-7 gap-1">
          {dias.map((dia) => {
            const chave = paraChaveISO(dia);
            const itens = itensPorDia.get(chave);
            const noMesAtual = dia.getMonth() === referencia.getMonth();
            const ehHoje = chave === paraChaveISO(hoje);
            const selecionado = chave === diaSelecionado;

            return (
              <button
                key={chave}
                type="button"
                onClick={() => setDiaSelecionado(chave)}
                className={cn(
                  "flex min-h-16 flex-col items-start rounded-md border p-1 text-left text-xs transition-colors hover:bg-accent",
                  !noMesAtual && "opacity-40",
                  ehHoje && "border-primary",
                  selecionado && "bg-accent",
                )}
              >
                <span className={cn("font-medium", ehHoje && "text-primary")}>{dia.getDate()}</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {itens && itens.prazos.length > 0 && (
                    <span className="rounded bg-destructive/15 px-1 text-[10px] text-destructive">
                      {itens.prazos.length} prazo{itens.prazos.length > 1 ? "s" : ""}
                    </span>
                  )}
                  {itens && itens.tarefas.length > 0 && (
                    <span className="rounded bg-primary/15 px-1 text-[10px] text-primary">
                      {itens.tarefas.length} tarefa{itens.tarefas.length > 1 ? "s" : ""}
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        <div className="mt-4 border-t pt-4">
          <p className="mb-2 text-sm font-medium">{formatarData(diaSelecionado)}</p>
          {!itensDoDiaSelecionado ||
          (itensDoDiaSelecionado.prazos.length === 0 && itensDoDiaSelecionado.tarefas.length === 0) ? (
            <p className="text-sm text-muted-foreground">Nada agendado neste dia.</p>
          ) : (
            <div className="space-y-2">
              {itensDoDiaSelecionado.prazos.map((prazo) => (
                <div
                  key={prazo.id}
                  className="flex items-center justify-between rounded-md border border-destructive/30 p-2"
                >
                  <div>
                    <p className="text-sm font-medium capitalize">
                      Prazo {prazo.tipo} — {prazo.processo ? formatarNumeroCnj(prazo.processo.numero_cnj) : "Processo"}
                    </p>
                    {prazo.descricao && <p className="text-xs text-muted-foreground">{prazo.descricao}</p>}
                  </div>
                  <Badge variant="destructive">{prazo.status}</Badge>
                </div>
              ))}
              {itensDoDiaSelecionado.tarefas.map((tarefa) => (
                <div
                  key={tarefa.id}
                  className="flex items-center justify-between rounded-md border border-primary/30 p-2"
                >
                  <div>
                    <p className="text-sm font-medium">{tarefa.titulo}</p>
                    <p className="text-xs text-muted-foreground">
                      {tarefa.responsavel ? tarefa.responsavel.nome : "Sem responsável"}
                    </p>
                  </div>
                  <Badge variant={tarefa.status === "concluida" ? "success" : "secondary"}>{tarefa.status}</Badge>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
