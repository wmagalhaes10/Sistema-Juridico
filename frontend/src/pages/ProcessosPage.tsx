import { useState, type MouseEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import { Plus, Search, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { ProcessoFormDialog } from "@/components/processos/ProcessoFormDialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatarNumeroCnj } from "@/lib/format";
import { createProcesso, deleteProcesso, listProcessos, updateProcesso } from "@/services/processoService";
import type { Processo, ProcessoCreateInput, ProcessoUpdateInput, StatusProcesso } from "@/types/processo";

const PAGE_SIZE = 10;

const STATUS_LABEL: Record<StatusProcesso, string> = {
  ativo: "Ativo",
  suspenso: "Suspenso",
  arquivado: "Arquivado",
  encerrado: "Encerrado",
};

const STATUS_VARIANT: Record<StatusProcesso, "success" | "secondary" | "warning" | "outline"> = {
  ativo: "success",
  suspenso: "warning",
  arquivado: "outline",
  encerrado: "secondary",
};

function extrairErro(erro: unknown): string {
  const axiosErro = erro as AxiosError<{ detail?: string }>;
  return axiosErro.response?.data?.detail ?? "Ocorreu um erro. Tente novamente.";
}

export function ProcessosPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [busca, setBusca] = useState("");
  const [statusFiltro, setStatusFiltro] = useState<string>("todos");
  const [page, setPage] = useState(1);
  const [dialogAberto, setDialogAberto] = useState(false);
  const [processoEditando, setProcessoEditando] = useState<Processo | null>(null);
  const [erroForm, setErroForm] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["processos", page, busca, statusFiltro],
    queryFn: () =>
      listProcessos({
        page,
        pageSize: PAGE_SIZE,
        busca,
        statusProcesso: statusFiltro === "todos" ? undefined : statusFiltro,
      }),
  });

  const criarMutation = useMutation({
    mutationFn: createProcesso,
    onSuccess: (novoProcesso) => {
      queryClient.invalidateQueries({ queryKey: ["processos"] });
      setDialogAberto(false);
      setErroForm(null);
      navigate(`/processos/${novoProcesso.id}`);
    },
    onError: (erro) => setErroForm(extrairErro(erro)),
  });

  const atualizarMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: ProcessoUpdateInput }) => updateProcesso(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["processos"] });
      setDialogAberto(false);
      setErroForm(null);
    },
    onError: (erro) => setErroForm(extrairErro(erro)),
  });

  const excluirMutation = useMutation({
    mutationFn: deleteProcesso,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["processos"] }),
    onError: (erro) => window.alert(extrairErro(erro)),
  });

  function abrirNovo() {
    setProcessoEditando(null);
    setErroForm(null);
    setDialogAberto(true);
  }

  function handleExcluir(processo: Processo, event: MouseEvent) {
    event.stopPropagation();
    if (window.confirm(`Excluir o processo "${formatarNumeroCnj(processo.numero_cnj)}"?`)) {
      excluirMutation.mutate(processo.id);
    }
  }

  const totalPaginas = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold tracking-tight">Processos</h2>
        <Button onClick={abrirNovo}>
          <Plus className="mr-2 h-4 w-4" />
          Novo processo
        </Button>
      </div>

      <div className="flex gap-3">
        <div className="relative max-w-sm flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Buscar por número, partes ou tipo de ação..."
            className="pl-9"
            value={busca}
            onChange={(e) => {
              setBusca(e.target.value);
              setPage(1);
            }}
          />
        </div>
        <Select
          value={statusFiltro}
          onValueChange={(value) => {
            setStatusFiltro(value);
            setPage(1);
          }}
        >
          <SelectTrigger className="w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="todos">Todos os status</SelectItem>
            <SelectItem value="ativo">Ativo</SelectItem>
            <SelectItem value="suspenso">Suspenso</SelectItem>
            <SelectItem value="arquivado">Arquivado</SelectItem>
            <SelectItem value="encerrado">Encerrado</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Número CNJ</TableHead>
                <TableHead>Cliente</TableHead>
                <TableHead>Fase</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-16">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading && (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-muted-foreground">
                    Carregando...
                  </TableCell>
                </TableRow>
              )}
              {!isLoading && data?.items.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-muted-foreground">
                    Nenhum processo encontrado.
                  </TableCell>
                </TableRow>
              )}
              {data?.items.map((processo) => (
                <TableRow
                  key={processo.id}
                  className="cursor-pointer"
                  onClick={() => navigate(`/processos/${processo.id}`)}
                >
                  <TableCell className="font-medium">{formatarNumeroCnj(processo.numero_cnj)}</TableCell>
                  <TableCell>{processo.cliente?.nome_razao_social ?? "-"}</TableCell>
                  <TableCell className="capitalize">{processo.fase_processual}</TableCell>
                  <TableCell>
                    <Badge variant={STATUS_VARIANT[processo.status]}>{STATUS_LABEL[processo.status]}</Badge>
                  </TableCell>
                  <TableCell>
                    <Button variant="ghost" size="icon" onClick={(e) => handleExcluir(processo, e)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {data && data.total > 0 && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>
            Página {data.page} de {totalPaginas} · {data.total} processo(s)
          </span>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              Anterior
            </Button>
            <Button variant="outline" size="sm" disabled={page >= totalPaginas} onClick={() => setPage((p) => p + 1)}>
              Próxima
            </Button>
          </div>
        </div>
      )}

      <ProcessoFormDialog
        open={dialogAberto}
        onOpenChange={setDialogAberto}
        processo={processoEditando}
        erro={erroForm}
        enviando={criarMutation.isPending || atualizarMutation.isPending}
        onSubmitCreate={async (dataInput: ProcessoCreateInput) => {
          await criarMutation.mutateAsync(dataInput);
        }}
        onSubmitUpdate={async (id: string, dataInput: ProcessoUpdateInput) => {
          await atualizarMutation.mutateAsync({ id, data: dataInput });
        }}
      />
    </div>
  );
}
