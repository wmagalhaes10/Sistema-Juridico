import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { MovimentacaoCreateInput } from "@/types/processo";

interface MovimentacaoFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: MovimentacaoCreateInput) => Promise<void>;
  enviando: boolean;
}

export function MovimentacaoFormDialog({ open, onOpenChange, onSubmit, enviando }: MovimentacaoFormDialogProps) {
  const [dataMovimentacao, setDataMovimentacao] = useState("");
  const [descricao, setDescricao] = useState("");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    await onSubmit({ data_movimentacao: dataMovimentacao, descricao });
    setDataMovimentacao("");
    setDescricao("");
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Nova movimentação</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="data_movimentacao">Data e hora</Label>
            <Input
              id="data_movimentacao"
              type="datetime-local"
              value={dataMovimentacao}
              onChange={(e) => setDataMovimentacao(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="descricao">Descrição</Label>
            <Input id="descricao" value={descricao} onChange={(e) => setDescricao(e.target.value)} required />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={enviando}>
              {enviando ? "Salvando..." : "Salvar"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
