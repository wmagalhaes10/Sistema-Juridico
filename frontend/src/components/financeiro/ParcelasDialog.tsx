import { useMutation, useQueryClient } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { formatarData, formatarMoeda } from "@/lib/format";
import { baixarRecibo, registrarPagamento } from "@/services/financeiroService";
import type { ContratoHonorario, StatusParcela } from "@/types/financeiro";

interface ParcelasDialogProps {
  contrato: ContratoHonorario | null;
  onOpenChange: (open: boolean) => void;
}

const STATUS_LABEL: Record<StatusParcela, string> = {
  pago: "Pago",
  pendente: "Pendente",
  atrasado: "Atrasado",
};

const STATUS_VARIANT: Record<StatusParcela, "success" | "secondary" | "destructive"> = {
  pago: "success",
  pendente: "secondary",
  atrasado: "destructive",
};

export function ParcelasDialog({ contrato, onOpenChange }: ParcelasDialogProps) {
  const queryClient = useQueryClient();

  const pagarMutation = useMutation({
    mutationFn: registrarPagamento,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["contratos"] }),
  });

  return (
    <Dialog open={contrato !== null} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Parcelas do contrato</DialogTitle>
        </DialogHeader>
        <div className="space-y-2">
          {contrato?.parcelas.map((parcela) => (
            <div key={parcela.id} className="flex items-center justify-between border-b py-2 last:border-0">
              <div>
                <p className="font-medium">
                  Parcela {parcela.numero_parcela}/{contrato.numero_parcelas} · {formatarMoeda(parcela.valor)}
                </p>
                <p className="text-sm text-muted-foreground">
                  Vencimento: {formatarData(parcela.data_vencimento)}
                  {parcela.data_pagamento && ` · Pago em ${formatarData(parcela.data_pagamento)}`}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={STATUS_VARIANT[parcela.status]}>{STATUS_LABEL[parcela.status]}</Badge>
                {parcela.status !== "pago" ? (
                  <Button size="sm" variant="outline" onClick={() => pagarMutation.mutate(parcela.id)}>
                    Registrar pagamento
                  </Button>
                ) : (
                  <Button size="sm" variant="outline" onClick={() => baixarRecibo(parcela.id, parcela.numero_parcela)}>
                    Baixar recibo
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
