# 🚀 Quick Start - Sistema Jurídico

## Pré-requisitos
- Docker & Docker Compose instalados
- Windows 10+ (WSL2 recomendado para melhor performance)

## ⚡ 5 Passos para Iniciar

### 1️⃣ Clonar o arquivo .env

```powershell
cd "C:\Users\Wagner\Documents\Claude\Projects\MSA\Sistema"
Copy-Item .env.example .env
```

### 2️⃣ (Opcional) Editar .env para suas integrações

```env
# Já está configurado para desenvolvimento local
DATAJUD_API_KEY=sua-chave-se-tiver
DJEN_OABS=240608/RJ
SMTP_HOST=smtp.gmail.com
SMTP_USER=seu@email.com
SMTP_PASSWORD=sua-senha
```

### 3️⃣ Build Docker Compose

```powershell
docker-compose build
```

### 4️⃣ Iniciar todos os serviços

```powershell
docker-compose up
```

Esperado:
```
postgres_1     | database system is ready to accept connections
redis_1        | Ready to accept connections
api_1          | Uvicorn running on http://0.0.0.0:8000
frontend_1     | VITE v5.0.0 ready in XXX ms
```

### 5️⃣ Acessar

| O quê | URL |
|------|-----|
| **Sistema** | http://localhost:5173 |
| **API Docs** | http://localhost:8000/docs |

---

## 📝 Primeiro Login

Use as credenciais de um usuário já criado:

```
Email: wagner@example.com
Senha: (a que foi criada no backend)
```

Se não tiver usuário:
```bash
# Entrar no container api
docker-compose exec api bash

# Criar usuário via CLI (usar POST /users com token admin)
```

---

## 🛑 Parar os serviços

```powershell
docker-compose down
```

---

## 📊 Logs em Tempo Real

```powershell
# Todos os serviços
docker-compose logs -f

# Apenas um serviço
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f postgres
```

---

## 🔄 Resetar Banco de Dados

```powershell
# Parar tudo e remover volumes
docker-compose down -v

# Reconstruir e reiniciar
docker-compose up --build
```

---

## ✅ Checklist de Funcionalidades

- [ ] Login com email/senha
- [ ] Ver Dashboard com KPIs (prazos, vencidos, urgentes, tarefas)
- [ ] Criar novo cliente
- [ ] Criar novo processo (CNJ)
- [ ] Sincronizar processo com DataJud
- [ ] Criar prazo manualmente
- [ ] Criar contrato honorário e ver parcelas geradas
- [ ] Sincronizar publicações DJEN
- [ ] Marcar publicação como tratada/descartada
- [ ] Ver relatório de receitas/despesas

---

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| "docker-compose: command not found" | Instalar Docker Desktop |
| "Address already in use :5173" | Porta 5173 ocupada. Mudar em docker-compose.yml |
| "Connection refused (postgres)" | Esperar 10s, postgres leva tempo pra iniciar |
| "401 Unauthorized" | Token expirou. Fazer login novamente |
| "E-mail inválido" | Validar formato e dados do .env |

---

## 📞 Suporte Rápido

Qualquer erro, verificar logs:
```powershell
docker-compose logs -f api
```

Se erro de banco de dados, resetar:
```powershell
docker-compose down -v
docker-compose up --build
```

---

**Pronto! Sistema deve estar rodando.** 🎉
