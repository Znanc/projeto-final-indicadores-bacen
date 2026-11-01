
-- 1. Consultar os indicadores por mês
SELECT
    t.ano,
    t.mes,
    f.selic,
    f.ipca_12m,
    f.dolar,
    f.ibc_br
FROM fato_indicadores f
JOIN dim_tempo t ON f.data = t.data
ORDER BY t.ano, t.mes;


-- 2. Verificar a média da Selic por ano
SELECT
    t.ano,
    ROUND(AVG(f.selic), 2) AS media_selic
FROM fato_indicadores f
JOIN dim_tempo t ON f.data = t.data
GROUP BY t.ano
ORDER BY t.ano;


-- 3. Verificar os meses em que o dólar
-- ficou acima da média do período
SELECT
    data,
    dolar
FROM fato_indicadores
WHERE dolar > (
    SELECT AVG(dolar)
    FROM fato_indicadores
)
ORDER BY data;


-- 4. Comparar Selic e juro real
SELECT
    data,
    selic,
    ipca_12m,
    juro_real
FROM fato_indicadores
ORDER BY data;


-- 5. Consultar a atividade econômica
-- durante o período analisado
SELECT
    t.ano,
    ROUND(AVG(f.ibc_br), 2) AS media_ibc_br
FROM fato_indicadores f
JOIN dim_tempo t ON f.data = t.data
GROUP BY t.ano
ORDER BY t.ano;
