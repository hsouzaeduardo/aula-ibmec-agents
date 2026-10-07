# Labs práticos: a escada GenAI (RAG → Agentes → MCP → A2A)

Trilha progressiva de **scripts prontos para demonstrar em sala**. Cada lab sobe um degrau do
**modelo de maturidade GenAI** do deck e roda com **Google ADK + Gemini**.

Cenário único em todos os labs: **TechNova**, uma empresa que está construindo um assistente
interno. A cada lab o mesmo assistente ganha uma capacidade arquitetural nova.

| Lab | Nível | O que demonstra | Arquivo |
|-----|-------|-----------------|---------|
| 0 | L0 · Dados | Preparar e "chunkar" a base de conhecimento (governança) | `lab0_dados.py` |
| 1 | L1 · Prompt/Serve | Agente + ferramenta (function calling) | `lab1_agente_tool.py` |
| 2 | L2/L4 · RAG + Grounding | Recuperação como ferramenta, resposta com **citações** | `lab2_rag_grounding.py` |
| 3 | L5 · Agente único | Loop ReAct com **várias** ferramentas | `lab3_agente_unico.py` |
| 3.5 | Harness | O **runtime** que executa o agente: harness na mão vs. Runner do ADK | `lab3b_harness.py` |
| 4 | L5 · MCP | Conectar o agente a um **servidor MCP** | `lab4_mcp.py` |
| 5 | L6 · Multi-agente | **A2A**: orquestrador delega a agentes remotos | `lab5_a2a_servidor.py` + `lab5_a2a_orquestrador.py` |
| 6 | Capstone | Tudo junto: RAG + tools + sub-agentes | `lab6_capstone.py` |

> L3 (fine-tuning) é discutido conceitualmente no guia do instrutor — não é demonstrável ao vivo
> sem treino dedicado; o lab 2 cobre o degrau seguinte (L4 · Grounding), que é o que realmente
> aparece em produção.

---

## Setup (uma vez)

```bash
# 1. Ambiente Python 3.10+
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# 2. Dependências
pip install -r requirements.txt

# 3. Chave do Gemini (pegue em https://aistudio.google.com/apikey)
#    Edite o arquivo .env e troque "cole-sua-chave-aqui" pela sua chave
#    (se não existir, copie de .env.example). Os labs leem o .env sozinhos.

# 4. Verifique tudo
python 00_setup_check.py
```

**Rodar todos os labs de uma vez** (salva as saídas em `outputs/`):

```powershell
powershell -ExecutionPolicy Bypass -File .\executar_labs.ps1
```

Todos os comandos, lab a lab, estão em **`COMANDOS_EXECUCAO.md`**.

O lab 4 (MCP) usa um servidor MCP de filesystem via `npx`, então precisa de **Node.js** instalado.
Os demais labs precisam só de Python + a chave do Gemini.

---

## Como conduzir em sala

1. **Abra com o lab 0** para mostrar que tudo começa nos dados (L0). É rápido e tira o "RAG é mágica" da cabeça da turma.
2. **Rode um lab por degrau**, sempre fazendo a mesma pergunta de negócio e mostrando o que o assistente *passa a conseguir fazer*.
3. Cada script imprime no console **o que está acontecendo em cada etapa** (recuperação, decisão de ferramenta, delegação) — pause e comente.
4. O **capstone** fecha a aula: o mesmo assistente agora recupera conhecimento, age e delega.

Pontos de fala, saída esperada e erros comuns de cada lab estão em **`GUIA_INSTRUTOR.md`**.

---

## Regra de ouro (slide 20)

> Comece no nível mais simples que resolve o problema; suba na escada só quando a dor justificar a complexidade.
