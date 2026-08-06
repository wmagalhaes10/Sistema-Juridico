import { useState, type FormEvent } from "react";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { formatarNumeroCnj } from "@/lib/format";
import { listClientes } from "@/services/clienteService";
import { listProcessos } from "@/services/processoService";
import type { ContratoCreateInput, TipoContrato } from "@/types/financeiro";

interface ContratoFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: ContratoCreateInput) => Promise<void>;
  erro: string | null;
  enviando: boolean;
}

export function ContratoFormDialog({ open, onOpenChange, onSubmit, erro, enviando }: ContratoFormDialogProps) {
  const [clienteId, setClienteId] = useState("");
  const [processoId, setProcessoId] = useState("");
  const [tipo, setTipo] = useState<TipoContrato>("fixo");
  const [valorContratado, setValorContratado] = useState("");
  const [numeroParcelas, setNumeroParcelas] = useState("1");
  const [dataAssinatura, setDataAssinatura] = useState("");
  const [observacoes, setObservacoes] = useState("");

  const { data: clientesData } = useQuery({
    queryKey: ["clientes-select"],
    queryFn: () => listClientes({ pageSize: 100 }),
    enabled: open,
  });

  const { data: processosData } = useQuery({
    queryKey: ["processos-select"],
    queryFn: () => listProcessos({ pageSize: 100 }),
    enabled: open,
  });

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    await onSubmit({
      cliente_id: clienteId,
      processo_id: processoId || undefined,
      tipo,
      valor_contratado: valorContratado,
      numero_parcelas: Number(numeroParcelas),
      data_assinatura: dataAssinatura || undefined,
      observacoes: observacoes || undefined,
    });
    setClienteId("");
    setProcessoId("");
    setTipo("fixo");
    setValorContratado("");
    setNumeroParcelas("1");
    setDataAssinatura("");
    setObservacoes("");
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Novo contrato de honorários</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Cliente</Label>
            <Select value={clienteId} onValueChange={setClienteId}>
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
          </div>

          <div className="space-y-2">
            <Label>Processo (opcional)</Label>
            <Select value={processoId} onValueChange={setProcessoId}>
              <SelectTrigger>
                <SelectValue placeholder="Nenhum" />
              </SelectTrigger>
              <SelectContent>
                {processosData?.items.map((processo) => (
                  <SelectItem key={processo.id} value={processo.id}>
                    {formatarNumeroCnj(processo.numero_cnj)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Tipo</Label>
              <Select value={tipo} onValueChange={(value) => setTipo(value as TipoContrato)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="fixo">Fixo</SelectItem>
                  <SelectItem value="exito">Êxito</SelectItem>
                  <SelectItem value="misto">Misto</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="valor">Valor contratado (R$)</Label>
              <Input
                id="valor"
                type="number"
                step="0.01"
                value={valorContratado}
                onChange={(e) => setValorContratado(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="numero_parcelas">Nº de parcelas</Label>
              <Input
                id="numero_parcelas"
                type="number"
                min={1}
                value={numeroParcelas}
                onChange={(e) => setNumeroParcelas(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="data_assinatura">Data de assinatura</Label>
              <Input
                id="data_assinatura"
                type="date"
                value={dataAssinatura}
                onChange={(e) => setDataAssinatura(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="observacoes">Observações</Label>
            <Input id="observacoes" value={observacoes} onChange={(e) => setObservacoes(e.target.value)} />
          </div>

          {erro && <p className="text-sm text-destructive">{erro}</p>}

          <DialogFooter>
            <Button type="submit" disabled={enviando || !clienteId}>
              {enviando ? "Salvando..." : "Salvar"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
