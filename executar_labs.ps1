<#
executar_labs.ps1 — roda todos os labs da Aula 2 em sequência e salva as saídas
===============================================================================
Uso (de dentro da pasta Labs_Aula2):

    .\executar_labs.ps1              # setup (se preciso) + todos os labs
    .\executar_labs.ps1 -Labs 0,1,2  # só alguns labs (0 1 2 3 3b 4 5 6)
    .\executar_labs.ps1 -SoSetup     # só cria o .venv, instala e verifica

Se o PowerShell bloquear scripts:
    powershell -ExecutionPolicy Bypass -File .\executar_labs.ps1

Saídas de cada lab ficam em .\outputs\<lab>.txt  (+ outputs\RESUMO.txt)
#>
param(
    [string[]]$Labs = @("0", "1", "2", "3", "3b", "4", "5", "6"),
    [switch]$SoSetup
)

# "Continue": no PowerShell 5.1, stderr de python (warnings do ADK) com "Stop" vira erro fatal
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONWARNINGS = "ignore"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$PY  = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$OUT = Join-Path $PSScriptRoot "outputs"
$Labs = $Labs -join "," -split "[,\s]+" | Where-Object { $_ }

# Roda um script python, mostra na tela e grava em outputs\<nome>.txt (UTF-8)
function Rodar-Py($script, $log) {
    $linhas = & $PY $script 2>&1 | ForEach-Object { "$_" } |
        Where-Object { $_ -notmatch "UserWarning|check_feature_enabled|^\s+warnings\.warn" } |
        ForEach-Object { Write-Host $_; $_ }
    $rc = $LASTEXITCODE
    $linhas | Out-File -FilePath $log -Encoding utf8
    return $rc
}

# --- 1. Ambiente virtual + dependências -----------------------------------
if (-not (Test-Path $PY)) {
    Write-Host ">> Criando .venv e instalando dependências..." -ForegroundColor Cyan
    python -m venv .venv
    & $PY -m pip install -q --upgrade pip
    & $PY -m pip install -q -r requirements.txt
}
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ">> Criei o .env — cole sua GOOGLE_API_KEY nele e rode de novo." -ForegroundColor Yellow
}
New-Item -ItemType Directory -Force $OUT | Out-Null

# --- 2. Verificação de ambiente -------------------------------------------
$rc = Rodar-Py "00_setup_check.py" (Join-Path $OUT "00_setup_check.txt")
if ($SoSetup) { exit $rc }
if ($rc -ne 0) {
    Write-Host ">> Corrija os itens FALHA acima (provavelmente a chave no .env)." -ForegroundColor Red
    exit 1
}

$resumo = New-Object System.Collections.ArrayList
function Rodar-Lab($nome, $script) {
    Write-Host "`n############ $nome ($script) ############" -ForegroundColor Cyan
    $inicio = Get-Date
    $rc = Rodar-Py $script (Join-Path $OUT ($script -replace "\.py$", ".txt"))
    $seg = [int]((Get-Date) - $inicio).TotalSeconds
    [void]$resumo.Add([pscustomobject]@{
        Lab = $nome; Script = $script; Tempo = "${seg}s"
        Status = $(if ($rc -eq 0) { "OK" } else { "FALHA (exit $rc)" })
    })
}

$mapa = [ordered]@{
    "0"  = @("Lab 0 · Dados",          "lab0_dados.py")
    "1"  = @("Lab 1 · Agente + tool",  "lab1_agente_tool.py")
    "2"  = @("Lab 2 · RAG + grounding","lab2_rag_grounding.py")
    "3"  = @("Lab 3 · Agente único",   "lab3_agente_unico.py")
    "3b" = @("Lab 3.5 · Harness",      "lab3b_harness.py")
    "4"  = @("Lab 4 · MCP",            "lab4_mcp.py")
    "6"  = @("Lab 6 · Capstone",       "lab6_capstone.py")
}

foreach ($l in $Labs) {
    if ($l -eq "5") {
        # Lab 5: sobe o servidor A2A em 2o plano, roda o orquestrador e SEMPRE derruba o servidor
        Write-Host "`n############ Lab 5 · A2A (servidor + orquestrador) ############" -ForegroundColor Cyan
        $srvLog = Join-Path $OUT "lab5_a2a_servidor.txt"
        $srv = Start-Process -FilePath $PY -ArgumentList "lab5_a2a_servidor.py" `
            -RedirectStandardOutput $srvLog -RedirectStandardError "$srvLog.err" `
            -WindowStyle Hidden -PassThru
        try {
            $pronto = $false
            foreach ($i in 1..30) {
                try {
                    Invoke-WebRequest "http://localhost:8001/.well-known/agent-card.json" `
                        -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop | Out-Null
                    $pronto = $true; break
                } catch { Start-Sleep -Seconds 1 }
            }
            if ($pronto) {
                Write-Host ">> Servidor A2A no ar (porta 8001)." -ForegroundColor Green
                Rodar-Lab "Lab 5 · A2A" "lab5_a2a_orquestrador.py"
            } else {
                Write-Host ">> Servidor A2A não subiu — veja $srvLog.err" -ForegroundColor Red
                [void]$resumo.Add([pscustomobject]@{ Lab = "Lab 5 · A2A"; Script = "lab5_a2a_servidor.py"; Tempo = "-"; Status = "FALHA (servidor)" })
            }
        } finally {
            # o venv do Windows usa um processo "lançador": derruba quem estiver na porta 8001
            Stop-Process -Id $srv.Id -Force -ErrorAction SilentlyContinue
            Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue |
                ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
        }
        continue
    }
    if ($mapa.Contains($l)) { Rodar-Lab $mapa[$l][0] $mapa[$l][1] }
    else { Write-Host ">> Lab desconhecido: $l" -ForegroundColor Yellow }
}

# --- 3. Resumo ------------------------------------------------------------
Write-Host "`n================ RESUMO ================" -ForegroundColor Cyan
$tabela = $resumo | Format-Table -AutoSize | Out-String
Write-Host $tabela
$tabela | Out-File -FilePath (Join-Path $OUT "RESUMO.txt") -Encoding utf8
Write-Host "Saídas completas em: $OUT"
if ($resumo | Where-Object { $_.Status -ne "OK" }) { exit 1 }
