"""
LAB 3.5 · O HARNESS — o runtime que faz o agente "andar"
========================================================
Elo perdido entre o slide 9 (loop ReAct) e o slide 22 (ADK na prática).

DEFINIÇÕES (úteis na lousa):
  • Scaffolding = o código que MONTA o agente antes do 1º passo
    (instruções, registro de ferramentas, esquema). Build-time.
  • Harness     = o runtime que roda DEPOIS: o loop pensar->agir->observar,
    despacha ferramentas, realimenta o resultado, controla limite de passos,
    erros e estado. Run-time.

A ideia desta aula: construir um harness MÍNIMO na mão (Parte 1) para a turma
ENXERGAR o loop, e então mostrar que o Runner do ADK é esse harness pronto (Parte 2).

    python lab3b_harness.py
"""
from comum import MODELO, exigir_chave

exigir_chave()

# A mesma ferramenta dos outros labs — aqui ela é só uma função Python.
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


FERRAMENTAS = {"consultar_estoque": consultar_estoque}
MAX_PASSOS = 5  # responsabilidade do harness: não rodar para sempre


# ===========================================================================
# PARTE 1 — HARNESS NA MÃO (sem ADK), usando o SDK google-genai cru
# ===========================================================================
def harness_manual(pergunta: str) -> str:
    """Implementa, à mão, o loop que um harness executa por baixo dos panos."""
    from google import genai
    from google.genai import types

    client = genai.Client()  # usa GOOGLE_API_KEY do ambiente

    # SCAFFOLDING: instrução + ferramentas declaradas + AFC desligado
    # (desligamos a execução automática justamente para FAZER o loop na mão).
    config = types.GenerateContentConfig(
        system_instruction=(
            "Você ajuda a consultar o estoque da TechNova. "
            "Use consultar_estoque quando perguntarem disponibilidade. Responda curto, em PT-BR."
        ),
        tools=[consultar_estoque],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    historico = [types.Content(role="user", parts=[types.Part(text=pergunta)])]

    for passo in range(1, MAX_PASSOS + 1):
        # 1) PENSAR: o modelo decide o próximo passo
        resp = client.models.generate_content(
            model=MODELO, contents=historico, config=config
        )
        turno = resp.candidates[0].content
        historico.append(turno)  # HARNESS: mantém o estado da conversa

        chamadas = [p.function_call for p in turno.parts if p.function_call]
        if not chamadas:
            # Sem ferramenta a chamar -> é a resposta final
            return "".join(p.text for p in turno.parts if p.text)

        # 2) AGIR + 3) OBSERVAR: o harness executa a tool e realimenta o resultado
        for fc in chamadas:
            print(f"   [harness] passo {passo}: executando {fc.name}({dict(fc.args)})")
            resultado = FERRAMENTAS[fc.name](**dict(fc.args))
            historico.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_function_response(
                        name=fc.name, response={"resultado": resultado})],
                )
            )
        # 4) REFLETIR/REPETIR: volta ao topo do loop
    return "[harness] limite de passos atingido sem resposta final."


# ===========================================================================
# PARTE 2 — O MESMO, com o Runner do ADK (o harness PRONTO)
# ===========================================================================
def harness_adk(pergunta: str) -> str:
    """O ADK Runner é o harness: o loop acima vem de graça em 3 linhas."""
    from comum import perguntar
    from google.adk.agents import LlmAgent

    agente = LlmAgent(
        model=MODELO,
        name="assistente_estoque",
        instruction="Consulte o estoque da TechNova com consultar_estoque. PT-BR, curto.",
        tools=[consultar_estoque],
    )
    return perguntar(agente, pergunta, app="harness")


if __name__ == "__main__":
    P = "Temos o notebook NB-14 e o dock DOCK-USB em estoque?"

    print("=" * 60)
    print("PARTE 1 — Harness construído NA MÃO (loop visível)")
    print("=" * 60)
    print(f">>> Pergunta: {P}")
    print(f"<<< Resposta:\n{harness_manual(P)}")

    print("\n" + "=" * 60)
    print("PARTE 2 — O mesmo com o Runner do ADK (harness pronto)")
    print("=" * 60)
    harness_adk(P)

    print(">> Mesma tarefa, mesmo loop. A diferença: na Parte 1 NÓS escrevemos o")
    print("   loop, o controle de passos e o realimento; na Parte 2 o Runner faz isso.")
    print(">> Isso é 'harness engineering': o código ao redor do modelo decide tanto")
    print("   o resultado quanto o próprio modelo.")
