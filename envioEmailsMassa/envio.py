#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
import json  # ← ADICIONADO
from email.message import EmailMessage
from typing import List
import time

# ---------- CONFIGURAÇÕS ----------

# config das contas 

# 000devHome@gmail.com  -  jmqg fvep cjnm oluy
# desenvolvasoftwares@gmail.com  -  irak wyqd plnk wkcf

#==================

REMETENTE     = ""
SENHA         = ""
SERVIDOR_SMTP = "smtp.gmail.com"
PORTA_SMTP    = 587
ASSUNTO       = "Viabilidade Técnica"
CORPO_HTML    = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pesquisa de Viabilidade Técnica</title>
<style>
  body {
    font-family: 'Segoe UI', Arial, sans-serif;
    background-color: #f0f2f5;
    margin: 0;
    padding: 20px;
    color: #333;
  }

  .container {
    max-width: 500px;
    margin: 20px auto;
    background: #ffffff;
    padding: 35px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  }

  h1 {
    font-size: 20px;
    color: #1a365d;
    line-height: 1.3;
  }

  p {
    line-height: 1.6;
    font-size: 15px;
    color: #4a5568;
  }

  .highlight-box {
    background: #f8fafc;
    border-left: 4px solid #2563eb;
    padding: 15px;
    margin: 20px 0;
    font-style: italic;
  }

  .btn {
    display: block;
    text-align: center;
    background: #2563eb;
    color: #ffffff !important;
    text-decoration: none;
    padding: 15px;
    border-radius: 8px;
    font-weight: bold;
    margin-bottom: 12px;
    transition: background 0.3s ease;
  }

  .btn:hover {
    background: #1d4ed8;
  }

  .btn-secondary {
    background: #ffffff;
    color: #2563eb !important;
    border: 1px solid #2563eb;
  }

  .btn-secondary:hover {
    background: #f1f5f9;
  }

  .footer {
    font-size: 12px;
    color: #94a3b8;
    text-align: center;
    margin-top: 30px;
  }
</style>
</head>

<body>
  <div class="container">
    <h1>Análise de Retenção de Pacientes</h1>
    
    <p>
      Olá, estou desenvolvendo uma ferramenta específica para clínicas que desejam 
      <strong>blindar sua reputação online</strong>. 
    </p>

    <p>
      Estudos mostram que 70% dos pacientes leem avaliações antes de agendar. Uma resposta profissional em tempo hábil pode converter uma crítica em uma nova oportunidade.
    </p>

    <div class="highlight-box">
      "Se uma solução automatizada evitasse a perda de apenas um paciente por mês, isso teria valor estratégico para sua clínica hoje?"
    </div>

    <a class="btn" href="mailto:seu-email@dominio.com?subject=Interesse: Monitoramento de Avaliações&body=Olá, gostaria de saber mais sobre como funciona a validação desse serviço de monitoramento para minha clínica.">
      Sim, gostaria de mais informações
    </a>

    <a class="btn btn-secondary" href="mailto:seu-email@dominio.com?subject=Consulta: Site Institucional Profissional&body=Olá, vi que você também desenvolve sites. Poderia me enviar informações sobre prazos e modelos para clínicas?">
      Preciso de um site profissional
    </a>

    <p style="font-size: 13px; margin-top: 20px;">
      <em>Basta clicar em uma das opções acima para me enviar uma resposta automática.</em>
    </p>

    <div class="footer">
      Pesquisa de mercado conduzida por DEVs<br>
      Foco em Desenvolvimento de Software e Experiência do Paciente.
    </div>
  </div>
</body>
</html>
"""  # (seu HTML continua igual)
ARQ_LISTA     = "emails.txt"
DELAY_SEG     = 10
ARQ_PROGRESSO = "progresso.json"  # ← ADICIONADO
LIMITE_POR_EXEC = 10              # ← ADICIONADO
# -----------------------------------

ordemEmail = 0

if (ordemEmail == 0):
  REMETENTE     = "000devHome@gmail.com"
  SENHA         = "jmqg fvep cjnm oluy"
else:
  REMETENTE     = "desenvolvasoftwares@gmail.com"
  SENHA         = "irak wyqd plnk wkcf"


def ler_lista(caminho: str) -> List[str]:
    with open(caminho, encoding="utf-8") as f:
        return [lin.strip() for lin in f if lin.strip() and "@" in lin]

def carregar_progresso() -> int:
    try:
        with open(ARQ_PROGRESSO, "r", encoding="utf-8") as f:
            return json.load(f).get("index", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def salvar_progresso(index: int):
    with open(ARQ_PROGRESSO, "w", encoding="utf-8") as f:
        json.dump({"index": index}, f)

def enviar_para(dest: str, remetente: str, senha: str,
                servidor: str, porta: int, assunto: str, html: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = dest
    msg.set_content("Seu cliente de e-mail não suporta HTML.")
    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP(servidor, porta) as smtp:
        smtp.starttls()
        smtp.login(remetente, senha)
        smtp.send_message(msg)
    print(f"[✓] Enviado para {dest}")

def main():
    emails = ler_lista(ARQ_LISTA)
    total = len(emails)
    print(f"Total de destinatários: {total}\n")

    indice_atual = carregar_progresso()
    enviados = 0

    while enviados < LIMITE_POR_EXEC and indice_atual < total:
        dest = emails[indice_atual]
        try:
            enviar_para(dest, REMETENTE, SENHA, SERVIDOR_SMTP, PORTA_SMTP,
                        ASSUNTO, CORPO_HTML)
            time.sleep(DELAY_SEG)
            enviados += 1
            indice_atual += 1
        except Exception as exc:
            print(f"[ERRO] {dest} -> {exc}")
            indice_atual += 1

    salvar_progresso(indice_atual % total)
    print(f"\n[✓] Envios realizados: {enviados}")
    print(f"[→] Próximo índice: {indice_atual % total}")

if __name__ == "__main__":
    main()