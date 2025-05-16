import os
import time
import logging
from logging.handlers import RotatingFileHandler
from typing import List, Dict

import pandas as pd
import requests
from requests import Response
from tqdm import tqdm


BASE_URL = "https://www.iacanga.sp.gov.br/Transparencia/"
HEADERS = {
    "User-Agent": "IacangaCrawler/0.1 (+https://github.com/jrcassorielo)"
}

TIPOS = ["Despesas", "Receitas", "Empenhos"]
ANOS = range(2019, 2026)
MESES = range(1, 13)

LOG_PATH = os.path.join("logs", "crawler.log")
DATA_DIR = "dados"


def configurar_logging() -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    handler = RotatingFileHandler(LOG_PATH, maxBytes=5 * 1024 * 1024, backupCount=5)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=[handler])


def obter_json(url: str) -> List[Dict]:
    for tentativa in range(3):
        try:
            resposta: Response = requests.get(url, headers=HEADERS, timeout=30)
            if resposta.status_code >= 500:
                logging.warning("Falha %s em %s", resposta.status_code, url)
                time.sleep(0.5)
                continue
            if "application/json" in resposta.headers.get("Content-Type", ""):
                return resposta.json()
            logging.warning("Conteúdo não JSON em %s", url)
            return []
        except requests.RequestException as exc:
            logging.warning("Erro de requisição %s", exc)
            time.sleep(0.5)
    logging.error("Falha ao obter %s", url)
    return []


def normalizar_linha(item: Dict) -> Dict:
    return {
        "unidade": item.get("Unidade") or item.get("unidade"),
        "funcao": item.get("Funcao") or item.get("funcao"),
        "subfuncao": item.get("SubFuncao") or item.get("subfuncao"),
        "elemento": item.get("Elemento") or item.get("elemento"),
        "fonte": item.get("Fonte") or item.get("fonte"),
        "favorecido": item.get("Favorecido") or item.get("favorecido"),
        "descricao": item.get("Descricao") or item.get("descricao"),
        "valor_empenhado": item.get("ValorEmpenhado") or item.get("valor_empenhado"),
        "valor_liquidado": item.get("ValorLiquidado") or item.get("valor_liquidado"),
        "valor_pago": item.get("ValorPago") or item.get("valor_pago"),
        "data_empenho": item.get("DataEmpenho") or item.get("data_empenho"),
    }


def salvar_csv(tipo: str, ano: int, mes: int, dados: List[Dict]) -> None:
    if not dados:
        return
    os.makedirs(DATA_DIR, exist_ok=True)
    df = pd.DataFrame([normalizar_linha(d) for d in dados])
    caminho = os.path.join(DATA_DIR, f"{tipo.lower()}_{ano}-{mes:02}.csv")
    df.to_csv(caminho, sep=";", index=False)


def main() -> None:
    configurar_logging()
    for tipo in TIPOS:
        for ano in ANOS:
            for mes in tqdm(MESES, desc=f"{tipo} {ano}"):
                url = f"{BASE_URL}{tipo}?exercicio={ano}&mes={mes}"
                dados = obter_json(url)
                if not dados:
                    continue
                salvar_csv(tipo, ano, mes, dados)


if __name__ == "__main__":
    main()
