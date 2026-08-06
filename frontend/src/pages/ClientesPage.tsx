import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import { Pencil, Plus, Search, Trash2 } from "lucide-react";

import { ClienteFormDialog } from "@/components/clientes/ClienteFormDialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { createCliente, deleteCliente, listClientes, updateCliente } from "@/services/clienteService";
import type { Cliente, ClienteCreateInput, ClienteUpdateInput } from "@/types/cliente";

const PAGE_SIZE = 10;

function extrairErro(erro: unknown): string {
  const axiosErro = erro as AxiosError<{ detail?: string }>;
  return axiosErro.response?.data?.detail ?? "Ocorreu um erro. Tente novamente.";
}

export function ClientesPage() {
  const queryClient = useQueryClient();
  const [busca, setBusca] = useState("");
  const [page, setPage] = useState(1);
  const [dialogAberto, setDialogAberto] = useState(false);
  const [clienteEditando, setClienteEditando] = useState<Cliente | null>(null);
  const [erroForm, setErroForm] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["clientes", page, busca],
    queryFn: () => listClientes({ page, pageSize: PAGE_SIZE, busca }),
  });

  const criarMutation = useMutation({
    mutationFn: createCliente,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clientes"] });
      setDialogAberto(false);
      setErroForm(null);
    },
    onError: (erro) => setErroForm(extrairErro(erro)),
  });

  const atualizarMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: ClienteUpdateInput }) => updateCliente(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clientes"] });
      setDialogAberto(false);
      setErroForm(null);
    },
    onError: (erro) => setErroForm(extrairErro(erro)),
  });

  const excluirMutation = useMutation({
    mutationFn: deleteCliente,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["clientes"] }),
    onError: (erro) => window.alert(extrairErro(erro)),
  });

  function abrirNovo() {
    setClienteEditando(null);
    setErroForm(null);
    setDialogAberto(true);
  }

  function abrirEdicao(cliente: Cliente) {
    setClienteEditando(cliente);
    setErroForm(null);
    setDialogAberto(true);
  }

  function handleExcluir(cliente: Cliente) {
    if (window.confirm(`Excluir o cliente "${cliente.nome_razao_social}"?`)) {
      excluirMutation.mutate(cliente.id);
    }
  }

  const totalPaginas = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold tracking-tight">Clientes</h2>
        <Button onClick={abrirNovo}>
          <Plus className="mr-2 h-4 w-4" />
          Novo cliente
        </Button>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Buscar por nome ou CPF/CNPJ..."
          className="pl-9"
          value={busca}
          onChange={(e) => {
            setBusca(e.target.value);
            setPage(1);
          }}
        />
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome / Razão social</TableHead>
                <TableHead>CPF/CNPJ</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Telefone</TableHead>
                <TableHead>E-mail</TableHead>
                <TableHead className="w-24">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-muted-foreground">
                    Carregando...
                  </TableCell>
                </TableRow>
              )}
              {!isLoading && data?.items.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-muted-foreground">
                    Nenhum cliente encontrado.
                  </TableCell>
                </TableRow>
              )}
              {data?.items.map((cliente) => (
                <TableRow key={cliente.id}>
                  <TableCell className="font-medium">{cliente.nome_razao_social}</TableCell>
                  <TableCell>{cliente.cpf_cnpj}</TableCell>
                  <TableCell>{cliente.tipo_pessoa === "fisica" ? "Física" : "Jurídica"}</TableCell>
                  <TableCell>{cliente.telefone || "-"}</TableCell>
                  <TableCell>{cliente.email || "-"}</TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon" onClick={() => abrirEdicao(cliente)}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => handleExcluir(cliente)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
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
            Página {data.page} de {totalPaginas} · {data.total} cliente(s)
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

      <ClienteFormDialog
        open={dialogAberto}
        onOpenChange={setDialogAberto}
        cliente={clienteEditando}
        erro={erroForm}
        enviando={criarMutation.isPending || atualizarMutation.isPending}
        onSubmitCreate={async (dataInput: ClienteCreateInput) => {
          await criarMutation.mutateAsync(dataInput);
        }}
        onSubmitUpdate={async (id: string, dataInput: ClienteUpdateInput) => {
          await atualizarMutation.mutateAsync({ id, data: dataInput });
        }}
      />
    </div>
  );
}
