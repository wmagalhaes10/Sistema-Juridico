# 🐳 Docker Troubleshooting

## Problemas Comuns & Soluções

### 1. **"Read-only file system" ao fazer build**

**Causa:** Cache Docker corrompido (geralmente após resetar Docker no WSL2)

**Solução:**

```powershell
# Opção 1: Limpar cache e rebuildar
docker system prune -f
docker-compose build

# Opção 2: Se ainda falhar, limpar tudo
docker system prune -af  # Remove TODAS as imagens
docker-compose build     # Reconstruir do zero
```

---

### 2. **"Address already in use :5173" ou :8000**

**Causa:** Porta já está em uso (outro processo ou container antigo)

**Solução:**

```powershell
# Listar containers rodando
docker ps

# Parar tudo
docker-compose down

# Ou matar processo específico (Windows)
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

---

### 3. **"Connection refused" ao acessar http://localhost:5173**

**Causa:** Frontend container não iniciou ou ainda está building

**Solução:**

```powershell
# Verificar logs
docker-compose logs frontend

# Aguardar ~30s para build completar
# Se error persiste, resetar:
docker-compose down -v
docker-compose up --build
```

---

### 4. **PostgreSQL recusa conexão**

**Causa:** Banco de dados ainda não iniciou (demora 10-15s)

**Solução:**

```powershell
# Aguardar healthcheck passar
docker-compose up postgres

# Verificar status
docker-compose ps

# Se postgres estiver "unhealthy", resetar volume:
docker-compose down -v
docker-compose up postgres
```

---

### 5. **"ModuleNotFoundError" no backend**

**Causa:** requirements.txt não foi instalado ou versão incompatível

**Solução:**

```powershell
# Forçar rebuild do container api
docker-compose down
docker-compose build --no-cache api
docker-compose up api
```

**Versão crítica:** bcrypt==4.0.1 (deve estar em requirements.txt)

---

### 6. **"VITE API URL not found"**

**Causa:** Variável .env não foi carregada no frontend

**Solução:**

```bash
# Verificar .env existe
cat .env | grep VITE_API_URL

# Deve conter:
# VITE_API_URL=http://localhost:8000

# Se .env novo, atualizar e rebuildar
docker-compose down
docker-compose build --no-cache frontend
docker-compose up frontend
```

---

### 7. **Email não envia no desenvolvimento**

**Causa:** SMTP não configurado ou credenciais inválidas

**Solução:**

```env
# Usar Gmail (mais simples para dev)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu@gmail.com
SMTP_PASSWORD=sua-senha-app-google  # Não use senha normal do Gmail!
SMTP_FROM=seu@gmail.com
```

Para Gmail:
1. Ativar "App Passwords" em https://myaccount.google.com/apppasswords
2. Gerar senha de app
3. Colar em SMTP_PASSWORD

Se não quiser email no dev, deixar vazio (logs apenas)

---

### 8. **Celery Beat não está agendando tarefas**

**Causa:** Redis ou Celery Beat container não iniciou

**Solução:**

```powershell
# Verificar logs do celery-beat
docker-compose logs celery-beat

# Verificar redis
docker-compose logs redis

# Resetar:
docker-compose down
docker-compose up redis celery-beat -d
```

---

### 9. **Frontend fica "loading" infinitamente**

**Causa:** Autenticação falhou silenciosamente ou API não responde

**Solução:**

```powershell
# Verificar API está rodando
curl http://localhost:8000/docs

# Verificar logs da API
docker-compose logs api

# Verificar console do browser (F12 > Console)
# Deve mostrar erro HTTP/CORS

# Resetar tudo:
docker-compose down -v
docker-compose up --build
```

---

### 10. **"Port 5432 is in use" (PostgreSQL)**

**Causa:** PostgreSQL local já está rodando ou antigo container não parou

**Solução:**

```powershell
# Parar containers Docker
docker-compose down

# Verificar se PostgreSQL local está rodando
Get-Process | grep postgres

# Matar processo (WSL2)
wsl -d Docker-Desktop ps aux | grep postgres
wsl -d Docker-Desktop kill <PID>

# Reiniciar Docker container
docker-compose up postgres
```

---

## 🧹 Limpeza Completa

Se nada funcionar, fazer reset total:

```powershell
cd "C:\Users\Wagner\Documents\Claude\Projects\MSA\Sistema"

# Parar tudo
docker-compose down

# Remover volumes (banco de dados)
docker-compose down -v

# Remover imagens
docker image rm $(docker images -q sistema_*)

# Limpar cache Docker global
docker system prune -af

# Reconstruir do zero
docker-compose build
docker-compose up
```

---

## ✅ Verificação de Saúde

```powershell
# 1. Containers rodando?
docker-compose ps
# Esperado: 6 containers com status "Up"

# 2. Portas abertas?
netstat -ano | findstr "5173\|8000\|5432\|6379"
# Esperado: 4 linhas (frontend, api, postgres, redis)

# 3. API respondendo?
curl http://localhost:8000/docs
# Esperado: HTML do Swagger UI

# 4. Frontend carregando?
curl http://localhost:5173
# Esperado: HTML da aplicação

# 5. Banco de dados?
docker-compose exec postgres psql -U juridico -d juridico -c "SELECT COUNT(*) FROM \"user\";"
# Esperado: Número de usuários (ou 0 se novo)
```

---

## 📞 Se Nada Funcionar

1. **Reinstalar Docker Desktop**
   - Desinstalar completamente
   - Limpar WSL2 (se usar): `wsl --unregister Docker-Desktop`
   - Reinstalar

2. **Verificar WSL2 (se Windows)**
   - `wsl -l -v` — Confirmar Docker Desktop usa WSL2
   - `wsl --update` — Atualizar WSL2

3. **Contatar suporte com:**
   - Saída de `docker-compose logs` (últimas 50 linhas)
   - Versão do Docker: `docker --version`
   - Versão do Compose: `docker-compose --version`
   - Sistema operacional: `systeminfo | findstr /C:"OS"`

---

**Última atualização:** 2026-07-27
