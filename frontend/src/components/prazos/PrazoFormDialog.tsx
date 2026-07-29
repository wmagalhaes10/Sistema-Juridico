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
import type { PrazoCreateInput, TipoPrazo } from "@/types/prazo";

interface PrazoFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Se informado, o prazo é criado direto para esse processo (sem exibir o seletor). */
  processoId?: string;
  onSubmit: (processoId: string, data: PrazoCreateInput) => Promise<void>;
  enviando: boolean;
}

export function PrazoFormDialog({ open, onOpenChange, processoId, onSubmit, enviando }: PrazoFormDialogProps) {
  const [processoSelecionado, setProcessoSelecionado] = useState("");
  const [dataPrazo, setDataPrazo] = useState("");
  const [tipo, setTipo] = useState<TipoPrazo>("peremptorio");
  const [descricao, setDescricao] = useState("");
  const [responsavelId, setResponsavelId] = useState("");

  const precisaSelecionarProcesso = !processoId;

  const { data: processosData } = useQuery({
    queryKey: ["processos-select"],
    queryFn: () => listProcessos({ pageSize: 100 }),
    enabled: open && precisaSelecionarProcesso,
  });

  const { data: usuarios } = useQuery({
    queryKey: ["usuarios-basico"],
    queryFn: listUsuariosBasico,
    enabled: open,
  });

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const alvo = processoId ?? processoSelecionado;
    await onSubmit(alvo, {
      data_prazo: dataPrazo,
      tipo,
      descricao: descricao || undefined,
      responsavel_id: responsavelId || undefined,
    });
    setProcessoSelecionado("");
    setDataPrazo("");
    setTipo("peremptorio");
    setDescricao("");
    setResponsavelId("");
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Novo prazo</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {precisaSelecionarProcesso && (
            <div className="space-y-2">
              <Label>Processo</Label>
              <Select value={processoSelecionado} onValueChange={setProcessoSelecionado}>
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
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="data_prazo">Data do prazo</Label>
              <Input
                id="data_prazo"
                type="date"
                value={dataPrazo}
                onChange={(e) => setDataPrazo(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label>Tipo</Label>
              <Select value={tipo} onValueChange={(value) => setTipo(value as TipoPrazo)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="peremptorio">Peremptório</SelectItem>
                  <SelectItem value="dilatorio">Dilatório</SelectItem>
                  <SelectItem value="recursal">Recursal</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label>Responsável (opcional)</Label>
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

          <div className="space-y-2">
            <Label htmlFor="descricao">Descrição</Label>
            <Input id="descricao" value={descricao} onChange={(e) => setDescricao(e.target.value)} />
          </div>

          <DialogFooter>
            <Button type="submit" disabled={enviando || (precisaSelecionarProcesso && !processoSelecionado)}>
              {enviando ? "Salvando..." : "Salvar"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
