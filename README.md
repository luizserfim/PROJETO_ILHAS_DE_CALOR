🌍 Simulador de Ilhas de Calor Urbanas — Baturité-CE

Simulador computacional educacional desenvolvido em Python e Streamlit para investigar a influência da cobertura do solo sobre o comportamento térmico urbano no município de Baturité, Ceará.

A ferramenta utiliza dados meteorológicos da FUNCEME como temperatura de referência e permite construir cenários personalizados de ocupação do solo, comparar resultados e simular intervenções urbanas.

Importante: o modelo possui finalidade didática. As temperaturas calculadas são estimativas computacionais para comparação de cenários e não medições diretas dos bairros de Baturité.

🎯 Objetivo

O projeto busca explorar, de maneira interativa, como diferentes formas de cobertura do solo podem influenciar o comportamento térmico de uma região urbana.

O usuário informa uma região de interesse e estima as porcentagens de:

vegetação;

pavimento;

edificações;

solo exposto;

água.

A partir desses dados, o simulador calcula um Índice Térmico Urbano Didático, estima uma anomalia térmica em relação à temperatura meteorológica de referência e permite testar intervenções urbanas.

🛠️ Tecnologias utilizadas

Python — linguagem de programação;

Streamlit — interface interativa;

Matplotlib — geração dos gráficos;

Pandas — organização e apresentação de dados;

Requests — consulta dos dados meteorológicos;

unittest — testes automatizados do modelo.

📁 Estrutura do projeto

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
│   ├── geospatial.py
│   ├── landsat_service.py
│   └── landsat_lst.py
├── tests/
│   └── test_modelo_termico.py
├── main.py
├── README.md
├── requirements.txt
└── .gitignore

Os recursos geoespaciais e de sensoriamento remoto permanecem no projeto como base para possíveis expansões futuras. Eles não fazem parte do funcionamento principal da versão atual do simulador.

🌡️ Funcionamento do simulador

1. Região analisada

O usuário informa o nome da região que deseja estudar, como um bairro, praça, comunidade ou outra área de interesse.

O nome da região não determina automaticamente suas características térmicas. O resultado depende das porcentagens de cobertura do solo informadas pelo usuário.

2. Cobertura do solo

A interface possui barras deslizantes para definir as porcentagens de:

🌳 vegetação;

🛣️ pavimento;

🏢 edificações;

🟫 solo exposto;

💧 água.

A soma das cinco categorias deve ser igual a 100% para que a simulação seja executada.

As porcentagens podem ser estimadas a partir da observação da região, mapas, imagens de satélite ou outras fontes adequadas ao estudo.

3. Temperatura meteorológica de referência

O simulador consulta automaticamente dados da estação Baturité - APA, da Fundação Cearense de Meteorologia e Recursos Hídricos (FUNCEME).

A temperatura obtida funciona como referência meteorológica para o modelo e não representa automaticamente a temperatura de todos os bairros ou regiões de Baturité.

Caso a consulta automática não esteja disponível, o programa permite informar manualmente uma temperatura de referência.

🧮 Modelo térmico didático

O simulador utiliza o seguinte Índice Térmico Urbano Didático:

$$
I_T = \frac{-0{,}35V + 0{,}40P + 0{,}30E + 0{,}15S - 0{,}20A}{100}
$$

em que:

V = porcentagem de vegetação;

P = porcentagem de pavimento;

E = porcentagem de edificações;

S = porcentagem de solo exposto;

A = porcentagem de água.

A anomalia térmica é calculada por:

$$
\Delta T = 10I_T
$$

O resultado é limitado ao intervalo:

$$
-2,^\circ\mathrm{C} \leq \Delta T \leq 3,^\circ\mathrm{C}
$$

Finalmente, a temperatura simulada é calculada por:

$$
T_{\mathrm{simulada}} = T_{\mathrm{referência}} + \Delta T
$$

Interpretação dos parâmetros

No modelo:

vegetação possui contribuição térmica negativa;

água possui contribuição térmica negativa;

pavimento possui contribuição térmica positiva;

edificações possuem contribuição térmica positiva;

solo exposto possui contribuição térmica positiva.

Os pesos são parâmetros de um modelo didático simplificado. Eles não representam coeficientes experimentais medidos nos bairros de Baturité.

🌳 Simulação de intervenções urbanas

O sistema permite comparar o cenário atual com três intervenções simplificadas:

Pavimento → Vegetação

Solo exposto → Vegetação

Edificações → Vegetação

O usuário escolhe quantos pontos percentuais deseja converter em vegetação.

Após a intervenção, o simulador recalcula:

composição da cobertura do solo;

índice térmico;

anomalia térmica;

temperatura simulada;

redução térmica estimada.

Os gráficos permitem visualizar a diferença entre o cenário original e o cenário após a intervenção.

💾 Cenários personalizados

O usuário pode salvar temporariamente diferentes cenários durante a execução do aplicativo.

Cada cenário armazena:

nome da região;

porcentagem de vegetação;

porcentagem de pavimento;

porcentagem de edificações;

porcentagem de solo exposto;

porcentagem de água.

A opção Nova análise reinicia o formulário para estudar outra região, enquanto os cenários anteriores permanecem disponíveis durante a sessão.

Os cenários são armazenados apenas no estado da sessão do Streamlit e, portanto, não possuem armazenamento permanente.

🖥️ Interface

O aplicativo está organizado em quatro abas:

📖 Introdução

Apresenta a proposta e o objetivo geral do projeto.

📚 Fundamentação Teórica

Apresenta conceitos relacionados às Ilhas de Calor Urbanas, cobertura do solo, vegetação, urbanização e temperatura de referência.

🌡️ Simulador

Reúne os controles de entrada, consulta meteorológica, cálculo térmico, intervenções e gráficos.

📊 Metodologia e Resultados

Apresenta o modelo matemático, os dados utilizados, a validação computacional e as limitações da ferramenta.

✅ Validação computacional

O modelo possui testes automatizados em:

tests/test_modelo_termico.py

Foram executados 10 testes, todos aprovados.

Os testes verificam:

soma das coberturas igual a 100%;

rejeição de porcentagens inválidas;

comportamento do cenário padrão;

redução térmica com aumento da vegetação;

funcionamento das intervenções;

preservação dos 100% de cobertura após uma intervenção;

impedimento de conversões maiores que a área disponível;

limite superior da anomalia térmica;

limite inferior da anomalia térmica.

Para executar os testes:

python -m unittest tests.test_modelo_termico -v

Resultado esperado:

Ran 10 tests
OK

🚀 Como executar

1. Instalar as dependências

Dentro da pasta do projeto:

pip install -r requirements.txt

2. Executar os testes

python -m unittest tests.test_modelo_termico -v

3. Iniciar o aplicativo

streamlit run main.py

O Streamlit abrirá o aplicativo no navegador.

⚠️ Limitações

O projeto deve ser interpretado como uma ferramenta educacional de simulação de cenários.

Entre suas principais limitações:

as temperaturas simuladas não correspondem a medições diretas dos bairros;

uma observação meteorológica é utilizada como referência para os cenários;

as porcentagens de cobertura do solo são informadas ou estimadas pelo usuário;

os pesos térmicos não foram calibrados experimentalmente para cada região de Baturité;

o modelo não substitui medições de campo, estações meteorológicas ou produtos científicos de temperatura de superfície;

os cenários salvos durante a execução não possuem persistência permanente.

Os resultados devem ser utilizados principalmente para comparar cenários e investigar tendências, e não como previsão meteorológica.

🔭 Possíveis desenvolvimentos futuros

A estrutura do projeto permite futuras expansões, como:

mapas interativos;

delimitação espacial das regiões analisadas;

integração com dados de sensoriamento remoto;

uso de imagens Landsat;

estimativa automática da cobertura do solo;

comparação com medições de campo;

calibração dos parâmetros térmicos;

armazenamento permanente dos cenários;

comparação espacial entre diferentes regiões de Baturité.

📌 Considerações finais

O Simulador de Ilhas de Calor Urbanas oferece uma forma interativa de explorar relações entre urbanização, cobertura vegetal e comportamento térmico.

A proposta permite que estudantes construam seus próprios cenários, modifiquem características da superfície e observem como essas alterações afetam os resultados do modelo, aproximando conceitos de Física, climatologia urbana, análise de dados e programação de situações relacionadas ao espaço urbano de Baturité.