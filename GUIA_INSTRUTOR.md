# Guia do instrutor — Labs Aula 2

Roteiro para conduzir os labs ao vivo. Cada lab tem: **objetivo**, **o que falar**,
**saída esperada** e **erros comuns**. Tempo total sugerido: ~90 min.

---

## Antes da aula
- Rode `python 00_setup_check.py` na máquina de apresentação.
- Deixe a `GOOGLE_API_KEY` já exportada no ambiente.
- Para o lab 4 (MCP), confirme que `npx` responde (`npx --version`).
- Abra dois terminais — você vai precisar deles no lab 5.

---

## Lab 0 — Dados (L0) · ~5 min
**Objetivo:** mostrar que RAG começa em dado preparado, não em mágica.
**Fale:** "Antes de qualquer modelo, alguém limpa e fatia (chunk) o conhecimento.
Cada chunk guarda a FONTE — é isso que vai permitir citar lá no RAG."
**Saída esperada:** lista de ~9 chunks com id, seção e tamanho.
**Erro comum:** rodar fora da pasta `Labs_Aula2` (não acha `dados/`). Rode de dentro da pasta.

## Lab 1 — Agente + ferramenta (L1) · ~10 min
**Objetivo:** function calling — o modelo decide chamar código.
**Fale:** "A docstring + type hints viram o schema. Não escrevi schema nenhum.
Veja a linha `[tool] ->`: foi o agente decidindo chamar a função."
**Saída esperada:** chama `consultar_estoque` nas 2 primeiras perguntas; na 3ª (capital
da França) responde **sem** ferramenta.
**Erro comum:** `GOOGLE_API_KEY` ausente → o script avisa e encerra.

## Lab 2 — RAG com grounding (L2/L4) · ~12 min
**Objetivo:** acabar com a alucinação respondendo com fonte.
**Fale:** "A recuperação virou uma ferramenta. O agente busca, e só responde com
base nos trechos — e cita `[fonte#id]`. Na pergunta sobre 'Marte', sem fonte, ele recusa."
**Saída esperada:** respostas com citação entre colchetes; recusa educada na última.
**Erro comum:** modelo às vezes parafraseia a citação — reforce na instrução se quiser rigor.

## Lab 3 — Agente único, ReAct (L5) · ~12 min
**Objetivo:** um agente, várias ferramentas, decidindo a sequência.
**Fale:** "Pergunta composta: ele encadeia RAG + estoque. Na falha de produção, ele
DECIDE abrir um chamado severidade 1. Esse encadeamento é o loop Pensar→Agir→Observar."
**Saída esperada:** múltiplas linhas `[tool] ->` numa mesma pergunta; um chamado aberto.

## Lab 3.5 — O Harness · ~12 min
**Objetivo:** nomear e mostrar o *runtime* que executa o agente — o elo entre o loop
ReAct (slide 9) e o ADK (slide 22). Veja também o slide novo "AGENTES · HARNESS".
**Conceitos na lousa:**
- *Scaffolding* = código que MONTA o agente antes do 1º passo (instrução, tools, schema). Build-time.
- *Harness* = runtime que roda DEPOIS: loop, despacho de tools, contexto/estado, limites e erros. Run-time.
**Fale:** "Na Parte 1 escrevemos o loop NA MÃO: o modelo decide, nós executamos a tool,
realimentamos o resultado e repetimos — controlando até o teto de passos. Na Parte 2, o
`Runner` do ADK faz tudo isso. É o mesmo loop; muda quem escreve o encanamento."
**Saída esperada:** Parte 1 imprime `[harness] passo N: executando ...` a cada iteração;
Parte 2 chega à mesma resposta via ADK.
**Erro comum:** sem `GOOGLE_API_KEY` o script encerra avisando.
**Gancho de discussão:** "harness engineering" — o código ao redor do modelo pesa tanto
quanto o próprio modelo na qualidade do agente.

## Lab 4 — MCP · ~12 min
**Objetivo:** o agente ganha ferramentas de um servidor externo padronizado.
**Fale:** "Não escrevi nenhuma tool de arquivo. Elas vieram do servidor MCP, descobertas
em runtime. Trocar por um servidor de banco ou API reusa o mesmo padrão: é o M+N do slide 13."
**Saída esperada:** lista os arquivos de `dados/` e resume `produtos.md`.
**Erros comuns:**
- Sem Node.js → `npx` falha. Instale Node ou pule este lab (tem fallback no guia abaixo).
- 1ª execução baixa o servidor e demora; avise a turma.

## Lab 5 — A2A (L6) · ~15 min · **dois terminais**
**Objetivo:** um agente delega a OUTRO agente pela rede.
**Passos:**
1. Terminal 1: `python lab5_a2a_servidor.py` (sobe o especialista na porta 8001).
2. Terminal 2: `python lab5_a2a_orquestrador.py`.
**Fale:** "O orquestrador descobre o especialista pelo agent card e delega como se fosse
local. Ele não sabe como o outro funciona por dentro — integração horizontal."
**Saída esperada:** 1ª pergunta (preço/SLA) é roteada ao especialista remoto; 2ª o
orquestrador responde sozinho.
**Erros comuns:**
- Orquestrador antes do servidor → erro de conexão. Suba o servidor primeiro.
- Porta 8001 ocupada → troque a porta nos dois arquivos.

## Lab 6 — Capstone · ~10 min
**Objetivo:** fechar a escada num só runtime: RAG + tools + multi-agente.
**Fale:** "O orquestrador delega para o agente de conhecimento (RAG) e o de operações
(ações). É o slide 17 rodando. Em produção, qualquer sub-agente poderia ser remoto via A2A."
**Saída esperada:** resposta composta com citação + estoque; depois abre chamado urgente.

---

## Sobre o L3 (fine-tuning)
Não há lab executável: fine-tuning exige um job de treino dedicado (PEFT/LoRA), tempo e
dados rotulados — inviável ao vivo. Discuta como conceito: "especializa o modelo quando
prompt + RAG não bastam". O degrau seguinte e mais usado em produção é o **L4 · Grounding**,
coberto no lab 2.

## Plano B sem Node (lab 4)
Se a turma não tiver Node, descreva o MCP com o diagrama do slide 12 e mostre o código do
`lab4_mcp.py` na tela, rodando o lab 3 (que já usa tools locais) como prova de "agente + ferramentas".

## Decisão de arquitetura (encerramento — slide 20)
Feche perguntando à turma, para cada caso do slide 19, qual degrau usariam: RAG, agente
único ou multi-agente. Regra de ouro: comece simples; suba só quando a dor justificar.
