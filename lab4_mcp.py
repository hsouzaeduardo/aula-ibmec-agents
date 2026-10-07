"""
LAB 4 · L5 — CONECTAR A UM SERVIDOR MCP
=======================================
Slides 11-14 e slide 24, Gancho 2: o McpToolset conecta o agente a um servidor
MCP, descobre as ferramentas EM RUNTIME (list_tools) e as injeta no agente.

Aqui usamos o servidor MCP oficial de filesystem (Node), apontado para a pasta
'dados/'. O agente ganha ferramentas de ler/listar arquivos SEM nós programá-las.

PRÉ-REQUISITO: Node.js instalado (o ADK chama 'npx').
    python lab4_mcp.py
"""
import os
from comum import MODELO, exigir_chave, perguntar
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

exigir_chave()

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")

# O agente descobre, em runtime, as tools expostas pelo servidor MCP de filesystem.
agente = LlmAgent(
    model=MODELO,
    name="assistente_arquivos",
    instruction=(
        "Você acessa os arquivos da pasta de dados da TechNova via ferramentas MCP. "
        "Liste, leia e resuma arquivos conforme pedido. Responda em português."
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        PASTA_DADOS,
                    ],
                ),
                # 1a execução baixa o servidor via npx; o padrão (5s) é curto demais.
                timeout=60,
            )
        )
    ],
)

if __name__ == "__main__":
    print("=" * 60)
    print("LAB 4 — Agente conectado a um servidor MCP (filesystem)")
    print("=" * 60)
    print("(A primeira execução baixa o servidor via npx — pode demorar.)\n")
    perguntar(agente, "Quais arquivos existem na pasta de dados?")
    perguntar(agente, "Leia o arquivo produtos.md e me diga os planos e preços.")
    print(">> Não escrevemos NENHUMA tool de arquivo: vieram do servidor MCP.")
    print(">> Trocar o servidor (DB, APIs...) reaproveita o mesmo padrão (slide 13: M+N).")
