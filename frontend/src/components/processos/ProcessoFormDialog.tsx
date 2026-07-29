import { useEffect, useState, type FormEvent } from "react";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { listClientes } from "@/services/clienteService";
import type {
  FaseProcessual,
  Processo,
  ProcessoCreateInput,
  ProcessoUpdateInput,
  StatusProcesso,
} from "@/types/processo";

interface ProcessoFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  processo: Processo | null;
  onSubmitCreate: (data: ProcessoCreateInput) => Promise<void>;
  onSubmitUpdate: (id: string, data: ProcessoUpdateInput) => Promise<void>;
  erro: string | null;
  enviando: boolean;
}

const CAMPOS_VAZIOS = {
  numero_cnj: "",
  cliente_id: "",
  vara: "",
  tribunal: "",
  comarca: "",
  tipo_acao: "",
  fase_processual: "conhecimento" as FaseProcessual,
  status: "ativo" as StatusProcesso,
  polo_ativo: "",
  polo_passivo: "",
  data_distribuicao: "",
  valor_causa: "",
};

export function ProcessoFormDialog({
  open,
  onOpenChange,
  processo,
  onSubmitCreate,
  onSubmitUpdate,
  erro,
  enviando,
}: ProcessoFormDialogProps) {
  const [form, setForm] = useState(CAMPOS_VAZIOS);
  const editando = processo !== null;

  const { data: clientesData } = useQuery({
    queryKey: ["clientes-select"],
    queryFn: () => listClientes({ pageSize: 100 }),
    enabled: open && !editando,
  });

  useEffect(() => {
    if (processo) {
      setForm({
        numero_cnj: processo.numero_cnj,
        cliente_id: processo.cliente_id,
        vara: processo.vara ?? "",
        tribunal: processo.tribunal ?? "",
        comarca: processo.comarca ?? "",
        tipo_acao: processo.tipo_acao ?? "",
        fase_processual: processo.fase_processual,
        status: processo.status,
        polo_ativo: processo.polo_ativo ?? "",
        polo_passivo: processo.polo_passivo ?? "",
        data_distribuicao: processo.data_distribuicao ?? "",
        valor_causa: processo.valor_causa ?? "",
      });
    } else {
      setForm(CAMPOS_VAZIOS);
    }
  }, [processo, open]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      if (editando && processo) {
        await onSubmitUpdate(processo.id, {
          vara: form.vara || undefined,
          tribunal: form.tribunal || undefined,
          comarca: form.comarca || undefined,
          tipo_acao: form.tipo_acao || undefined,
          fase_processual: form.fase_processual,
          status: form.status,
          polo_ativo: form.polo_ativo || undefined,
          polo_passivo: form.polo_passivo || undefined,
          data_distribuicao: form.data_distribuicao || undefined,
          valor_causa: form.valor_causa || undefined,
        });
      } else {
        await onSubmitCreate({
          numero_cnj: form.numero_cnj,
          cliente_id: form.cliente_id,
          vara: form.vara || undefined,
          tribunal: form.tribunal || undefined,
          comarca: form.comarca || undefined,
          tipo_acao: form.tipo_acao || undefined,
          fase_processual: form.fase_processual,
          polo_ativo: form.polo_ativo || undefined,
          polo_passivo: form.polo_passivo || undefined,
          data_distribuicao: form.data_distribuicao || undefined,
          valor_causa: form.valor_causa || undefined,
        });
      }
    } catch {
      // erro exposto via prop `erro`
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{editando ? "Editar processo" : "Novo processo"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="numero_cnj">Número CNJ</Label>
              <Input
                id="numero_cnj"
                placeholder="0000000-00.0000.0.00.0000"
                value={form.numero_cnj}
                onChange={(e) => setForm((f) => ({ ...f, numero_cnj: e.target.value }))}
                disabled={editando}
                required
              />
            </div>
            <div className="space-y-2">
              <Label>Cliente</Label>
              {editando ? (
                <Input value={processo?.cliente?.nome_razao_social ?? ""} disabled />
              ) : (
                <Select
                  value={form.cliente_id}
                  onValueChange={(value) => setForm((f) => ({ ...f, cliente_id: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione..." />
                  </SelectTrigger>
                  <SelectContent>
                    {clientesData?.items.map((cliente) => (
                      <SelectItem key={cliente.id} value={cliente.id}>
                        {cliente.nome_razao_social}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="vara">Vara</Label>
              <Input id="vara" value={form.vara} onChange={(e) => setForm((f) => ({ ...f, vara: e.target.value }))} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="tribunal">Tribunal</Label>
              <Input
                id="tribunal"
                placeholder="TJSP"
                value={form.tribunal}
                onChange={(e) => setForm((f) => ({ ...f, tribunal: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="comarca">Comarca</Label>
              <Input
                id="comarca"
                value={form.comarca}
                onChange={(e) => setForm((f) => ({ ...f, comarca: e.target.value }))}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="tipo_acao">Tipo de ação</Label>
            <Input
              id="tipo_acao"
              value={form.tipo_acao}
              onChange={(e) => setForm((f) => ({ ...f, tipo_acao: e.target.value }))}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="polo_ativo">Polo ativo</Label>
              <Input
                id="polo_ativo"
                value={form.polo_ativo}
                onChange={(e) => setForm((f) => ({ ...f, polo_ativo: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="polo_passivo">Polo passivo</Label>
              <Input
                id="polo_passivo"
                value={form.polo_passivo}
                onChange={(e) => setForm((f) => ({ ...f, polo_passivo: e.target.value }))}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Fase processual</Label>
              <Select
                value={form.fase_processual}
                onValueChange={(value) => setForm((f) => ({ ...f, fase_processual: value as FaseProcessual }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="conhecimento">Conhecimento</SelectItem>
                  <SelectItem value="recursal">Recursal</SelectItem>
                  <SelectItem value="execucao">Execução</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {editando && (
              <div className="space-y-2">
                <Label>Status</Label>
                <Select
                  value={form.status}
                  onValueChange={(value) => setForm((f) => ({ ...f, status: value as StatusProcesso }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ativo">Ativo</SelectItem>
                    <SelectItem value="suspenso">Suspenso</SelectItem>
                    <SelectItem value="arquivado">Arquivado</SelectItem>
                    <SelectItem value="encerrado">Encerrado</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="data_distribuicao">Data de distribuição</Label>
              <Input
                id="data_distribuicao"
                type="date"
                value={form.data_distribuicao}
                onChange={(e) => setForm((f) => ({ ...f, data_distribuicao: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="valor_causa">Valor da causa (R$)</Label>
              <Input
                id="valor_causa"
                type="number"
                step="0.01"
                value={form.valor_causa}
                onChange={(e) => setForm((f) => ({ ...f, valor_causa: e.target.value }))}
              />
            </div>
          </div>

          {erro && <p className="text-sm text-destructive">{erro}</p>}

          <DialogFooter>
            <Button type="submit" disabled={enviando || (!editando && !form.cliente_id)}>
              {enviando ? "Salvando..." : "Salvar"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
