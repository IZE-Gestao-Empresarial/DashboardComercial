# Streamlit - Indicadores Comerciais (Google Sheets)

Este app lê diretamente uma aba pública do Google Sheets usando a exportação CSV nativa.

{
  "updatedAt": "...",
  "sheet": "INDICADORES_COMERCIAL",
  "rows": [ ... ]
}

## Como rodar local

1) Instalar deps:
pip install -r requirements.txt

2) Rodar:
streamlit run app.py

## Streamlit Cloud
O app faz refresh automático e atualiza os dados a partir do Sheets.
