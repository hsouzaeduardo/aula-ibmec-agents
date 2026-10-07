"""
comum.py — utilitários compartilhados pelos labs
================================================
Mantém os scripts de aula curtos: a "cola" de Runner/sessão fica aqui.
"""
import asyncio
import os
import sys

# --- carrega o arquivo .env da pasta dos labs (GOOGLE_API_KEY etc.) ---
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

# --- garante que a chave existe antes de qualquer chamada ao modelo ---
def exigir_chave():
    chave = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not chave or chave == "cole-sua-chave-aqui":
        print("ERRO: defina GOOGLE_API_KEY no arquivo .env (ou no ambiente). Veja o README.")
        sys.exit(1)


# Modelo usado em todos os labs (rápido e barato, ideal para demo ao vivo)
MODELO = "gemini-2.5-flash"


async def _rodar(agente, prompt, app="aula2", usuario="aluno"):
    """Executa UMA pergunta no agente e devolve o texto final."""
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    runner = InMemoryRunner(agent=agente, app_name=app)
    await runner.session_service.create_session(
        app_name=app, user_id=usuario, session_id="s1"
    )
    conteudo = types.Content(role="user", parts=[types.Part(text=prompt)])

    resposta_final = ""
    async for evento in runner.run_async(
        user_id=usuario, session_id="s1", new_message=conteudo
    ):
        # Mostra cada ferramenta que o agente decide chamar (visível em sala)
        if evento.content and evento.content.parts:
            for parte in evento.content.parts:
                fc = getattr(parte, "function_call", None)
                if fc:
                    print(f"   [tool] -> {fc.name}({dict(fc.args)})")
        if evento.is_final_response() and evento.content:
            resposta_final = evento.content.parts[0].text
    return resposta_final


def perguntar(agente, prompt, app="aula2"):
    """Versão síncrona para usar em scripts de demonstração."""
    print(f"\n>>> Pergunta: {prompt}")
    resposta = asyncio.run(_rodar(agente, prompt, app=app))
    print(f"<<< Resposta:\n{resposta}\n" + "-" * 60)
    return resposta
