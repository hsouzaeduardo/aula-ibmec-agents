"""
LAB 1 · L1 — AGENTE + FERRAMENTA (function calling)
===================================================
Slide 23, Gancho 1: "Uma função Python comum vira uma ferramenta do agente:
a docstring e os type hints geram o schema automaticamente."

Mensagem em sala: o modelo deixa de só "falar" e passa a DECIDIR chamar código.
Compare com a Aula 1 (modelo puro): aqui ele consulta um sistema real.

    python lab1_agente_tool.py
"""
from comum import MODELO, exigir_chave, perguntar
from google.adk.agents import LlmAgent

exigir_chave()

# --- "Banco de dados" de estoque fake (slide 23) -------------------------
_ESTOQUE = {"NB-14": 12, "MON-27": 0, "DOCK-USB": 47}


def consultar_estoque(sku: str) -> dict:
    """Retorna a quantidade em estoque de um SKU.

    Args:
        sku: código do produto, ex. 'NB-14'.
    """
    qtd = _ESTOQUE.get(sku.upper())
    if qtd is None:
        return {"sku": sku, "erro": "SKU não encontrado"}
    return {"sku": sku.upper(), "qtd": qtd, "disponivel": qtd > 0}


# O agente: note que NÃO escrevemos schema nenhum — o ADK gera da função.
agente = LlmAgent(
    model=MODELO,
    name="assistente_estoque",
    instruction=(
        "Você ajuda a consultar o estoque da TechNova. "
        "Use a ferramenta consultar_estoque sempre que perguntarem sobre disponibilidade. "
        "Responda em português, de forma curta e objetiva."
    ),
    tools=[consultar_estoque],
)

if __name__ == "__main__":
    print("=" * 60)
    print("LAB 1 — Agente + ferramenta (function calling)")
    print("=" * 60)
    # Observe no console a linha [tool] -> mostrando o agente DECIDINDO chamar a função.
    perguntar(agente, "Temos o notebook NB-14 em estoque?")
    perguntar(agente, "E o monitor MON-27, posso vender?")
    perguntar(agente, "Qual a capital da França?")  # ele NÃO chama a tool — bom contraste
    print(">> Repare: na 3a pergunta o agente respondeu sem ferramenta.")
    print(">> Ele só aciona a tool quando a tarefa exige dado do sistema.")
