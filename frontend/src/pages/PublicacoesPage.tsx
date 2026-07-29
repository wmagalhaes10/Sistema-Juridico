import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import { CheckCircle2, ExternalLink, RefreshCw, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatarData, formatarNumeroCnj } from "@/lib/format";
import {
  atualizarStatusPublicacao,
  getResumoPublicacoes,
  listPublicacoes,
  sincronizarPublicacoes,
} from "@/services/publicacaoService";
import type { Publicacao, StatusPublicacao } from "@/types/publicacao";

const PAGE_SIZE = 10;

const STATUS_LABEL: Record<StatusPublicacao, string> = {
  nao_tratada: "Não tratada",
  tratada: "Tratada",
  descartada: "Descartada",
};

function extrairErro(erro: unknown): string {
  const axiosErro = erro as AxiosError<{ detail?: string }>;
  return axiosErro.response?.data?.detail ?? "Ocorreu um erro. Tente novamente.";
}

function CardPublicacao({
  publicacao,
  onTratar,
  onDescartar,
}: {
  publicacao: Publicacao;
  onTratar: () => void;
  onDescartar: () => void;
}) {
  const [expandida, setExpandida] = useState(false);
  const texto = publicacao.texto ?? "";
  const resumoTexto = texto.length > 300 && !expandida ? `${texto.slice(0, 300)}...` : texto;

  return (
    <div className="border-b py-4 last:border-0">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline">{publicacao.sigla_tribunal ?? "?"}</Badge>
            <Badge variant="secondary">{publicacao.tipo_comunicacao ?? "Comunicação"}</Badge>
            {publicacao.tipo_documento && <Badge variant="outline">{publicacao.tipo_documento}</Badge>}
            <span className="text-sm text-muted-foreground">
              {formatarData(publicacao.data_disponibilizacao)} · {publicacao.nome_orgao ?? ""}
            </span>
          </div>

          <p className="mt-1 font-medium">
            {publicacao.numero_processo ? formatarNumeroCnj(publicacao.numero_processo) : "Processo não identificado"}
            {publicacao.processo && (
              <Link to={`/processos/${publicacao.processo.id}`} className="ml-2 text-sm text-blue-600 underline">
                ver processo cadastrado
              </Link>
            )}
          </p>

          {texto && (
            <p className="mt-1 whitespace-pre-line text-sm text-muted-foreground">{resumoTexto}</p>
          )}
          {texto.length > 300 && (
            <button
              type="button"
              className="mt-1 text-sm text-blue-600 underline"
              onClick={() => setExpandida((v) => !v)}
            >
              {expandida ? "Recolher" : "Ler mais"}
            </button>
          )}

          {publicacao.link && (
            <a
              href={publicacao.link}
              target="_blank"
              rel="noreferrer"
              className="mt-1 flex items-center gap-1 text-sm text-blue-600 underline"
            >
              <ExternalLink className="h-3 w-3" />
              Inteiro teor no tribunal
            </a>
          )}
        </div>

        <div className="flex shrink-0 flex-col items-end gap-2">
          <Badge
            variant={
              publicacao.status === "nao_tratada"
                ? "destructive"
                : publicacao.status === "tratada"
                  ? "success"
                  : "secondary"
            }
          >
            {STATUS_LABEL[publicacao.status]}
          </Badge>
          {publicacao.status === "nao_tratada" && (
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={onTratar}>
                <CheckCircle2 className="mr-1 h-4 w-4" />
                Tratar
              </Button>
              <Button size="sm" variant="ghost" onClick={onDescartar}>
                <Trash2 className="mr-1 h-4 w-4" />
                Descartar
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function PublicacoesPage() {
  const queryClient = useQueryClient();
  const [filtroStatus, setFiltroStatus] = useState<StatusPublicacao>("nao_tratada");
  const [page, setPage] = useState(1);

  const { data: resumo } = useQuery({ queryKey: ["publicacoes-resumo"], queryFn: getResumoPublicacoes });

  const { data, isLoading } = useQuery({
    queryKey: ["publicacoes", filtroStatus, page],
    queryFn: () => listPublicacoes({ page, pageSize: PAGE_SIZE, status: filtroStatus }),
  });

  function invalidar() {
    queryClient.invalidateQueries({ queryKey: ["publicacoes"] });
    queryClient.invalidateQueries({ queryKey: ["publicacoes-resumo"] });
  }

  const sincronizarMutation = useMutation({
    mutationFn: sincronizarPublicacoes,
    onSuccess: (novas) => {
      invalidar();
      window.alert(`${novas.length} nova(s) publicação(ões) importada(s) do DJEN.`);
    },
    onError: (erro) => window.alert(extrairErro(erro)),
  });

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: StatusPublicacao }) =>
      atualizarStatusPublicacao(id, status),
    onSuccess: invalidar,
    onError: (erro) => window.alert(extrairErro(erro)),
  });

  const totalPaginas = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

  const FILTROS: { valor: StatusPublicacao; rotulo: string; contagem?: number }[] = [
    { valor: "nao_tratada", rotulo: "Não tratadas", contagem: resumo?.nao_tratadas },
    { valor: "tratada", rotulo: "Tratadas", contagem: resumo?.tratadas },
    { valor: "descartada", rotulo: "Descartadas", contagem: resumo?.descartadas },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Publicações</h2>
          <p className="text-muted-foreground">
            Intimações dos diários oficiais (DJEN) monitoradas pela OAB do escritório
          </p>
        </div>
        <Button onClick={() => sincronizarMutation.mutate()} disabled={sincronizarMutation.isPending}>
          <RefreshCw className="mr-2 h-4 w-4" />
          {sincronizarMutation.isPending ? "Sincronizando..." : "Sincronizar agora"}
        </Button>
      </div>

      <div className="flex gap-2">
        {FILTROS.map((filtro) => (
          <Button
            key={filtro.valor}
            variant={filtroStatus === filtro.valor ? "default" : "outline"}
            onClick={() => {
              setFiltroStatus(filtro.valor);
              setPage(1);
            }}
          >
            {filtro.rotulo}
            {filtro.contagem !== undefined && ` (${filtro.contagem})`}
          </Button>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            {isLoading ? "Carregando..." : `${data?.total ?? 0} publicação(ões)`}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!isLoading && (data?.items.length ?? 0) === 0 && (
            <p className="text-sm text-muted-foreground">Nenhuma publicação neste filtro.</p>
          )}
          {data?.items.map((publicacao) => (
            <CardPublicacao
              key={publicacao.id}
              publicacao={publicacao}
              onTratar={() => statusMutation.mutate({ id: publicacao.id, status: "tratada" })}
              onDescartar={() => statusMutation.mutate({ id: publicacao.id, status: "descartada" })}
            />
          ))}
        </CardContent>
      </Card>

      {data && data.total > PAGE_SIZE && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>
            Página {data.page} de {totalPaginas}
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
    </div>
  );
}
