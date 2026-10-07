# Comandos de execução — Labs Aula 2

Todos os comandos são rodados **de dentro da pasta `Labs_Aula2`** (PowerShell no Windows).

---

## 1. Setup (uma vez)

```powershell
# Ambiente virtual + dependências
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Chave do Gemini: edite o arquivo .env e troque "cole-sua-chave-aqui" pela sua chave
#   (pegue em https://aistudio.google.com/apikey)
notepad .env

# Verificação
python 00_setup_check.py
```

> O `.env` é carregado automaticamente por `comum.py` — não precisa de `setx`.
> Se `Activate.ps1` for bloqueado: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

---

## 2. Rodar TUDO de uma vez (recomendado para validar antes da aula)

```powershell
powershell -ExecutionPolicy Bypass -File .\executar_labs.ps1
```

- Faz o setup se o `.venv` não existir, roda o `00_setup_check.py` e todos os labs em sequência.
- No lab 5 sobe o servidor A2A sozinho em segundo plano, roda o orquestrador e derruba o servidor.
- Grava a saída de cada lab em `outputs\<lab>.txt` e um quadro final em `outputs\RESUMO.txt`.

Variações:

```powershell
.\executar_labs.ps1 -Labs 0,1,2      # só alguns labs (0 1 2 3 3b 4 5 6)
.\executar_labs.ps1 -SoSetup         # só cria o .venv, instala e verifica
```

---

## 3. Rodar lab a lab (ao vivo em sala)

Com o `.venv` ativado (`.\.venv\Scripts\Activate.ps1`):

| Lab | Comando | Precisa de chave? |
|-----|---------|-------------------|
| Setup | `python 00_setup_check.py` | — |
| 0 · Dados | `python lab0_dados.py` | não |
| 1 · Agente + tool | `python lab1_agente_tool.py` | sim |
| 2 · RAG + grounding | `python lab2_rag_grounding.py` | sim |
| 3 · Agente único | `python lab3_agente_unico.py` | sim |
| 3.5 · Harness | `python lab3b_harness.py` | sim |
| 4 · MCP | `python lab4_mcp.py` | sim (+ Node.js) |
| 5 · A2A | **2 terminais**, veja abaixo | sim |
| 6 · Capstone | `python lab6_capstone.py` | sim |

### Lab 5 — dois terminais

```powershell
# Terminal 1 (deixe aberto)
.\.venv\Scripts\Activate.ps1
python lab5_a2a_servidor.py
# confira: http://localhost:8001/.well-known/agent-card.json

# Terminal 2
.\.venv\Scripts\Activate.ps1
python lab5_a2a_orquestrador.py
```

### Lab 4 — pré-aquecer o servidor MCP (evita espera na 1ª execução)

```powershell
npx -y @modelcontextprotocol/server-filesystem .\dados
# quando aparecer "Secure MCP Filesystem Server running on stdio", Ctrl+C
```

---

## 4. Problemas resolvidos nesta validação (06/10/2026)

| Problema | Causa | Correção |
|---|---|---|
| `ImportError: DLL load failed while importing win32api` ao importar `google.adk` | `pywintypes312.dll` antigo na raiz do Python 3.12 sobrepondo o DLL do pywin32 | Renomeado para `pywintypes312.dll.bak_stale` em `%LOCALAPPDATA%\Programs\Python\Python312\` |
| `No module named 'mcp'` / `'a2a'` | ADK 2.x não instala mais MCP e A2A por padrão | `requirements.txt` → `google-adk[a2a]`, `mcp`, `python-dotenv` |
| Lab 4: `timed out after 5.0s waiting for the session` | 1ª execução do `npx` baixa o servidor; timeout padrão é 5s | `timeout=60` em `StdioConnectionParams` (`lab4_mcp.py`) |
| Chave só via `setx` | — | `.env` + `load_dotenv` em `comum.py` e `00_setup_check.py` |

Para desfazer a correção do DLL (se algum outro programa reclamar):
```powershell
Rename-Item "$env:LOCALAPPDATA\Programs\Python\Python312\pywintypes312.dll.bak_stale" pywintypes312.dll
```
