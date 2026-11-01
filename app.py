"""Dashboard educacional de macroeconomia brasileira (2019–2023)."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='Painel Macroeconômico | BACEN', layout='wide')
st.title('Painel Macroeconômico Brasileiro | 2019–2023')
st.caption('Fonte: Banco Central do Brasil, (SGS).')

@st.cache_data(ttl=3600)
def carregar():
    # Prioriza SQL quando configurado; mantém CSV como contingência.
    try:
        conn = st.connection('postgresql', type='sql')
        df = conn.query('SELECT * FROM macro_tratado ORDER BY data', ttl=3600)
        if df.empty:
            raise ValueError('Banco sem registros')
        return df
    except Exception:
        caminho = ROOT / 'data' / 'macro_tratado.csv'
        if not caminho.exists():
            st.error('Base não encontrada. Execute: python -m src.etl')
            st.stop()
        return pd.read_csv(caminho)

base = carregar()
base['data'] = pd.to_datetime(base['data'])
base['ano'] = base['data'].dt.year
anos = sorted(base['ano'].dropna().unique().tolist())
if 'anos' not in st.session_state:
    st.session_state.anos = anos
if 'variaveis' not in st.session_state:
    st.session_state.variaveis = ['selic','ipca_12m','dolar','ibc_br']
if 'intervalo' not in st.session_state:
    st.session_state.intervalo = (base['data'].min().date(), base['data'].max().date())
with st.sidebar:
    st.header('Filtros')
    def resetar():
        st.session_state.anos = anos
        st.session_state.variaveis = ['selic','ipca_12m','dolar','ibc_br']
        st.session_state.intervalo = (base['data'].min().date(), base['data'].max().date())
    st.button('Resetar filtros', on_click=resetar)
    st.multiselect('Anos', anos, key='anos')
    st.multiselect('Variáveis para correlação', ['selic','ipca_mensal','ipca_12m','dolar','ibc_br','juro_real'], key='variaveis')
    st.date_input(
    "Período",
    min_value=base["data"].min().date(),
    max_value=base["data"].max().date(),
    format="DD/MM/YYYY",
    key="intervalo"
)
periodo = st.session_state.intervalo
if not isinstance(periodo, (list,tuple)) or len(periodo) != 2:
    st.info('Selecione as duas datas do período.')
    st.stop()
df = base[base['ano'].isin(st.session_state.anos) & base['data'].between(pd.Timestamp(periodo[0]), pd.Timestamp(periodo[1]))].copy()
if df.empty:
    st.warning('Nenhum dado para os filtros selecionados.')
    st.stop()


def metrica(coluna, rotulo, unidade):
    # Buscar os valores do indicador
    serie = df.sort_values("data")[coluna].dropna()

    if serie.empty:
        return rotulo, "Sem dados", None

    # Identificar o valor atual e o anterior
    atual = serie.iloc[-1]
    anterior = serie.iloc[-2] if len(serie) > 1 else None

    # Calcular a diferença entre os valores
    if anterior is not None:
        if coluna == "dolar":
            delta = f"R$ {atual - anterior:+.2f}"
        else:
            delta = f"{atual - anterior:+.2f} p.p."
    else:
        delta = None

    # Formatar o dólar no padrão brasileiro
    if coluna == "dolar":
        valor = f"R$ {atual:.2f}".replace(".", ",")
    else:
        valor = f"{atual:.2f}{unidade}"

    # Retornar as informações para os indicadores
    return rotulo, valor, delta


cols = st.columns(4)
for coluna,rotulo,unidade,area in zip(['selic','ipca_12m','juro_real','dolar'], ['Selic Meta','IPCA 12 meses','Juro real estimado','Dólar PTAX'], ['% a.a.','%','% a.a.',' R$'],cols):
    nome,valor,delta = metrica(coluna,rotulo,unidade)
    area.metric(
    nome,
    valor,
    delta,
    delta_color="off" if coluna == "dolar" else "normal"
)
aba1,aba2,aba3,aba4 = st.tabs(['1. Juros e inflação','2. Câmbio','3. Atividade','4. Correlações'])


with aba1:
    st.subheader("Pergunta 1 — Selic, inflação e juro real")

    # Criar o gráfico com os três indicadores
    fig = go.Figure()

    fig.add_bar(
        x=df["data"],
        y=df["juro_real"],
        name="Juro real estimado (%)",
        opacity=0.4
    )

    fig.add_scatter(
        x=df["data"],
        y=df["selic"],
        name="Selic (%)"
    )

    fig.add_scatter(
        x=df["data"],
        y=df["ipca_12m"],
        name="IPCA 12m (%)"
    )

    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Taxa (%)"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Encontrar os três meses com maiores juros reais
    maiores_juros = df.nlargest(3, "juro_real")[
        ["data", "juro_real"]
    ].copy()

    # Melhorar a apresentação da tabela
    maiores_juros["data"] = maiores_juros["data"].dt.strftime("%m/%Y")
    maiores_juros["juro_real"] = maiores_juros["juro_real"].round(2)

    maiores_juros.columns = ["Mês/Ano", "Juro real estimado (%)"]

    st.write("**Meses com maiores juros reais estimados:**")
    st.dataframe(maiores_juros, hide_index=True)

    # Análise dos indicadores conforme os filtros selecionados
    st.write("**Análise dos indicadores:**")

    # Encontrar o mês com maior juro real
    maior_juro = df.loc[df["juro_real"].idxmax()]

    # Preparar as informações
    mes_ano = maior_juro["data"].strftime("%m/%Y")
    valor_juro = maior_juro["juro_real"]

    # Identificar o primeiro e o último ano
    ano_inicial = df["ano"].min()
    ano_final = df["ano"].max()

    # Ajustar o texto conforme a quantidade de anos
    if ano_inicial == ano_final:
        periodo_texto = str(ano_inicial)
    else:
        periodo_texto = f"{ano_inicial} a {ano_final}"

    # Mostrar a análise completa
    st.write(
        f"No período selecionado ({periodo_texto}), "
        f"o maior juro real estimado foi registrado em {mes_ano}, "
        f"atingindo {valor_juro:.2f}%. "
        "Esse indicador é uma estimativa do juro real, "
        "calculada pela fórmula de Fisher, utilizando a Selic meta "
        "e a inflação acumulada em 12 meses."
    )



with aba2:
    st.subheader("Pergunta 2 — Dólar em relação à média histórica")

    # Calcular a média histórica de 2019 a 2023
    media = base["dolar"].mean()

    # Criar o gráfico do dólar
    fig = px.line(
        df,
        x="data",
        y="dolar",
        title="Dólar PTAX venda (R$)"
    )

    # Adicionar a linha da média histórica
    fig.add_hline(
        y=media,
        line_dash="dash",
        annotation_text=f"Média 2019–2023: R$ {media:.2f}"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Identificar os meses acima da média histórica
    meses_acima = int((df["dolar"] > media).sum())

    st.write(
        f"Meses do período selecionado acima da média histórica: {meses_acima}."
    )

    # Identificar períodos consecutivos acima da média
    dados_dolar = df.sort_values("data").copy()
    dados_dolar["acima_media"] = dados_dolar["dolar"] > media

    periodos = []
    inicio = None
    fim = None

    for _, linha in dados_dolar.iterrows():
        if linha["acima_media"]:
            if inicio is None:
                inicio = linha["data"]
            elif (linha["data"].year - fim.year) * 12 + (
                linha["data"].month - fim.month
            ) != 1:
                periodos.append((inicio, fim))
                inicio = linha["data"]

            fim = linha["data"]

        elif inicio is not None:
            periodos.append((inicio, fim))
            inicio = None
            fim = None

    if inicio is not None:
        periodos.append((inicio, fim))

    # Mostrar os períodos encontrados
    st.write("**Períodos consecutivos acima da média:**")

    if periodos:
        for inicio, fim in periodos:
            if inicio == fim:
                st.write(f"- {inicio.strftime('%m/%Y')}")
            else:
                st.write(
                    f"- {inicio.strftime('%m/%Y')} "
                    f"até {fim.strftime('%m/%Y')}"
                )
    else:
        st.write("Nenhum mês acima da média no período selecionado.")

    # Analisar os valores do dólar
    maior_dolar = df["dolar"].max()
    menor_dolar = df["dolar"].min()

    ano_inicial = df["ano"].min()
    ano_final = df["ano"].max()

    if ano_inicial == ano_final:
        periodo_texto = str(ano_inicial)
    else:
        periodo_texto = f"{ano_inicial} a {ano_final}"

    st.write("**Análise do câmbio:**")

    st.write(
        f"No período selecionado ({periodo_texto}), "
        f"o dólar variou entre R$ {menor_dolar:.2f} "
        f"e R$ {maior_dolar:.2f}. "
        f"A média histórica de 2019 a 2023 foi de R$ {media:.2f}. "
        f"O dólar ficou acima dessa média em {meses_acima} meses."
    )

    # Pergunta 3
    st.subheader(
        "Pergunta 3 — Dólar e inflação (associação, não causalidade)"
    )

    # Criar gráfico de dispersão
    fig = px.scatter(
        df,
        x="dolar",
        y="ipca_12m",
        color="ano",
        size="selic",
        hover_data=["data"],
        title="PTAX vs IPCA acumulado em 12 meses"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Calcular as correlações
    correlacao_atual = df[["dolar", "ipca_12m"]].corr().iloc[0, 1]

    correlacao_futura = df[
        ["variacao_dolar_pct", "ipca_12m_prox_3m"]
    ].corr().iloc[0, 1]

    st.write(
        f"Correlação contemporânea: {correlacao_atual:.3f}"
    )

    st.write(
        "Correlação entre a variação mensal do dólar "
        f"e o IPCA 12 meses três meses depois: {correlacao_futura:.3f}"
    )

    # Explica como foi calculada a correlação futura
    st.caption(
        "A correlação com três meses de diferença compara a variação "
        "mensal do dólar com o IPCA acumulado em 12 meses observado "
        "três meses depois. A análise considera os meses selecionados "
        "nos filtros, utilizando os valores futuros previamente calculados "
        "na base de dados. Correlação não significa causalidade."
    )

    # Classificar a intensidade da correlação
    def interpretar_correlacao(valor):
        if pd.isna(valor):
            return "não pôde ser calculada"

        intensidade = abs(valor)

        if intensidade < 0.3:
            forca = "fraca"
        elif intensidade < 0.7:
            forca = "moderada"
        else:
            forca = "forte"

        if valor > 0:
            return f"positiva e {forca}"
        elif valor < 0:
            return f"negativa e {forca}"
        else:
            return "nula"

    # Mostrar a interpretação
    st.write("**Análise da correlação:**")

    st.write(
        "No período selecionado, a correlação entre "
        "o dólar e o IPCA acumulado em 12 meses foi "
        f"{interpretar_correlacao(correlacao_atual)}."
    )

    st.write(
        "A correlação entre a variação mensal do dólar "
        "e o IPCA acumulado em 12 meses três meses depois foi "
        f"{interpretar_correlacao(correlacao_futura)}. "
        "Esses resultados indicam associação estatística, "
        "mas não comprovam uma relação de causa e efeito."
    )

    
with aba3:
    st.subheader("Pergunta 4 — Atividade econômica (IBC-Br dessazonalizado)")

    # Criar o gráfico de evolução mensal do IBC-Br
    fig = px.line(
        df,
        x="data",
        y="ibc_br",
        title="IBC-Br: evolução mensal"
    )

    st.plotly_chart(fig, width="stretch")

    # Organizar os dados por data
    dados_atividade = df.sort_values("data").dropna(
        subset=["ibc_br"]
    ).copy()

    if dados_atividade.empty:
        st.info("Não há dados de IBC-Br para o período selecionado.")

    else:
        # Encontrar os meses de maior e menor atividade econômica
        maior_ibc = dados_atividade.loc[
            dados_atividade["ibc_br"].idxmax()
        ]

        menor_ibc = dados_atividade.loc[
            dados_atividade["ibc_br"].idxmin()
        ]

        # Criar uma tabela simples com os resultados
        resumo = pd.DataFrame({
            "Indicador": ["Maior IBC-Br", "Menor IBC-Br"],
            "Mês/Ano": [
                maior_ibc["data"].strftime("%m/%Y"),
                menor_ibc["data"].strftime("%m/%Y")
            ],
            "Valor": [
                round(maior_ibc["ibc_br"], 2),
                round(menor_ibc["ibc_br"], 2)
            ]
        })

        st.write("**Maiores e menores valores do IBC-Br:**")
        st.dataframe(resumo, hide_index=True)

        # Comparar o primeiro e o último mês selecionado
        valor_inicial = dados_atividade["ibc_br"].iloc[0]
        valor_final = dados_atividade["ibc_br"].iloc[-1]

        variacao = (
            (valor_final - valor_inicial) / valor_inicial
        ) * 100 if valor_inicial != 0 else None

        # Identificar os meses analisados
        data_inicial = dados_atividade["data"].iloc[0].strftime("%m/%Y")
        data_final = dados_atividade["data"].iloc[-1].strftime("%m/%Y")

        # Verificar se o indicador aumentou ou diminuiu
        if variacao is None:
            comportamento = "não pôde ter sua variação calculada"
        elif variacao > 0:
            comportamento = "apresentou crescimento"
        elif variacao < 0:
            comportamento = "apresentou queda"
        else:
            comportamento = "permaneceu estável"

        # Mostrar a análise conforme os filtros
        st.write("**Análise dos indicadores:**")

        if variacao is not None:
            st.write(
                f"Entre {data_inicial} e {data_final}, "
                f"o IBC-Br {comportamento}, "
                f"com variação de {variacao:+.2f}%. "
                f"O maior valor foi registrado em "
                f"{maior_ibc['data'].strftime('%m/%Y')} "
                f"e o menor em "
                f"{menor_ibc['data'].strftime('%m/%Y')}."
            )
        else:
            st.write(
                "Não foi possível calcular a variação do IBC-Br "
                "para o período selecionado."
            )

        # Comparação descritiva com a Selic
        if dados_atividade["selic"].notna().sum() >= 2:
            selic_inicial = dados_atividade["selic"].iloc[0]
            selic_final = dados_atividade["selic"].iloc[-1]

            st.write(
                f"No mesmo período, a Selic passou de "
                f"{selic_inicial:.2f}% para {selic_final:.2f}% ao ano. "
                "A comparação permite observar o comportamento "
                "dos indicadores ao longo do tempo, mas não comprova "
                "que as mudanças na Selic causaram as variações do IBC-Br."
            )

    st.caption(
        "O IBC-Br é um indicador de atividade econômica. "
        "A comparação temporal com a Selic não comprova causalidade."
    )




with aba4:
    st.subheader("Pergunta 5 — Matriz de correlação de Pearson")

    # Identificar as variáveis selecionadas no filtro
    escolhidas = st.session_state.variaveis

    if len(escolhidas) < 2:
        st.info("Selecione pelo menos duas variáveis no filtro lateral.")

    else:
        # Calcular a correlação entre os indicadores
        correlacao = df[escolhidas].corr()

        # Mostrar a matriz de correlação
        fig = px.imshow(
            correlacao,
            text_auto=".2f",
            zmin=-1,
            zmax=1,
            color_continuous_scale="RdBu_r",
            title="Correlação linear (-1 a +1)"
        )

        st.plotly_chart(fig, width="stretch")

        # Organizar os pares de indicadores
        pares = correlacao.where(
            ~pd.DataFrame(
                [
                    [i >= j for j in range(len(correlacao))]
                    for i in range(len(correlacao))
                ],
                index=correlacao.index,
                columns=correlacao.columns
            )
        ).stack().reset_index()

        pares.columns = ["Variável 1", "Variável 2", "Correlação"]

        # Ordenar pela força da correlação
        pares = pares.assign(
            Forca=pares["Correlação"].abs()
        ).sort_values("Forca", ascending=False)

        # Mostrar a tabela
        st.dataframe(
            pares.drop(columns="Forca"),
            hide_index=True
        )

        # Criar um nome para cada par de indicadores
        pares["Indicadores"] = (
            pares["Variável 1"] + " x " + pares["Variável 2"]
        )

        # Criar o gráfico de barras
        fig = px.bar(
            pares,
            x="Correlação",
            y="Indicadores",
            orientation="h",
            title="Correlações entre os indicadores",
            text="Correlação"
        )

        # Melhorar a apresentação do gráfico
        fig.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Correlação de Pearson",
            yaxis_title="",
            yaxis=dict(autorange="reversed")
        )

        st.plotly_chart(fig, use_container_width=True)

        # Análise das correlações conforme os filtros
        st.write("**Análise dos indicadores:**")

        if not pares.empty:
            # Identificar o par com maior correlação absoluta
            maior_par = pares.iloc[0]

            variavel1 = maior_par["Variável 1"]
            variavel2 = maior_par["Variável 2"]
            valor = maior_par["Correlação"]

            # Identificar o período selecionado
            ano_inicial = df["ano"].min()
            ano_final = df["ano"].max()

            if ano_inicial == ano_final:
                periodo = str(ano_inicial)
            else:
                periodo = f"{ano_inicial} a {ano_final}"

            # Identificar se a correlação é positiva ou negativa
            if valor > 0:
                tipo = "positiva"
            elif valor < 0:
                tipo = "negativa"
            else:
                tipo = "nula"

            # Mostrar a interpretação
            st.write(
                f"No período selecionado ({periodo}), "
                f"a maior correlação absoluta foi entre {variavel1} "
                f"e {variavel2}, com valor de {valor:.2f}. "
                f"Essa correlação é {tipo}. "
                "O resultado indica uma associação estatística "
                "entre os indicadores, mas não comprova "
                "uma relação de causa e efeito."
            )
        else:
            st.info("Não há correlações suficientes para analisar.")

# Botão para baixar os dados filtrados
st.download_button(
    "Baixar dados filtrados (CSV)",
    df.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
    file_name="macro_filtrado.csv",
    mime="text/csv"
)

