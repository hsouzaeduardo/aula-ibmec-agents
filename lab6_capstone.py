"""
LAB 6 · CAPSTONE — A ARQUITETURA COMPLETA, PONTA A PONTA
========================================================
Slide 17 ("como tudo se encaixa") e slide 28 (síntese). Fecha a escada de
maturidade num só runtime: RAG (saber) + ferramentas (agir) + multi-agente (coordenar).

Para rodar num só processo (sem 2 terminais), os sub-agentes aqui são LOCAIS.
Em produção, qualquer um deles poderia ser remoto via A2A (lab 5) — a interface é a mesma.

    python lab6_capstone.py
"""
from comum import MODELO, exigir_chave, perguntar
from google.adk.agents import LlmAgent
from lab2_rag_grounding import buscar_conhecimento

exigir_chave()

_CHAMADOS = {}


def consultar_estoque(sku: str) -> dict:
    """Retorna a quantidade em estoque de um SKU.

    Args:
        sku: código do produto, ex. 'NB-14'.
    """
    estoque = {"NB-14": 12, "MON-27": 0, "DOCK-USB": 47}
    qtd = estoque.get(sku.upper())
    if qtd is None:
        return {"sku": sku, "erro": "SKU não encontrado"}
    return {"sku": sku.upper(), "qtd": qtd, "disponivel": qtd > 0}


def abrir_chamado(titulo: str, severidade: str) -> dict:
    """Abre um chamado de suporte e devolve o protocolo.

    Args:
        titulo: resumo do problema.
        severidade: '1' (crítico) a '4' (baixo).
    """
    numero = f"TN-{2000 + len(_CHAMADOS)}"
    _CHAMADOS[numero] = {"titulo": titulo, "severidade": severidade}
    return {"protocolo": numero, "status": "aberto"}


# --- Sub-agente 1: conhecimento (RAG + grounding) -------------------------
agente_conhecimento = LlmAgent(
    model=MODELO,
    name="agente_conhecimento",
    description="Responde sobre políticas, planos e suporte citando a base interna.",
    instruction=(
        "Use buscar_conhecimento e responda só com base nos trechos, "
        "citando a fonte entre colchetes. Não invente."
    ),
    tools=[buscar_conhecimento],
)

# --- Sub-agente 2: operações (ferramentas de ação) ------------------------
agente_operacoes = LlmAgent(
    model=MODELO,
    name="agente_operacoes",
    description="Consulta estoque e abre chamados de suporte.",
    instruction=(
        "Use consultar_estoque para disponibilidade e abrir_chamado para falhas. "
        "Falha crítica de produção = severidade '1'. Responda em português."
    ),
    tools=[consultar_estoque, abrir_chamado],
)

# --- Orquestrador: planeja e delega (slide 17) ----------------------------
orquestrador = LlmAgent(
    model=MODELO,
    name="orquestrador_technova",
    instruction=(
        "Você coordena o atendimento da TechNova. Analise o pedido e delegue:\n"
        "- dúvidas de política/plano/suporte -> agente_conhecimento;\n"
        "- estoque ou abrir chamado -> agente_operacoes.\n"
        "Pedidos compostos podem exigir os dois. Junte as respostas de forma clara, "
        "em português, e preserve as citações de fonte."
    ),
    sub_agents=[agente_conhecimento, agente_operacoes],
)

if __name__ == "__main__":
    print("=" * 60)
    print("LAB 6 — CAPSTONE: RAG + ferramentas + multi-agente")
    print("=" * 60)
    # Pedido composto: conhecimento (RAG) + ação (estoque) numa só conversa.
    perguntar(
        orquestrador,
        "Quero migrar para o plano Business — qual o preço e o SLA? "
        "E veja se há DOCK-USB em estoque para meu time.",
    )
    perguntar(
        orquestrador,
        "O TechNova Cloud caiu em produção agora! Abram um chamado urgente.",
    )
    print(f"\n>> Chamados abertos: {_CHAMADOS}")
    print(">> Cinco ideias do slide 28, vivas: RAG fundamenta, agentes agem,")
    print("   MCP padroniza ferramentas, A2A conecta agentes, ADK amarra tudo.")
