"""
LAB 0 · L0 — DADOS (a base de tudo)
===================================
Slide 4: "L0 · Dados — Coleta, limpeza e governança."
Slide 6: a INDEXAÇÃO offline (Fontes -> Chunking -> Embeddings -> Vector DB).

Mensagem em sala: antes de qualquer IA inteligente, existe DADO preparado.
Aqui fazemos o "chunking" da base — o primeiro passo do RAG — sem nenhum modelo.

    python lab0_dados.py
"""
import glob
import os
import re

PASTA_DADOS = os.path.join(os.path.dirname(__file__), "dados")


def carregar_documentos():
    """Lê os arquivos .md da pasta dados/."""
    docs = {}
    for caminho in glob.glob(os.path.join(PASTA_DADOS, "*.md")):
        with open(caminho, encoding="utf-8") as f:
            docs[os.path.basename(caminho)] = f.read()
    return docs


def chunk_por_secao(texto):
    """
    Chunking simples por seção (cabeçalhos '## ...').
    Em produção usaríamos chunking semântico + sobreposição (slide 7, Advanced RAG).
    """
    blocos = re.split(r"\n(?=##\s)", texto)
    return [b.strip() for b in blocos if b.strip()]


def construir_indice():
    """Devolve uma lista de chunks com metadados (rastreabilidade = governança)."""
    indice = []
    for arquivo, texto in carregar_documentos().items():
        for i, bloco in enumerate(chunk_por_secao(texto)):
            titulo = bloco.splitlines()[0].lstrip("# ").strip()
            indice.append({
                "fonte": arquivo,
                "secao": titulo,
                "id": f"{arquivo}#{i}",
                "texto": bloco,
            })
    return indice


if __name__ == "__main__":
    print("=" * 60)
    print("LAB 0 — Preparando a base de conhecimento (L0)")
    print("=" * 60)
    indice = construir_indice()
    print(f"Documentos lidos: {len(set(c['fonte'] for c in indice))}")
    print(f"Chunks gerados:   {len(indice)}\n")
    for c in indice:
        print(f"  [{c['id']}]  {c['secao']}  ({len(c['texto'])} chars)")
    print("\n>> Esse índice de chunks é o que o RAG vai consultar no lab 2.")
    print(">> Repare: cada chunk guarda sua FONTE — isso é o que permite citar depois.")
