# iacanga-transparency

Este projeto baixa automaticamente dados do Portal da Transparência de Iacanga.

## Instalação (macOS)

```bash
brew install python@3.12
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Agendamento

Para agendar a execução diária, utilize `crontab -e` ou o `launchd` do macOS.

Exemplo no `crontab`:

```
0 2 * * * /caminho/para/.venv/bin/python /caminho/para/crawler.py
```
