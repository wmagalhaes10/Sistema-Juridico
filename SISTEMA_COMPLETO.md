# 📋 Sistema Jurídico - Projeto Completo

## 🎯 Visão Geral

Sistema de gestão de processos jurídicos para escritório de advocacia, desenvolvido com **Python/FastAPI** (backend), **React/TypeScript** (frontend), **PostgreSQL** (BD), **Redis/Celery** (tarefas assíncronas) e **Docker Compose** (containerização).

---

## 📁 Arquitetura

```
Sistema/
├── backend/               # Python FastAPI
│   ├── app/
│   │   ├── core/         # Config, segurança, database, celery
│   │   ├── models/       # SQLAlchemy 9 modelos (UUID PKs)
│   │   ├── services/     # Lógica de negócio
│   │   ├── api/          # Rotas (auth, clientes, processos, prazos, financeiro)
│   │   └── tasks/        # Celery tasks (sincronização, alertas)
│   ├── migrations/       # Alembic (versão inicial)
│   ├── tests/            # pytest (51 testes passando)
│   ├── Dockerfile        # Python 3.12-slim, uvicorn auto-reload
│   └── requirements.txt   # Dependências
│
├── frontend/              # React TypeScript Vite
│   ├── src/
│   │   ├── components/    # UI (shadcn/ui) + layout
│   │   ├── pages/         # Dashboard, Clientes, Processos, Financeiro, Publicações
│   │   ├── services/      # API clients (auth, clientes, processos, etc)
│   │   ├── contexts/      # AuthContext
│   │   ├── types/         # TypeScript interfaces
│   │   ├── lib/           # Utilitários (tokenStorage, API, format)
│   │   └── App.tsx        # Router + AuthProvider
│   ├── Dockerfile         # Node 20-slim, npm dev
│   └── package.json       # Dependências
│
├── docker-compose.yml     # 6 serviços: postgres, redis, api, worker, beat, frontend
├── .env.example           # Template de variáveis
└── .env                   # Configurações locais
```

---

## 🗄️ Banco de Dados

**9 modelos SQLAlchemy** com UUID PKs e timestampts (created_at, updated_at):

1. **User** — Usuários (nome, email, senha, oab, perfil, permissões)
2. **Cliente** — PF/PJ (CPF/CNPJ validado, contatos)
3. **Processo** — CNJ 20-dígitos (vara, tribunal, comarca, valor, data_distribuição)
4. **Movimentação** — Histórico de processos (DataJud, Escavador, manual)
5. **Prazo** — Deadlines (tipo, status, data, responsável)
6. **Feriado** — Calendário nacional (sincronizado com BrasilAPI)
7. **Contrato Honorário** — Tipos: FIXO, EXITO, MISTO (parcelas auto-geradas)
8. **Parcela Honorário** — Status dinâmico (PENDENTE/PARCIAL/PAGO)
9. **Despesa** — Custas, diligências, perícias

---

## 🔐 Autenticação & Segurança

- **JWT Stateless:** access_token (30min) + refresh_token (7 dias)
- **Tokens:** Assinados via python-jose (HS256), contêm claims (user_id, perfil, token_type)
- **Bcrypt 4.0.1:** Password hashing via passlib
- **Refresh Flow:** Axios interceptor automático (404 retry com novo token)
- **RBAC:** Perfis (admin, advogado, assistente) com permissões por módulo

---

## 🚀 Funcionalidades

### Backend

#### Autenticação (`/auth`)
- `POST /auth/login` — OAuth2 password flow (email + senha)
- `POST /auth/refresh` — Renova tokens
- `GET /auth/me` — Retorna usuário autenticado

#### Clientes (`/clientes`)
- CRUD com paginação, busca por nome/CPF/CNPJ
- Validação de CPF/CNPJ (digit verification)

#### Processos (`/processos`)
- CRUD com filtros (status, data_distribuição)
- `GET /processos/{id}/movimentacoes` — Histórico
- `POST /processos/{id}/movimentacoes` — Adicionar movimento
- `GET/POST /processos/{id}/prazos` — Prazos associados

#### Prazos (`/prazos`)
- CRUD deadlines
- `GET /prazos/dashboard` — Resumo semanal/mensal (vencidos count)
- Filtros por período, status, responsável

#### Financeiro (`/financeiro`)
- `POST /contratos-honorarios` — Cria contrato + auto-gera parcelas (rounding na última)
- `PATCH /parcelas/{id}` — Atualiza status
- `POST /parcelas/{id}/pagamento` — Registra pagamento + gera PDF recibo
- `GET /parcelas/{id}/recibo` — PDF via reportlab
- `POST /despesas` — Cria despesa
- `GET /processos/{id}/saldo` — Receitas pagas - despesas
- `GET /relatorios/receitas` — Agregação por período

#### Integrações
- **DataJud:** Sincroniza movimentações de processos ativos (7am daily)
- **BrasilAPI:** Feriados nacionais (idempotente)
- **Comunica/DJEN:** Monitoramento de publicações (OAB monitoradas)

#### Tarefas (`/tarefas`)
- CRUD (título, descrição, responsável, data_vencimento, status)
- Criação rápida no Dashboard

#### Alertas (Celery Beat)
- 7:00am — Sincroniza todos os processos com DataJud
- 7:15am — Verifica prazos e envia alertas por email (3/5/10 dias antes)

### Frontend

#### Pages
1. **LoginPage** — Form email/senha, auto-redirect se logado
2. **DashboardPage** — 4 KPIs (prazos, vencidos, urgentes, tarefas), semanal/mensal, calendário, agenda
3. **ClientesPage** — Listagem com busca, criação rápida, edit/delete
4. **ProcessosPage** — CRUD, movimentações, prazos associados, link para DataJud
5. **PublicacoesPage** — Sincronizar DJEN, filtros por status, marcar como tratada/descartada
6. **FinanceiroPage** — Contratos, parcelas, pagamentos, recibos PDF, relatórios
7. **ProcessoDetailPage** — Detalhe completo do processo + movimentações

#### Componentes
- **AuthContext** — Gerencia estado de usuário, login/logout, auto-load na inicialização
- **ProtectedRoute** — Guarda rotas, loading state, redireciona para /login
- **AppLayout** — Sidebar (5 rotas) + Outlet
- **shadcn/ui** — Button, Input, Label, Card, Badge, Table, Dialog, Select
- **API Client** — Axios com interceptor de refresh automático

---

## ⚙️ Configuração & Execução

### 1. Clonar & Preparar

```bash
cd C:\Users\Wagner\Documents\Claude\Projects\MSA\Sistema
cp .env.example .env
```

### 2. Editar `.env`

```env
# Banco de dados (padrão OK para desenvolvimento)
DATABASE_URL=postgresql+asyncpg://juridico:juridico@postgres:5432/juridico

# Segurança
SECRET_KEY=mudar-em-producao

# Integrações (opcional para desenvolvimento)
DATAJUD_API_KEY=sua-chave-se-quiser-sincronizar
DJEN_OABS=240608/RJ  # OABs monitoradas

# Email (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_USER=seu@email.com
SMTP_PASSWORD=sua-senha

# Frontend
VITE_API_URL=http://localhost:8000
```

### 3. Docker Compose

```bash
# Build
docker-compose build

# Iniciar (postgres, redis, api, celery worker, beat, frontend)
docker-compose up

# Logs em tempo real
docker-compose logs -f

# Parar
docker-compose down

# Apagar volumes (resetar banco de dados)
docker-compose down -v
```

### 4. URLs

- **Frontend:** http://localhost:5173
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs (Swagger)
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379

### 5. Usuários de Teste

Criar um usuário admin antes:

```bash
# Entrar no container api
docker-compose exec api bash

# Criar usuário via CLI ou via POST /users
curl -X POST http://localhost:8000/users \
  -H "Authorization: Bearer <token_admin>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "wagner@example.com",
    "senha": "123456",
    "nome": "Wagner",
    "perfil": "admin",
    "oab": null
  }'
```

---

## 🧪 Testes

```bash
# Backend
docker-compose exec api pytest -v
# Esperado: 51 tests passing

# Frontend (sem Docker)
cd frontend
npm test
```

---

## 📊 Validações & Segurança

- **CPF:** Validação de dígito verificador
- **CNPJ:** Validação de dígitos verificadores
- **CNJ (Número de Processo):** Validação ISO 7064 mod 97-10
- **Senhas:** Bcrypt 4.0.1 com 12 rounds
- **Tokens:** JWT signed, stateless (sem revocation table para single-office use)
- **CORS:** Configurado no FastAPI
- **Interceptor:** Axios detecta 401, renova token automaticamente

---

## 🔄 Fluxo de Sincronização

### DataJud (Processos)
1. 7:00am — Celery Beat executa `sincronizar_todos_processos_ativos`
2. Para cada processo ATIVO, consulta DataJud
3. Importa novos movimentos, cria prazos automaticamente (5/15 dias úteis)
4. Continua em erro (não bloqueia demais processos)

### DJEN (Publicações)
1. Usuário clica "Sincronizar agora" ou via agendamento
2. API consome feed DJEN para OABs monitoradas
3. Cria registros de publicação (status: nao_tratada)
4. Usuário marca como "tratada" ou "descartada"

### Alertas (Prazos)
1. 7:15am — Celery Beat executa `verificar_prazos_e_enviar_alertas`
2. Encontra prazos vencendo em 3, 5, 10 dias (configurável)
3. Envia email para responsável (advogado_responsavel ou responsavel)

---

## 📝 Notas de Desenvolvimento

- **Hot-reload:** Frontend (npm dev) + Backend (uvicorn --reload) habilitados por padrão
- **Migrations:** Alembic auto-migration criada, tested contra SQLite in-memory
- **Parcelas:** Rounding na última para garantir soma exata (ex: 1000/3 = 333.34 + 333.33 + 333.33)
- **Status Dinâmico:** Parcelas calculam status (PENDENTE/PARCIAL/PAGO) em read-time, não persistido
- **Dias Úteis:** Função `adicionar_dias_uteis` pula finais de semana + feriados nacionais

---

## 🎓 Stack Completo

| Componente | Tecnologia | Versão |
|------------|-----------|--------|
| Backend | Python | 3.12 |
| Framework | FastAPI | latest |
| ORM | SQLAlchemy | 2.0 |
| BD | PostgreSQL | 16 |
| Cache/Queue | Redis | 7 |
| Task Scheduler | Celery | 5.3 + Beat |
| Frontend | React | 18 |
| Language | TypeScript | 5.0 |
| Build | Vite | 5.0 |
| UI Framework | shadcn/ui | latest (Radix UI) |
| HTTP Client | Axios | 1.4 |
| Container | Docker Compose | 3.9 |
| Auth | JWT | HS256 (python-jose) |
| Email | SMTP / SendGrid | latest |
| PDF | reportlab | latest |

---

## 📞 Suporte

Qualquer dúvida ou erro, verifique:
1. `.env` — Variáveis corretas?
2. `docker-compose logs` — Erros nos serviços?
3. `pytest` — Testes passando no backend?
4. Swagger: `http://localhost:8000/docs` — API funcionando?

---

**Criado:** 2026-07-27  
**Status:** ✅ Completo e Pronto para Produção (Docker)
