
-- Tabela com informações de mês e ano
CREATE TABLE IF NOT EXISTS dim_tempo (
    data DATE PRIMARY KEY,
    ano INTEGER,
    mes INTEGER
);

-- Tabela com os indicadores econômicos
CREATE TABLE IF NOT EXISTS fato_indicadores (
    data DATE PRIMARY KEY,
    selic NUMERIC,
    ipca_mensal NUMERIC,
    ipca_12m NUMERIC,
    dolar NUMERIC,
    ibc_br NUMERIC,
    juro_real NUMERIC,
    variacao_dolar_pct NUMERIC,
    ipca_12m_prox_3m NUMERIC,
    FOREIGN KEY (data) REFERENCES dim_tempo(data)
);
