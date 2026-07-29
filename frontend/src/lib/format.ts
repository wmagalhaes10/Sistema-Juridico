export function formatarNumeroCnj(numero: string): string {
  if (numero.length !== 20) return numero;
  return `${numero.slice(0, 7)}-${numero.slice(7, 9)}.${numero.slice(9, 13)}.${numero.slice(13, 14)}.${numero.slice(14, 16)}.${numero.slice(16, 20)}`;
}

export function formatarData(iso: string): string {
  const [ano, mes, dia] = iso.slice(0, 10).split("-");
  return `${dia}/${mes}/${ano}`;
}

export function formatarMoeda(valor: number | string): string {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(Number(valor));
}
