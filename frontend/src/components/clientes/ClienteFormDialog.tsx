import { useEffect, useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { Cliente, ClienteCreateInput, ClienteUpdateInput, TipoPessoa } from "@/types/cliente";

interface ClienteFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  cliente: Cliente | null;
  onSubmitCreate: (data: ClienteCreateInput) => Promise<void>;
  onSubmitUpdate: (id: string, data: ClienteUpdateInput) => Promise<void>;
  erro: string | null;
  enviando: boolean;
}

const CAMPOS_VAZIOS = {
  tipo_pessoa: "fisica" as TipoPessoa,
  cpf_cnpj: "",
  nome_razao_social: "",
  endereco: "",
  telefone: "",
  email: "",
  oab_responsavel: "",
};

export function ClienteFormDialog({
  open,
  onOpenChange,
  cliente,
  onSubmitCreate,
  onSubmitUpdate,
  erro,
  enviando,
}: ClienteFormDialogProps) {
  const [form, setForm] = useState(CAMPOS_VAZIOS);
  const editando = cliente !== null;

  useEffect(() => {
    if (cliente) {
      setForm({
        tipo_pessoa: cliente.tipo_pessoa,
        cpf_cnpj: cliente.cpf_cnpj,
        nome_razao_social: cliente.nome_razao_social,
        endereco: cliente.endereco ?? "",
        telefone: cliente.telefone ?? "",
        email: cliente.email ?? "",
        oab_responsavel: cliente.oab_responsavel ?? "",
      });
    } else {
      setForm(CAMPOS_VAZIOS);
    }
  }, [cliente, open]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      if (editando && cliente) {
        await onSubmitUpdate(cliente.id, {
          nome_razao_social: form.nome_razao_social,
          endereco: form.endereco || undefined,
          telefone: form.telefone || undefined,
          email: form.email || undefined,
          oab_responsavel: form.oab_responsavel || undefined,
        });
      } else {
        await onSubmitCreate({
          tipo_pessoa: form.tipo_pessoa,
          cpf_cnpj: form.cpf_cnpj,
          nome_razao_social: form.nome_razao_social,
          endereco: form.endereco || undefined,
          telefone: form.telefone || undefined,
          email: form.email || undefined,
          oab_responsavel: form.oab_responsavel || undefined,
        });
      }
    } catch {
      // erro já é exposto via prop `erro`, tratado pelo componente pai
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{editando ? "Editar cliente" : "Novo cliente"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Tipo de pessoa</Label>
              <Select
                value={form.tipo_pessoa}
                onValueChange={(value) => setForm((f) => ({ ...f, tipo_pessoa: value as TipoPessoa }))}
                disabled={editando}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="fisica">Pessoa física</SelectItem>
                  <SelectItem value="juridica">Pessoa jurídica</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="cpf_cnpj">{form.tipo_pessoa === "fisica" ? "CPF" : "CNPJ"}</Label>
              <Input
                id="cpf_cnpj"
                value={form.cpf_cnpj}
                onChange={(e) => setForm((f) => ({ ...f, cpf_cnpj: e.target.value }))}
                disabled={editando}
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="nome">{form.tipo_pessoa === "fisica" ? "Nome completo" : "Razão social"}</Label>
            <Input
              id="nome"
              value={form.nome_razao_social}
              onChange={(e) => setForm((f) => ({ ...f, nome_razao_social: e.target.value }))}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="telefone">Telefone</Label>
              <Input
                id="telefone"
                value={form.telefone}
                onChange={(e) => setForm((f) => ({ ...f, telefone: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">E-mail</Label>
              <Input
                id="email"
                type="email"
                value={form.email}
                onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="endereco">Endereço</Label>
            <Input
              id="endereco"
              value={form.endereco}
              onChange={(e) => setForm((f) => ({ ...f, endereco: e.target.value }))}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="oab">OAB do responsável</Label>
            <Input
              id="oab"
              value={form.oab_responsavel}
              onChange={(e) => setForm((f) => ({ ...f, oab_responsavel: e.target.value }))}
            />
          </div>

          {erro && <p className="text-sm text-destructive">{erro}</p>}

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
