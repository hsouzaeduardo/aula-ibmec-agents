"""
00 · Verificação de ambiente
============================
Rode ANTES da aula. Confirma Python, pacotes e a chave do Gemini.

    python 00_setup_check.py
"""
import os
import sys


def check(nome, ok, detalhe=""):
    marca = "OK " if ok else "FALHA"
    print(f"[{marca}] {nome}" + (f"  -> {detalhe}" if detalhe else ""))
    return ok


def main():
    print("=" * 56)
    print("VERIFICACAO DE AMBIENTE — Labs Aula 2")
    print("=" * 56)
    tudo = True

    # Python 3.10+
    v = sys.version_info
    tudo &= check("Python 3.10+", v >= (3, 10), f"{v.major}.{v.minor}.{v.micro}")

    # google-adk
    try:
        import google.adk  # noqa
        tudo &= check("Pacote google-adk", True)
    except ImportError:
        tudo &= check("Pacote google-adk", False, "pip install google-adk")

    # google-genai
    try:
        import google.genai  # noqa
        tudo &= check("Pacote google-genai", True)
    except ImportError:
        tudo &= check("Pacote google-genai", False, "pip install google-genai")

    # Chave de API (ambiente ou arquivo .env)
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
    except ImportError:
        pass
    chave = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    tem_key = bool(chave) and chave != "cole-sua-chave-aqui"
    tudo &= check("GOOGLE_API_KEY definida", tem_key,
                  "" if tem_key else "preencha GOOGLE_API_KEY no arquivo .env")

    # Node (apenas para o lab 4 MCP) — não bloqueia
    import shutil
    tem_node = shutil.which("npx") is not None
    check("Node/npx (opcional, lab 4 MCP)", tem_node,
          "" if tem_node else "instale Node.js para o lab de MCP")

    print("=" * 56)
    if tudo:
        print(">> Ambiente pronto. Pode comecar pelo lab0_dados.py")
    else:
        print(">> Resolva os itens marcados como FALHA antes da aula.")
    print("=" * 56)
    sys.exit(0 if tudo else 1)


if __name__ == "__main__":
    main()
