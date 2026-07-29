import { useState, type FormEvent } from "react";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { formatarNumeroCnj } from "@/lib/format";
import { listProcessos } from "@/services/processoService";
import type { DespesaCreateInput, TipoDespesa } from "@/types/financeiro";

interface DespesaFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (processoId: string, data: DespesaCreateInput) => Promise<void>;
  enviando: boolean;
}

export function DespesaFormDialog({ open, onOpenChange, onSubmit, enviando }: DespesaFormDialogProps) {
  const [processoId, setProcessoId] = useState("");
  const [tipo, setTipo] = useState<TipoDespesa>("custas");
  const [descricao, setDescricao] = useState("");
  const [valor, setValor] = useState("");
  const [dataDespesa, setDataDespesa] = useState("");

  const { data: processosData } = useQuery({
    queryKey: ["processos-select"],
    queryFn: () => listProcessos({ pageSize: 100 }),
    enabled: open,
  });

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    await onSubmit(processoId, { tipo, descricao: descricao || undefined, valor, data_despesa: dataDespesa });
    setProcessoId("");
    setTipo("custas");
    setDescricao("");
    setValor("");
    setDataDespesa("");
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Nova despesa</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Processo</Label>
            <Select value={processoId} onValueChange={setProcessoId}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione..." />
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
              <Select value={tipo} onValueChange={(value) => setTipo(value as TipoDespesa)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="custas">Custas</SelectItem>
                  <SelectItem value="diligencia">Diligência</SelectItem>
                  <SelectItem value="pericia">Perícia</SelectItem>
                  <SelectItem value="outros">Outros</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="valor">Valor (R$)</Label>
              <Input
                id="valor"
                type="number"
                step="0.01"
                value={valor}
                onChange={(e) => setValor(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="data_despesa">Data</Label>
              <Input
                id="data_despesa"
                type="date"
                value={dataDespesa}
                onChange={(e) => setDataDespesa(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="descricao">Descrição</Label>
              <Input id="descricao" value={descricao} onChange={(e) => setDescricao(e.target.value)} />
            </div>
          </div>

          <DialogFooter>
            <Button type="submit" disabled={enviando || !processoId}>
              {enviando ? "Salvando..." : "Salvar"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
