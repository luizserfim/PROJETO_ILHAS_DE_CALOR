# 🌍 Simulador de Ilhas de Calor Urbanas --- Baturité-CE

## Introdução

O crescimento e a transformação das áreas urbanas modificam as
características naturais da superfície, principalmente pela substituição
da vegetação por edificações, pavimentos e outras superfícies
impermeáveis. Essas alterações podem contribuir para diferenças térmicas
entre regiões com diferentes formas de ocupação do solo.

Este projeto apresenta um **simulador computacional de Ilhas de Calor
Urbanas para o município de Baturité, Ceará**, desenvolvido em Python
com interface em Streamlit. A ferramenta utiliza dados meteorológicos da
**FUNCEME** como temperatura de referência e permite que o usuário
construa cenários próprios a partir das características de cobertura do
solo da região que deseja analisar.

O projeto possui finalidade **educacional** e busca integrar Física,
climatologia urbana, análise de dados e programação.

## Objetivo

O objetivo do simulador é permitir a investigação da influência de
diferentes tipos de cobertura do solo sobre o comportamento térmico de
uma região urbana.

O usuário pode informar uma área de interesse e estimar as porcentagens
de:

-   vegetação;
-   pavimento;
-   edificações;
-   solo exposto;
-   água.

A partir dessas informações, o sistema calcula um índice térmico
didático, estima uma anomalia térmica em relação à temperatura
meteorológica de referência e permite testar intervenções urbanas.

## Tecnologias utilizadas

O projeto utiliza principalmente:

-   **Python** --- linguagem de programação;
-   **Streamlit** --- construção da interface interativa;
-   **Matplotlib** --- geração dos gráficos;
-   **Requests** --- consulta de dados meteorológicos;
-   **unittest** --- testes automatizados do modelo.

## Estrutura do projeto

A organização principal é:

``` text
ILHAS_DE-CALOR/
├── components/
│   ├── __init__.py
│   └── styles.py
├── config/
│   ├── __init__.py
│   └── model_config.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── calibration/
├── Documentacao/
├── models/
│   ├── __init__.py
│   └── modelo_termico.py
├── services/
│   ├── __init__.py
│   ├── funceme.py
│   └── geospatial.py
├── tests/
│   └── test_modelo_termico.py
├── main.py
├── README.md
├── requirements.txt
└── .gitignore
```

Os arquivos experimentais relacionados a sensoriamento remoto podem
permanecer no repositório para estudos futuros, mas **não fazem parte do
funcionamento principal atual do simulador**.

## Funcionamento do simulador

### 1. Definição da região

O usuário informa o nome da região que deseja analisar, como um bairro,
praça, comunidade ou outra área de interesse.

Não são atribuídas automaticamente características térmicas a nomes de
bairros. O comportamento do cenário depende das porcentagens de
cobertura informadas pelo próprio usuário.

### 2. Cobertura do solo

A interface utiliza barras deslizantes para definir as porcentagens de:

-   vegetação;
-   pavimento;
-   edificações;
-   solo exposto;
-   água.

A soma deve ser igual a **100%** para que o cálculo seja realizado.

Os valores podem ser estimados pelo usuário a partir de observações da
região, mapas, imagens de satélite ou outras fontes adequadas ao estudo.

### 3. Temperatura meteorológica de referência

O sistema consulta automaticamente dados da estação **Baturité - APA**,
da Fundação Cearense de Meteorologia e Recursos Hídricos (FUNCEME).

A temperatura obtida funciona como **referência meteorológica** para o
modelo. Ela não representa automaticamente a temperatura de todos os
bairros ou regiões de Baturité.

Caso a consulta automática não esteja disponível, o programa permite
utilizar uma temperatura de referência informada manualmente.

## Modelo térmico didático

O simulador utiliza um **Índice Térmico Urbano Didático**, definido por:

``` text
I_T = (-0,35V + 0,40P + 0,30E + 0,15S - 0,20A) / 100
```

em que:

-   `V` = porcentagem de vegetação;
-   `P` = porcentagem de pavimento;
-   `E` = porcentagem de edificações;
-   `S` = porcentagem de solo exposto;
-   `A` = porcentagem de água.

A anomalia térmica é calculada por:

``` text
ΔT = 10 × I_T
```

O resultado é limitado ao intervalo:

``` text
-2 °C ≤ ΔT ≤ +3 °C
```

Finalmente:

``` text
T_simulada = T_referência + ΔT
```

### Interpretação

No modelo:

-   vegetação possui contribuição térmica negativa;
-   água possui contribuição térmica negativa;
-   pavimento possui contribuição positiva;
-   edificações possuem contribuição positiva;
-   solo exposto possui contribuição positiva.

Os pesos utilizados são **parâmetros de um modelo didático
simplificado**. Eles não devem ser interpretados como coeficientes
experimentais medidos nos bairros de Baturité.

## Simulação de intervenções urbanas

O sistema permite comparar o cenário atual com três intervenções
simplificadas:

1.  **Pavimento → Vegetação**
2.  **Solo exposto → Vegetação**
3.  **Edificações → Vegetação**

O usuário escolhe quantos pontos percentuais deseja converter em
vegetação.

O simulador então recalcula:

-   composição da cobertura do solo;
-   índice térmico;
-   anomalia térmica;
-   temperatura simulada;
-   redução térmica estimada.

Os gráficos permitem comparar o cenário original com o cenário após a
intervenção.

## Cenários personalizados

O usuário pode salvar temporariamente diferentes cenários durante a
utilização do aplicativo.

Por exemplo, podem ser cadastradas regiões como:

``` text
Centro
Praça da cidade
Comunidade A
Entorno da escola
```

Cada cenário armazena as porcentagens de cobertura informadas.

A opção **Nova análise** reinicia o formulário para que outra região
seja estudada, enquanto os cenários anteriores permanecem disponíveis
durante a sessão.

Esses dados são armazenados somente no estado da sessão do Streamlit.
Portanto, **não constituem armazenamento permanente** e são perdidos
quando a sessão/aplicação é encerrada ou reiniciada.

## Interface

O aplicativo está organizado em quatro áreas:

### 📖 Introdução

Apresenta a proposta e o objetivo geral do projeto.

### 📚 Fundamentação Teórica

Apresenta conceitos básicos relacionados às Ilhas de Calor Urbanas,
cobertura do solo, vegetação, urbanização e temperatura de referência.

### 🌡️ Simulador

Contém os controles de entrada, consulta meteorológica, cálculo térmico,
intervenções e visualizações.

### 📊 Metodologia e Resultados

Apresenta o modelo matemático, os dados utilizados, a validação
computacional e as limitações da ferramenta.

## Validação computacional

O modelo possui uma suíte automatizada de testes em:

``` text
tests/test_modelo_termico.py
```

Foram executados **10 testes**, todos aprovados.

Os testes verificam, entre outros aspectos:

-   cobertura total igual a 100%;
-   rejeição de valores inválidos;
-   comportamento do cenário padrão;
-   redução térmica com aumento da vegetação;
-   funcionamento da intervenção;
-   preservação dos 100% após a intervenção;
-   impedimento de conversões maiores que a área disponível;
-   limite superior da anomalia térmica;
-   limite inferior da anomalia térmica.

Para executar os testes:

``` powershell
python -m unittest tests.test_modelo_termico -v
```

O resultado esperado é:

``` text
Ran 10 tests
OK
```

## Como executar

### 1. Instalar as dependências

No terminal, dentro da pasta do projeto:

``` powershell
pip install -r requirements.txt
```

### 2. Executar os testes

``` powershell
python -m unittest tests.test_modelo_termico -v
```

### 3. Iniciar o aplicativo

``` powershell
streamlit run main.py
```

O Streamlit abrirá o aplicativo no navegador.

## Limitações

Este projeto deve ser interpretado como uma ferramenta **educacional e
de simulação de cenários**.

As principais limitações são:

-   as temperaturas simuladas não correspondem a medições diretas dos
    bairros;
-   uma única observação meteorológica é utilizada como referência para
    os cenários;
-   as porcentagens de cobertura são informadas ou estimadas pelo
    usuário;
-   os pesos térmicos não foram calibrados experimentalmente para cada
    região de Baturité;
-   o modelo não substitui medições de campo, estações meteorológicas ou
    produtos científicos de temperatura de superfície;
-   os cenários salvos no aplicativo não possuem persistência
    permanente.

Por isso, os resultados devem ser utilizados principalmente para
**comparar cenários e investigar tendências**, e não como previsão
meteorológica.

## Possíveis desenvolvimentos futuros

O projeto pode futuramente incorporar:

-   mapas interativos;
-   delimitação espacial de regiões;
-   dados de sensoriamento remoto;
-   estimativas de cobertura do solo obtidas automaticamente;
-   medições de campo para comparação com o modelo;
-   calibração dos parâmetros térmicos;
-   armazenamento permanente dos cenários;
-   comparação espacial entre diferentes regiões de Baturité.

Esses recursos são possibilidades de expansão e **não devem ser
confundidos com funcionalidades já implementadas**.

## Considerações finais

O Simulador de Ilhas de Calor Urbanas busca oferecer uma forma simples e
interativa de explorar a relação entre urbanização, cobertura vegetal e
comportamento térmico.

A proposta permite que estudantes construam seus próprios cenários,
modifiquem as características da superfície e observem como essas
alterações afetam os resultados do modelo. Dessa forma, a ferramenta
aproxima conceitos de Física, climatologia urbana e programação de
situações relacionadas ao espaço urbano de Baturité.

> **Importante:** o modelo é didático. Os resultados representam
> estimativas computacionais para comparação de cenários e não medições
> meteorológicas diretas das regiões analisadas.
#   P R O J E T O _ I L H A S _ D E _ C A L O R  
 