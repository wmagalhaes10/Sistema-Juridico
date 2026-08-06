# 🏢 Sistema Jurídico - Gestão de Processos Legais

Sistema completo de gestão de processos jurídicos para escritório de advocacia, desenvolvido com **FastAPI** (backend), **React** (frontend), **PostgreSQL** (banco), **Celery** (tarefas) e **Docker Compose** (deployment).

## ✨ Características

### 🔐 Autenticação & Segurança
- JWT com access (30min) e refresh (7 dias) tokens
- RBAC: admin, advogado, assistente com permissões granulares
- Bcrypt 4.0.1 para senhas (12 rounds)
- Axios interceptor para refresh automático

### 📊 Gestão de Processos
- CRUD completo de processos jurídicos
- Validação de número CNJ (ISO 7064 mod 97-10)
- Sincronização automática com DataJud API (7am daily)
- Rastreamento de movimentações por origem (DataJud/Escavador/Manual)
- Sistema de prazos com alertas automáticos

### 💼 Gestão Financeira
- Contratos de honorários (FIXO, ÊXITO, MISTO)
- Auto-geração de parcelas mensais com rounding na última
- Registro de pagamentos com recibos PDF (reportlab)
- Status dinâmico de parcelas (PENDENTE/PARCIAL/PAGO)
- Relatórios de receitas e despesas
- Cálculo de saldo por processo

### 📋 Publicações & Intimações
- Monitoramento de publicações DJEN (Diário de Justiça Eletrônico)
- Sincronização para OABs configuradas
- Filtros por status (não tratada, tratada, descartada)
- Link direto para inteiro teor do tribunal

### 📅 Agendamento & Tarefas
- Dashboard com 4 KPIs (prazos, vencidos, urgentes, tarefas)
- Visualização semanal e mensal
- Calendário de prazos e tarefas
- Criação rápida de tarefas e prazos
- Sistema de alertas (3/5/10 dias antes do vencimento)

### 🌐 Integrações
- **DataJud:** Sincronização de dados processuais em tempo real
- **BrasilAPI:** Calendário de feriados nacionais
- **DJEN/Comunica:** Publicações de intimações e comunicados
- **SMTP/SendGrid:** Disparo de alertas por email

## 📁 Estrutura

```
Sistema/
├── backend/                    # FastAPI Python
│   ├── app/core/              # Config, database, segurança, celery
│   ├── app/models/            # 9 modelos SQLAlchemy
│   ├── app/services/          # Lógica de negócio
│   ├── app/api/routes/        # Endpoints REST
│   ├── app/tasks/             # Celery tasks (sync, alertas)
│   ├── migrations/            # Alembic migrations
│   ├── tests/                 # 51 testes pytest
│   └── Dockerfile
│
├── frontend/                   # React TypeScript Vite
│   ├── src/components/        # shadcn/ui + layout
│   ├── src/pages/             # Dashboard, Clientes, Processos, etc
│   ├── src/services/          # API clients
│   ├── src/contexts/          # AuthContext
│   ├── src/types/             # TypeScript interfaces
│   └── Dockerfile
│
├── docker-compose.yml          # 6 serviços (postgres, redis, api, worker, beat, frontend)
├── .env.example               # Template de configuração
├── SISTEMA_COMPLETO.md        # Documentação técnica
├── QUICK_START.md             # Guia rápido
└── DOCKER_TROUBLESHOOTING.md  # Resolução de problemas
```

## 🚀 Quick Start

### Pré-requisitos
- Docker & Docker Compose
- (Opcional) Python 3.12+ e Node.js 20+ para desenvolvimento local

### Instalação

1. **Clone o arquivo .env**
```bash
copy .env.example .env
```

2. **(Opcional) Configure integrações**
```env
DATAJUD_API_KEY=sua-chave-datajud
DJEN_OABS=240608/RJ
SMTP_USER=seu@email.com
```

3. **Build & Iniciar**
```bash
docker-compose build
docker-compose up
```

4. **Acesse**
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

## 📚 Documentação

- **[SISTEMA_COMPLETO.md](SISTEMA_COMPLETO.md)** — Arquitetura, stack, banco de dados, configuração
- **[QUICK_START.md](QUICK_START.md)** — Passos rápidos, troubleshooting, checklist
- **[DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md)** — Resolução de problemas comuns

## 🧪 Testes

### Backend
```bash
docker-compose exec api pytest -v
# 51 testes passando ✓
```

### Frontend
```bash
cd frontend
npm test
# Ready to test
```

## 🛠️ Stack Completo

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Backend | FastAPI | 0.100+ |
| ORM | SQLAlchemy | 2.0 |
| BD | PostgreSQL | 16 |
| Cache/Queue | Redis | 7 |
| Task Scheduler | Celery + Beat | 5.3 |
| Frontend | React | 18 |
| Language | TypeScript | 5.0 |
| Build | Vite | 5.0 |
| UI | shadcn/ui (Radix UI) | latest |
| HTTP | Axios | 1.6+ |
| Container | Docker Compose | 3.9 |
| Auth | JWT HS256 | python-jose |

## 📖 Endpoints Principais

### Autenticação
- `POST /auth/login` — Login (email + senha)
- `POST /auth/refresh` — Renovar tokens
- `GET /auth/me` — Usuário autenticado

### Clientes
- `GET /clientes` — Listagem com paginação
- `POST /clientes` — Criar cliente
- `GET /clientes/{id}` — Detalhe
- `PATCH /clientes/{id}` — Atualizar
- `DELETE /clientes/{id}` — Deletar

### Processos
- `GET /processos` — Listagem com filtros
- `POST /processos` — Criar processo
- `GET /processos/{id}` — Detalhe
- `GET /processos/{id}/movimentacoes` — Histórico
- `POST /processos/{id}/movimentacoes` — Adicionar movimento
- `GET /processos/{id}/prazos` — Prazos associados

### Prazos
- `GET /prazos` — Listagem com filtros
- `GET /prazos/dashboard` — Resumo semanal/mensal
- `POST /prazos` — Criar prazo
- `PATCH /prazos/{id}` — Atualizar

### Financeiro
- `POST /contratos-honorarios` — Criar contrato
- `GET /parcelas` — Listagem
- `PATCH /parcelas/{id}` — Atualizar parcela
- `POST /parcelas/{id}/pagamento` — Registrar pagamento
- `GET /parcelas/{id}/recibo` — PDF recibo
- `POST /despesas` — Criar despesa
- `GET /processos/{id}/saldo` — Saldo do processo
- `GET /relatorios/receitas` — Relatório receitas
- `GET /relatorios/despesas` — Relatório despesas

### Publicações
- `GET /publicacoes` — Listagem com paginação
- `GET /publicacoes/resumo` — Contador por status
- `POST /publicacoes/sincronizar` — Sincronizar DJEN
- `PATCH /publicacoes/{id}` — Atualizar status

## ✅ Validações

- **CPF:** Validação de dígito verificador
- **CNPJ:** Validação de dígitos verificadores
- **CNJ:** Validação ISO 7064 mod 97-10
- **Datas:** Cálculo de dias úteis (pula finais de semana + feriados)
- **Números:** Formatação e validação de entrada

## 🔄 Fluxos Automáticos

### Sincronização DataJud (7:00 AM)
1. Celery Beat executa tarefa agendada
2. Para cada processo ATIVO, consulta DataJud
3. Importa novos movimentos
4. Auto-cria prazos (5/15 dias úteis conforme tipo)
5. Continua em erro (não bloqueia outros processos)

### Alertas de Prazos (7:15 AM)
1. Verifica prazos vencendo em 3, 5, 10 dias
2. Envia email para responsável (advogado_responsavel ou responsavel)
3. Inclui: processo, prazo, data limite, descrição
4. Usa SMTP ou SendGrid conforme configurado

### Sincronização DJEN
1. Usuário clica "Sincronizar agora"
2. API consome feed Comunica/DJEN
3. Filtra por OABs monitoradas
4. Cria registros com status "não_tratada"
5. Usuário marca como "tratada" ou "descartada"

## 🎓 Conceitos-Chave

- **Prazos Pendentes:** Status = "pendente" e data_prazo >= hoje
- **Prazos Vencidos:** Status = "pendente" e data_prazo < hoje
- **Dias Úteis:** Pula sábados, domingos e feriados nacionais
- **Parcelas:** Status calculado dinamicamente (soma pagamentos / valor contratado)
- **Rounding:** Última parcela absorve diferenças de centavos
- **Tokens:** Stateless (JWT), sem revocation table (single-office)

## 📝 Notas Importantes

- **bcrypt 4.0.1** — Crítico para compatibilidade com passlib
- **Refresh automático** — Axios intercepta 401, renova token, retenta request
- **Hot-reload** — Habilitado em desenvolvimento (Frontend + Backend)
- **Healthchecks** — Docker Compose aguarda postgres/redis antes de api/celery

## 🐛 Troubleshooting

Encontrou erro? Verifique:

1. **Logs:** `docker-compose logs -f`
2. **Banco:** Resetar volumes com `docker-compose down -v`
3. **Cache Docker:** `docker system prune -af`
4. **Documentação:** Veja [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md)

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte os arquivos de documentação (SISTEMA_COMPLETO.md, QUICK_START.md)
2. Verifique os logs: `docker-compose logs -f [service]`
3. Resetar volumes se necessário: `docker-compose down -v`

## 📄 Licença

Propriedade do cliente (Sistema Jurídico - Uso Interno)

---

**Status:** ✅ Completo e Pronto para Uso  
**Última atualização:** 2026-07-27  
**Versão:** 1.0.0
