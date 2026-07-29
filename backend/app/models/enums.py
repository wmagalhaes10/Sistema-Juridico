import enum


class ModuloSistema(str, enum.Enum):
    CLIENTES = "clientes"
    PROCESSOS = "processos"
    PRAZOS = "prazos"
    FINANCEIRO = "financeiro"
    TAREFAS = "tarefas"
    PUBLICACOES = "publicacoes"


class TipoPessoa(str, enum.Enum):
    FISICA = "fisica"
    JURIDICA = "juridica"


class FaseProcessual(str, enum.Enum):
    CONHECIMENTO = "conhecimento"
    RECURSAL = "recursal"
    EXECUCAO = "execucao"


class StatusProcesso(str, enum.Enum):
    ATIVO = "ativo"
    SUSPENSO = "suspenso"
    ARQUIVADO = "arquivado"
    ENCERRADO = "encerrado"


class OrigemMovimentacao(str, enum.Enum):
    DATAJUD = "datajud"
    ESCAVADOR = "escavador"
    MANUAL = "manual"


class TipoPrazo(str, enum.Enum):
    PEREMPTORIO = "peremptorio"
    DILATORIO = "dilatorio"
    RECURSAL = "recursal"


class StatusPrazo(str, enum.Enum):
    PENDENTE = "pendente"
    CUMPRIDO = "cumprido"
    PERDIDO = "perdido"


class TipoFeriado(str, enum.Enum):
    NACIONAL = "nacional"
    ESTADUAL = "estadual"
    MUNICIPAL = "municipal"


class TipoContrato(str, enum.Enum):
    FIXO = "fixo"
    EXITO = "exito"
    MISTO = "misto"


class StatusParcela(str, enum.Enum):
    PAGO = "pago"
    PENDENTE = "pendente"
    ATRASADO = "atrasado"


class TipoDespesa(str, enum.Enum):
    CUSTAS = "custas"
    DILIGENCIA = "diligencia"
    PERICIA = "pericia"
    OUTROS = "outros"


class StatusTarefa(str, enum.Enum):
    PENDENTE = "pendente"
    CONCLUIDA = "concluida"


class StatusPublicacao(str, enum.Enum):
    NAO_TRATADA = "nao_tratada"
    TRATADA = "tratada"
    DESCARTADA = "descartada"
