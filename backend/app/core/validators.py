import re


def somente_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor)


def cpf_valido(cpf: str) -> bool:
    cpf = somente_digitos(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in (9, 10):
        soma = sum(int(cpf[j]) * ((i + 1) - j) for j in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[i]):
            return False
    return True


def numero_cnj_valido(numero: str) -> bool:
    """Valida número unificado CNJ (NNNNNNN-DD.AAAA.J.TR.OOOO) via ISO 7064 mod 97-10."""
    n = somente_digitos(numero)
    if len(n) != 20:
        return False
    seq, dd, resto = n[:7], n[7:9], n[9:]
    return int(seq + resto + dd) % 97 == 1


def cnpj_valido(cnpj: str) -> bool:
    cnpj = somente_digitos(cnpj)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1
    for pesos, pos in ((pesos1, 12), (pesos2, 13)):
        soma = sum(int(cnpj[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        digito = 0 if resto < 2 else 11 - resto
        if digito != int(cnpj[pos]):
            return False
    return True
