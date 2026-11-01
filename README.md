# Projeto Final — Análise de Indicadores Macroeconômicos do Brasil

**Curso:** Visualização de Dados e Business Intelligence — SCTec  
**Aluna:** Zaira Nanci Zatelli Wendt  
**Turma:** 2  
**Período analisado:** 2019 a 2023  

## 1. Sobre o projeto

Este projeto foi desenvolvido como atividade final do curso de Visualização de Dados e Business Intelligence.

O objetivo é analisar indicadores macroeconômicos brasileiros entre 2019 e 2023, utilizando dados públicos do Banco Central do Brasil.

A análise busca compreender o comportamento dos juros, da inflação, do câmbio e da atividade econômica, por meio de consultas SQL, gráficos interativos e indicadores.

## 2. Fonte dos dados

Os dados foram coletados da API SGS do Banco Central do Brasil (BACEN).

Foram utilizadas cinco séries:

| Indicador | Código SGS |
|---|---|
| Selic Meta | 432 |
| IPCA mensal | 433 |
| IPCA acumulado em 12 meses | 13522 |
| Dólar PTAX | 1 |
| IBC-Br dessazonalizado | 24364 |

Fonte: https://dadosabertos.bcb.gov.br/

**Período analisado:** 01/01/2019 a 31/12/2023.

**Origem e utilização dos dados:** os indicadores foram obtidos de séries públicas disponibilizadas pelo Banco Central do Brasil por meio da API SGS. Os dados foram utilizados para fins educacionais, com identificação da fonte oficial. As condições de reutilização e eventual licença específica devem ser consultadas no Portal de Dados Abertos do Banco Central.

## 3. Ferramentas utilizadas

- **Python e Pandas:** utilizados para coletar, limpar, organizar e analisar os dados.
- **Requests:** utilizado para acessar a API pública do Banco Central.
- **SQLite e SQL:** utilizados para armazenar os dados em tabelas e realizar consultas.
- **Plotly:** utilizado para criar gráficos interativos que facilitam a visualização dos indicadores.
- **Streamlit:** utilizado para desenvolver o dashboard e permitir a interação com os dados.
- **Git e GitHub:** utilizados para registrar as alterações do projeto e organizar o desenvolvimento por branches.
- **Trello:** utilizado para planejar e acompanhar as atividades por meio do quadro Kanban.

## 4. Coleta e tratamento dos dados (ETL)

A coleta e a preparação dos dados foram realizadas no arquivo `src/etl.py`.

As principais etapas foram:

1. Coleta das cinco séries do BACEN.
2. Conversão das datas e dos valores numéricos.
3. Verificação de datas inválidas, valores ausentes e registros duplicados.
4. Padronização dos dados para frequência mensal.
5. Utilização do último valor disponível do mês para as séries diárias, como Selic e dólar.
6. União das cinco séries em uma única base.
7. Criação das colunas de ano, juro real estimado, variação mensal do dólar e IPCA acumulado observado três meses depois.
8. Exportação dos dados tratados para `data/macro_tratado.csv`.

A base final contém **60 registros mensais**, de janeiro de 2019 a dezembro de 2023.

Na validação, não foram identificados valores ausentes nos cinco indicadores principais.

Foram encontrados quatro valores ausentes nas colunas calculadas, considerados esperados:

- Um na variação mensal do dólar, por não existir mês anterior na base.
- Três no IPCA observado três meses depois, porque a base termina em dezembro de 2023.

### 4.1. Dicionário de Dados

A base tratada contém os indicadores econômicos coletados do Banco Central e algumas colunas calculadas durante o tratamento dos dados.

| Coluna | Tipo de dado | Descrição |
|---|---|---|
| `data` | Data (datetime) | Mês de referência dos indicadores. |
| `selic` | Decimal (float) | Taxa Selic Meta, em percentual ao ano. |
| `ipca_mensal` | Decimal (float) | Variação mensal do IPCA, em percentual. |
| `ipca_12m` | Decimal (float) | Inflação acumulada em 12 meses, em percentual. |
| `dolar` | Decimal (float) | Cotação de venda do dólar PTAX, em reais. |
| `ibc_br` | Decimal (float) | Índice de atividade econômica do Banco Central, dessazonalizado. |
| `juro_real` | Decimal (float) | Estimativa do juro real calculada com a Selic e o IPCA acumulado em 12 meses, utilizando a fórmula de Fisher. |
| `ano` | Inteiro (int) | Ano extraído da coluna `data`. |
| `variacao_dolar_pct` | Decimal (float) | Variação percentual do dólar em relação ao mês anterior. |
| `ipca_12m_prox_3m` | Decimal (float) | IPCA acumulado em 12 meses observado três meses depois, utilizado na análise de correlação. |

**Regras de tratamento e cálculo:**

- As datas foram convertidas para o formato datetime.
- Os valores dos indicadores foram convertidos para números.
- As séries foram organizadas mensalmente, utilizando o último valor disponível de cada mês.
- O juro real estimado foi calculado pela fórmula de Fisher.
- A variação do dólar foi calculada em relação ao mês anterior.
- A coluna `ipca_12m_prox_3m` foi criada deslocando o IPCA acumulado em 12 meses três posições para o futuro.

## 5. Banco de dados e consultas SQL

Foi utilizado o banco SQLite para armazenar os dados tratados.

O banco possui duas tabelas:

- `dim_tempo`: contém data, ano e mês.
- `fato_indicadores`: contém os indicadores econômicos e as colunas calculadas.

Foram criadas cinco consultas SQL para analisar:

1. Indicadores econômicos por mês.
2. Média anual da Selic.
3. Meses em que o dólar ficou acima da média histórica.
4. Comparação entre Selic, IPCA acumulado e juro real estimado.
5. Média anual do IBC-Br.

As duas tabelas foram carregadas com 60 registros cada, e as cinco consultas foram executadas com sucesso.

## 6. Perguntas de negócio

O projeto busca responder às seguintes perguntas:

1. Como a Selic evoluiu entre 2019 e 2023 e em quais momentos o juro real estimado apresentou os maiores valores?
2. Como o dólar PTAX se comportou e em quais períodos ficou acima da média histórica?
3. Existe correlação entre a variação do dólar e a inflação, inclusive considerando três meses de diferença?
4. Como o IBC-Br se comportou durante os períodos de aumento e redução da Selic?
5. Quais indicadores apresentaram as maiores correlações lineares de Pearson?

## 7. Dashboard Streamlit

Foi desenvolvido um dashboard interativo no arquivo `app.py`.

O painel está dividido em quatro abas:

**Aba 1 — Juros e inflação**

Apresenta a evolução da Selic, do IPCA acumulado em 12 meses e do juro real estimado, além dos meses com maiores juros reais e uma análise dos resultados.

**Aba 2 — Câmbio**

Apresenta a trajetória do dólar PTAX, a média histórica do período, um gráfico de dispersão entre dólar e inflação e análises das correlações.

**Aba 3 — Atividade econômica**

Apresenta a evolução do IBC-Br, os maiores e menores valores do indicador e uma análise comparativa com a Selic.

**Aba 4 — Correlações**

Apresenta a matriz de correlação de Pearson, uma tabela com os pares de indicadores, um gráfico de barras e uma interpretação automática da maior correlação absoluta.

## 8. Indicadores estratégicos (KPIs)

O dashboard apresenta quatro indicadores principais:

- Selic Meta.
- IPCA acumulado em 12 meses.
- Juro real estimado.
- Dólar PTAX.

Os indicadores apresentam o valor mais recente do período selecionado e a variação em relação ao registro anterior disponível.

O juro real foi estimado utilizando a fórmula de Fisher, com a Selic Meta e o IPCA acumulado em 12 meses.

## 9. Interatividade

O dashboard permite:

- Filtrar os dados por ano.
- Selecionar um intervalo de datas.
- Escolher as variáveis utilizadas na matriz de correlação.
- Restaurar os filtros.
- Visualizar gráficos e análises atualizados conforme a seleção.
- Baixar os dados filtrados em CSV, com separador e formato decimal adequados ao Excel brasileiro.

### 9.1. Demonstração do Dashboard

O dashboard foi desenvolvido no Streamlit e permite acompanhar os indicadores macroeconômicos de forma interativa.

**Tela principal da aplicação:**

![Dashboard de indicadores macroeconômicos](imagens/dashboard_geral.png)

**Como navegar pelo dashboard:**

- **Filtros laterais:** permitem selecionar os anos, o período de análise e as variáveis utilizadas nas correlações.
- **Aba Juros e inflação:** apresenta a evolução da Selic, do IPCA acumulado em 12 meses e do juro real estimado.
- **Aba Câmbio:** apresenta o comportamento do dólar, a média histórica e a relação entre câmbio e inflação.
- **Aba Atividade:** apresenta a evolução do IBC-Br e sua comparação com a Selic.
- **Aba Correlações:** apresenta a matriz de Pearson e a comparação das correlações entre os indicadores.

A aplicação também permite restaurar os filtros e baixar os dados filtrados em CSV.

## 10. Principais resultados

Durante a análise, foram observados alguns comportamentos importantes:

- O juro real estimado apresentou seu maior valor em junho de 2023, aproximadamente 10,27%.
- O IBC-Br apresentou uma queda acentuada em abril de 2020 e recuperação nos anos seguintes.
- Na análise de 2019 a 2023 com as quatro variáveis principais selecionadas, a maior correlação observada foi entre Selic e IBC-Br, aproximadamente 0,73.
- Os coeficientes de correlação mudaram quando foram selecionados períodos diferentes, demonstrando a importância de considerar o intervalo analisado.

Esses resultados são descritivos e não comprovam relações de causa e efeito.

## 11. Limitações da análise

O projeto possui algumas limitações:

- A análise considera somente o período de 2019 a 2023.
- Os dados foram padronizados para frequência mensal.
- Para séries originalmente diárias, foi utilizado o último valor disponível de cada mês.
- O juro real apresentado é uma estimativa, e não o retorno real efetivamente observado em um investimento.
- As correlações indicam associações estatísticas, mas não comprovam causalidade.
- A comparação do dólar com a inflação três meses depois utiliza valores futuros previamente calculados na base completa.
- A análise utiliza indicadores agregados, sem considerar todos os fatores que podem influenciar a economia.

### 11.1. Aplicação Profissional

O dashboard pode ser utilizado por analistas e gestores financeiros para acompanhar o comportamento dos principais indicadores macroeconômicos brasileiros.

A análise da Selic, inflação e câmbio pode ajudar no planejamento financeiro, na avaliação de custos e na compreensão do cenário econômico.

O acompanhamento do IBC-Br também permite observar mudanças na atividade econômica, enquanto os gráficos de correlação ajudam a identificar possíveis associações entre os indicadores.

Essas informações podem apoiar decisões de planejamento e análise de riscos, mas devem ser utilizadas em conjunto com outros dados e avaliações.

## 12. Como executar o projeto

Primeiro, é necessário instalar as dependências Python indicadas no arquivo `requirements.txt`.

Na pasta principal do projeto, execute o ETL:

```bash
python -m src.etl
```

Depois, crie e carregue o banco SQLite e execute as consultas:

```bash
python -m src.banco
```

Para iniciar o dashboard:

```bash
streamlit run app.py
```

O dashboard tenta utilizar uma conexão SQL configurada e, caso não esteja disponível, carrega o arquivo local `data/macro_tratado.csv`.

### 12.1. Estrutura de Pastas

O projeto foi organizado em pastas para separar os dados, os códigos de tratamento, as consultas SQL e a aplicação Streamlit.

```text
projeto_macro_bacen/
├── data/                # Arquivos de dados brutos e tratados
├── imagens/             # Imagem do quadro Trello
├── notebooks/           # Análises e testes realizados
├── sql/                 # Scripts de criação e consultas SQL
├── src/                 # Scripts Python de ETL e banco de dados
├── .streamlit/          # Configurações do Streamlit
├── app.py               # Dashboard interativo
├── requirements.txt     # Bibliotecas necessárias
├── .gitignore           # Arquivos ignorados pelo Git
└── README.md            # Documentação do projeto
```

Essa organização facilita a localização dos arquivos e a manutenção do projeto.


## 13. Organização e versionamento

O desenvolvimento do projeto foi organizado utilizando Trello e GitHub.

No Trello, as atividades foram distribuídas entre as etapas Backlog, A fazer, Em andamento e Concluído, permitindo acompanhar o andamento do projeto.

No GitHub, foram utilizadas branches para separar o desenvolvimento das funcionalidades, as correções e a versão principal da aplicação.

As alterações foram registradas por meio de commits e Pull Requests, utilizando as branches `develop` e `main`.

**Repositório GitHub:** https://github.com/Znanc/projeto-final-indicadores-bacen

**Pull Requests:** https://github.com/Znanc/projeto-final-indicadores-bacen/pulls?q=is%3Apr+is%3Aclosed

**Quadro Trello:** [Projeto Final — BI Macroeconômico BACEN](https://trello.com/b/NCqtPMVQ/projeto-final-bi-macroeconomico-bacen)

**Imagem do Trello:**

![Organização das atividades no Trello](imagens/trello_projeto.png)


## 14. Publicação 

O dashboard foi publicado no Streamlit Community Cloud, utilizando o repositório do GitHub, a branch main e o arquivo app.py.

Aplicação publicada: https://indicadores-macro-bacen.streamlit.app

Após a publicação, foram realizados testes dos filtros, gráficos e indicadores. Também foram feitos ajustes nos nomes dos indicadores para facilitar a leitura das informações.

As alterações foram registradas no GitHub utilizando branches e Pull Requests, seguindo o fluxo de desenvolvimento adotado no projeto.

A aplicação utiliza o arquivo data/macro_tratado.csv como alternativa quando não há conexão com o banco SQL configurada.

## 15. Referências

- Banco Central do Brasil — Portal de Dados Abertos: https://dadosabertos.bcb.gov.br/
- Banco Central do Brasil — Sistema Gerenciador de Séries Temporais (SGS): https://www3.bcb.gov.br/sgspub/
- Documentação do Streamlit: https://docs.streamlit.io/
- Documentação do Pandas: https://pandas.pydata.org/docs/
- Documentação do Plotly: https://plotly.com/python/