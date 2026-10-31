
# Criar o banco de dados e executar as consultas SQL

from pathlib import Path
import sqlite3
import pandas as pd

# Localizar a pasta principal do projeto
pasta_projeto = Path(__file__).resolve().parents[1]

# Arquivos utilizados
arquivo_csv = pasta_projeto / "data" / "macro_tratado.csv"
arquivo_tabelas = pasta_projeto / "sql" / "criar_tabelas.sql"
arquivo_consultas = pasta_projeto / "sql" / "consultas.sql"
arquivo_banco = pasta_projeto / "data" / "indicadores.db"

# Ler os dados tratados
dados = pd.read_csv(arquivo_csv)

# Conectar ao banco SQLite
conexao = sqlite3.connect(arquivo_banco)
conexao.execute("PRAGMA foreign_keys = ON")

try:
    # Criar as tabelas
    with open(arquivo_tabelas, "r", encoding="utf-8") as arquivo:
        conexao.executescript(arquivo.read())

    # Preparar a dimensão de tempo
    tempo = dados[["data", "ano"]].copy()
    tempo["mes"] = pd.to_datetime(tempo["data"]).dt.month

    # Preparar a tabela fato
    indicadores = dados.drop(columns=["ano"])

    
    # Limpar os registros anteriores, mantendo a estrutura das tabelas
    conexao.execute("DELETE FROM fato_indicadores")
    conexao.execute("DELETE FROM dim_tempo")

    # Inserir os dados nas tabelas já criadas
    tempo.to_sql("dim_tempo", conexao, if_exists="append", index=False)
    indicadores.to_sql("fato_indicadores", conexao, if_exists="append", index=False)

    conexao.commit()


    # Executar as consultas SQL
    with open(arquivo_consultas, "r", encoding="utf-8") as arquivo:
        consultas = arquivo.read()

    for numero, consulta in enumerate(consultas.split(";"), start=1):
        if consulta.strip():
            resultado = pd.read_sql_query(consulta, conexao)

            print(f"\nConsulta {numero}")
            print(resultado.head().to_string(index=False))

    print("\nBanco de dados criado e consultas executadas!")

finally:
    conexao.close()
