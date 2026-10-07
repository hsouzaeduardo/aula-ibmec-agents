"""
LAB 2 · L2/L4 — RAG COM GROUNDING (recuperar e citar)
=====================================================
Slides 5-7 (o problema e a arquitetura do RAG) e slide 26, Gancho 4
("retrieval vira tool do agente" / nível Grounding).

Para a demo ser leve e sempre rodar, a recuperação é LOCAL sobre a base do lab 0
(em produção seria um Vector DB / VertexAiRagRetrieval — ver bloco comentado no fim).

Mensagem em sala: o agente para de alucinar porque RESPONDE COM FONTE.

    python lab2_rag_grounding.py
"""
from comum import MODELO, exigir_chave, perguntar
from google.adk.agents import LlmAgent
from lab0_dados import construir_indice

exigir_chave()
_INDICE = construir_indice()  # reaproveita o chunking do lab 0


def buscar_conhecimento(consulta: str) -> dict:
    """Recupera trechos da base interna da TechNova relevantes à consulta.

    Use SEMPRE antes de responder perguntas sobre políticas, planos ou suporte.

    Args:
        consulta: o assunto a pesquisar, ex. 'dias de férias'.
    """
    termos = [t for t in consulta.lower().split() if len(t) > 3]
    ranqueados = []
    for chunk in _INDICE:
        texto = chunk["texto"].lower()
        score = sum(texto.count(t) for t in termos)
        if score:
            ranqueados.append((score, chunk))
    ranqueados.sort(key=lambda x: x[0], reverse=True)
    top = ranqueados[:3]  # similarity_top_k = 3 (slide 26)
    return {
        "trechos": [
            {"fonte": c["id"], "secao": c["secao"], "conteudo": c["texto"]}
            for _, c in top
        ],
        "encontrou": bool(top),
    }


agente = LlmAgent(
    model=MODELO,
    name="assistente_rh_rag",
    instruction=(
        "Você é o assistente interno da TechNova. "
        "Para QUALQUER pergunta sobre políticas, planos ou suporte, chame buscar_conhecimento "
        "e responda APENAS com base nos trechos retornados. "
        "Sempre cite a fonte entre colchetes ao fim de cada afirmação, ex.: [politicas_rh.md#0]. "
        "Se a busca não encontrar nada, diga que não há informação na base — NÃO invente."
    ),
    tools=[buscar_conhecimento],
)

if __name__ == "__main__":
    print("=" * 60)
    print("LAB 2 — RAG com grounding (resposta com citações)")
    print("=" * 60)
    perguntar(agente, "Quantos dias de férias eu tenho e com que antecedência peço?")
    perguntar(agente, "Quantos dias por semana posso trabalhar de casa?")
    perguntar(agente, "Qual o limite de reembolso de alimentação em viagem?")
    perguntar(agente, "A TechNova tem escritório em Marte?")  # deve recusar, sem alucinar
    print(">> Compare com o lab 1: agora cada resposta vem com [fonte].")
    print(">> Na última pergunta, sem fonte na base, o agente NÃO inventou.")

# ---------------------------------------------------------------------------
# EQUIVALENTE EM PRODUÇÃO (slide 26) — exige projeto GCP + corpus no Vertex AI:
#
# from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
# from vertexai import rag
# busca = VertexAiRagRetrieval(
#     name="busca_politicas",
#     description="Busca nas políticas internas.",
#     rag_resources=[rag.RagResource(rag_corpus="projects/.../ragCorpora/123")],
#     similarity_top_k=3,
# )
# agente = LlmAgent(model=MODELO, name="rh_assistant", tools=[busca], ...)
# ---------------------------------------------------------------------------
