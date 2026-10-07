"""
LAB 5 (parte B) · L6 — ORQUESTRADOR QUE DELEGA VIA A2A
======================================================
Slide 17 (como tudo se encaixa) e slide 25, Gancho 3: o orquestrador consome o
agente remoto via RemoteA2aAgent — como se fosse um sub-agente local.

PRÉ-REQUISITO: o lab5_a2a_servidor.py precisa estar RODANDO no outro terminal.
    python lab5_a2a_orquestrador.py

Mensagem em sala: integração HORIZONTAL — um agente delega a OUTRO agente,
possivelmente de outro time/fornecedor, sem saber como ele funciona por dentro.
"""
from comum import MODELO, exigir_chave, perguntar
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

exigir_chave()

# Descobre o agente remoto pelo seu agent card (publicado pela parte A).
especialista_planos = RemoteA2aAgent(
    name="especialista_planos",
    description="Especialista remoto em planos e preços (via A2A).",
    agent_card="http://localhost:8001/.well-known/agent-card.json",
)

# O orquestrador delega para o especialista como se fosse local (sub_agents).
orquestrador = LlmAgent(
    model=MODELO,
    name="orquestrador_atendimento",
    instruction=(
        "Você é o atendente principal da TechNova. Quando a pergunta envolver "
        "preço, plano ou SLA, DELEGUE ao especialista_planos. "
        "Para o resto, responda você mesmo. Responda em português."
    ),
    sub_agents=[especialista_planos],
)

if __name__ == "__main__":
    print("=" * 60)
    print("LAB 5B — Orquestrador delegando via A2A")
    print("(Confirme que lab5_a2a_servidor.py está rodando na porta 8001!)")
    print("=" * 60)
    perguntar(orquestrador, "Bom dia! Qual a diferença de preço e SLA entre Business e Enterprise?")
    perguntar(orquestrador, "Obrigado! Vocês atendem em português?")
    print(">> A 1a pergunta foi roteada ao especialista REMOTO; a 2a o orquestrador resolveu.")
    print(">> Isso é A2A: descobrir -> delegar -> agregar (slide 15).")
