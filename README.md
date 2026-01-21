# Streamlit - Indicadores Comerciais (Google Sheets)

Este app lê um endpoint (Apps Script Web App) que retorna JSON no formato:

{
  "updatedAt": "...",
  "sheet": "INDICADORES_COMERCIAL",
  "rows": [ ... ]
}

## Como rodar local

1) Instalar deps:
pip install -r requirements.txt

2) Criar secrets:
- Windows: %USERPROFILE%\.streamlit\secrets.toml
- Linux/mac: ~/.streamlit/secrets.toml

Conteúdo do secrets.toml:

SHEETS_WEBAPP_URL = "https://script.google.com/macros/s/...../exec"
SHEETS_WEBAPP_TOKEN = "seu_token"

3) Rodar:
streamlit run app.py

## Streamlit Cloud
No Streamlit Cloud -> Settings -> Secrets, use as mesmas chaves.

O app faz refresh automático a cada 1 minuto.
