"""
LAB 5 (parte A) · L6 — EXPOR UM AGENTE VIA A2A
==============================================
Slide 15 e slide 25, Gancho 3: to_a2a() expõe um agente como serviço e gera o
'agent card' sozinho. Outro agente o consumirá pela rede (ver parte B).

Este script sobe um AGENTE ESPECIALISTA em planos/preços da TechNova na porta 8001.

COMO RODAR (terminal 1 — deixe aberto):
    python lab5_a2a_servidor.py
Depois, em outro terminal, rode o orquestrador:
    python lab5_a2a_orquestrador.py

O agent card fica em: http://localhost:8001/.well-known/agent-card.json
"""
from comum import MODELO, exigir_chave
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

exigir_chave()


def cotar_plano(plano: str) -> dict:
    """Retorna preço e SLA de um plano do TechNova Cloud.

    Args:
        plano: 'starter', 'business' ou 'enterprise'.
    """
    tabela = {
        "starter": {"preco": "R$ 99/mês", "usuarios": 5, "sla": "24h"},
        "business": {"preco": "R$ 299/mês", "usuarios": 25, "sla": "8h"},
        "enterprise": {"preco": "sob consulta", "usuarios": "ilimitado", "sla": "1h"},
    }
    return tabela.get(plano.lower(), {"erro": "plano desconhecido"})


especialista_planos = LlmAgent(
    model=MODELO,
    name="especialista_planos",
    description="Especialista em planos, preços e SLA do TechNova Cloud.",
    instruction=(
        "Você é o especialista comercial da TechNova. Use cotar_plano para "
        "informar preço, número de usuários e SLA. Responda em português, curto."
    ),
    tools=[cotar_plano],
)

# to_a2a() embrulha o agente como app ASGI e gera o agent card automaticamente.
a2a_app = to_a2a(especialista_planos, port=8001)

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("LAB 5A — Especialista de planos exposto via A2A na porta 8001")
    print("Agent card: http://localhost:8001/.well-known/agent-card.json")
    print("Deixe este terminal aberto e rode lab5_a2a_orquestrador.py no outro.")
    print("=" * 60)
    uvicorn.run(a2a_app, host="localhost", port=8001)
