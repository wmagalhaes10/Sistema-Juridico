import { useState, type FormEvent } from "react";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { formatarNumeroCnj } from "@/lib/format";
import { listProcessos } from "@/services/processoService";
import { listUsuariosBasico } from "@/services/userService";
import type { TarefaCreateInput } from "@/types/tarefa";

interface TarefaFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: TarefaCreateInput) => Promise<void>;
  enviando: boolean;
}

export function TarefaFormDialog({ open, onOpenChange, onSubmit, enviando }: TarefaFormDialogProps) {
  const [titulo, setTitulo] = useState("");
  const [descricao, setDescricao] = useState("");
  const [dataVencimento, setDataVencimento] = useState("");
  const [responsavelId, setResponsavelId] = useState("");
  const [processoId, setProcessoId] = useState("");

  const { data: usuarios } = useQuery({
    queryKey: ["usuarios-basico"],
    queryFn: listUsuariosBasico,
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
      titulo,
      descricao: descricao || undefined,
      data_vencimento: dataVencimento || undefined,
      responsavel_id: responsavelId || undefined,
      processo_id: processoId || undefined,
    });
    setTitulo("");
    setDescricao("");
    setDataVencimento("");
    setResponsavelId("");
    setProcessoId("");
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Nova tarefa</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="titulo">Título</Label>
            <Input id="titulo" value={titulo} onChange={(e) => setTitulo(e.target.value)} required />
          </div>

          <div className="space-y-2">
            <Label htmlFor="descricao">Descrição</Label>
            <Input id="descricao" value={descricao} onChange={(e) => setDescricao(e.target.value)} />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="data_vencimento">Data (opcional)</Label>
              <Input
                id="data_vencimento"
                type="date"
                value={dataVencimento}
                onChange={(e) => setDataVencimento(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Responsável</Label>
              <Select value={responsavelId} onValueChange={setResponsavelId}>
                <SelectTrigger>
                  <SelectValue placeholder="Ninguém atribuído" />
                </SelectTrigger>
                <SelectContent>
                  {usuarios?.map((usuario) => (
                    <SelectItem key={usuario.id} value={usuario.id}>
                      {usuario.nome}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label>Processo relacionado (opcional)</Label>
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

          <DialogFooter>
            <Button type="submit" disabled={enviando || !titulo}>
              {enviando ? "Salvando..." : "Salvar"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
