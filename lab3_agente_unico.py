"""
LAB 3 · L5 — AGENTE ÚNICO (loop ReAct com várias ferramentas)
=============================================================
Slides 8-10: do conhecimento à ação; anatomia do agente; loop Pensar->Agir->
Observar->Refletir. Slide 19: caso "suporte ao cliente" e "empréstimo".

Mensagem em sala: um só agente, várias ferramentas, decidindo a SEQUÊNCIA sozinho.
Faça a pergunta composta e mostre no console o encadeamento de [tool] -> ...

    python lab3_agente_unico.py
"""
from comum import MODELO, exigir_chave, perguntar
from google.adk.agents import LlmAgent
from lab2_rag_grounding import buscar_conhecimento  # reusa o RAG do lab 2

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
    """Abre um chamado de suporte e devolve o número do protocolo.

    Args:
        titulo: resumo do problema.
        severidade: '1' (crítico) a '4' (baixo).
    """
    numero = f"TN-{1000 + len(_CHAMADOS)}"
    _CHAMADOS[numero] = {"titulo": titulo, "severidade": severidade, "status": "aberto"}
    return {"protocolo": numero, "status": "aberto"}


# Um agente, três ferramentas: conhecimento (RAG) + estoque + ação (chamado).
agente = LlmAgent(
    model=MODELO,
    name="agente_suporte",
    instruction=(
        "Você é o agente de suporte da TechNova. Raciocine passo a passo:\n"
        "1) Use buscar_conhecimento para questões de política/produto (cite a fonte).\n"
        "2) Use consultar_estoque para disponibilidade de itens.\n"
        "3) Se o cliente relatar uma falha crítica de produção, abra um chamado "
        "(abrir_chamado, severidade '1') e informe o protocolo.\n"
        "Responda em português, de forma objetiva."
    ),
    tools=[buscar_conhecimento, consultar_estoque, abrir_chamado],
)

if __name__ == "__main__":
    print("=" * 60)
    print("LAB 3 — Agente único (ReAct, múltiplas ferramentas)")
    print("=" * 60)
    # Pergunta composta: força o agente a encadear RAG + estoque numa só tarefa.
    perguntar(
        agente,
        "Quero contratar o plano Business: quanto custa e qual o SLA de suporte? "
        "Aproveite e veja se o dock DOCK-USB está disponível.",
    )
    # Aqui ele deve DECIDIR abrir um chamado severidade 1.
    perguntar(
        agente,
        "Nossa produção caiu, o TechNova Cloud está fora do ar e ninguém acessa. Socorro!",
    )
    print(">> Veja a sequência de [tool] -> no console: é o loop ReAct em ação.")
    print(f">> Chamados abertos nesta sessão: {_CHAMADOS}")
