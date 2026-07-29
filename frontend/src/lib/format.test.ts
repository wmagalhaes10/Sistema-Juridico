import { describe, expect, it } from "vitest";

import { formatarData, formatarMoeda, formatarNumeroCnj } from "@/lib/format";

describe("formatarNumeroCnj", () => {
  it("formata um número de 20 dígitos no padrão CNJ", () => {
    expect(formatarNumeroCnj("00000013920248260100")).toBe("0000001-39.2024.8.26.0100");
  });

  it("retorna o valor original se não tiver 20 dígitos", () => {
    expect(formatarNumeroCnj("123")).toBe("123");
  });
});

describe("formatarData", () => {
  it("converte data ISO para dd/mm/aaaa", () => {
    expect(formatarData("2026-07-15")).toBe("15/07/2026");
  });

  it("aceita datetime ISO completo, ignorando a hora", () => {
    expect(formatarData("2026-07-15T10:30:00")).toBe("15/07/2026");
  });
});

describe("formatarMoeda", () => {
  it("formata número como moeda brasileira", () => {
    expect(formatarMoeda(1234.5)).toContain("1.234,50");
  });

  it("aceita string numérica (vinda da API como Decimal)", () => {
    expect(formatarMoeda("500.00")).toContain("500,00");
  });

  it("inclui o prefixo R$", () => {
    expect(formatarMoeda(10)).toContain("R$");
  });
});
