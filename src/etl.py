"""Coleta e preparação das cinco séries oficiais do BACEN."""
from pathlib import Path
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
SERIES = {'selic': 432, 'ipca_mensal': 433, 'ipca_12m': 13522, 'dolar': 1, 'ibc_br': 24364}


def baixar_serie(nome, codigo):
    url = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados'
    resposta = requests.get(url, params={'formato':'json', 'dataInicial':'01/01/2019', 'dataFinal':'31/12/2023'}, timeout=35)
    resposta.raise_for_status()
    tabela = pd.DataFrame(resposta.json())
    tabela['data'] = pd.to_datetime(tabela['data'], format='%d/%m/%Y', errors='coerce')
    tabela[nome] = pd.to_numeric(tabela['valor'].astype(str).str.replace(',', '.', regex=False), errors='coerce')

    
    # Verificar problemas antes da limpeza
    datas_invalidas = tabela['data'].isna().sum()
    valores_invalidos = tabela[nome].isna().sum()
    datas_duplicadas = tabela['data'].duplicated().sum()

    print(f'\nIndicador: {nome}')
    print(f'Datas inválidas: {datas_invalidas}')
    print(f'Valores inválidos: {valores_invalidos}')
    print(f'Datas duplicadas: {datas_duplicadas}')

    # Remover registros inválidos e datas repetidas
    tabela = tabela[['data', nome]].dropna(
        subset=['data', nome]
    ).drop_duplicates(subset=['data'])

    return tabela.sort_values('data')


def preparar():
    DATA.mkdir(parents=True, exist_ok=True)
    # Frequências diferentes: mensal para inflação/IBC-Br, diária para Selic/PTAX.
    # A comparação mensal usa o último valor disponível no mês para séries diárias.
    series = []
    for nome, codigo in SERIES.items():
        df = baixar_serie(nome, codigo)
        df.to_csv(DATA / f'{nome}_bruto.csv', index=False)
        df = df.set_index('data').resample('MS').last().rename_axis('data').reset_index()
        series.append(df)
    base = series[0]
    for tabela in series[1:]:
        base = base.merge(tabela, on='data', how='outer', validate='one_to_one')
    base = base.sort_values('data').reset_index(drop=True)
    base['juro_real'] = ((1 + base['selic']/100) / (1 + base['ipca_12m']/100) - 1) * 100
    base['ano'] = base['data'].dt.year
    base['variacao_dolar_pct'] = base['dolar'].pct_change(fill_method=None) * 100
    base['ipca_12m_prox_3m'] = base['ipca_12m'].shift(-3)
    base.to_csv(DATA / 'macro_tratado.csv', index=False)
    print('Base gerada:', len(base), 'meses; valores ausentes por coluna:')
    print(base.isna().sum().to_string())
    return base

if __name__ == '__main__':
    preparar()
