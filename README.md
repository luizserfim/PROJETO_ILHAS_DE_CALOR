# Simulador de Ilhas de Calor Urbanas — Baturité/CE

Aplicativo educacional em Python e Streamlit para comparar coberturas do solo e intervenções urbanas. Os pesos são didáticos, sem calibração experimental para os bairros de Baturité. Os resultados não são previsões meteorológicas nem medições locais.

## Instalação e execução

Use Python 3.12 ou superior. A revisão foi testada com Python 3.12 no Windows; outras versões precisam ser verificadas no ambiente de destino.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run main.py
```

As dependências diretas estão fixadas nas versões usadas nesta revisão. `requirements-lock.txt` inclui também as dependências transitivas do aplicativo, para repetir o ambiente testado. Esse arquivo é destinado ao ambiente Windows/Python 3.12 usado na validação.

## Uso

1. Informe o nome da região (até 100 caracteres).
2. Ajuste vegetação, pavimento, edificações, solo exposto e água para somar 100%.
3. Use a referência FUNCEME ou informe a temperatura manual quando a fonte estiver indisponível.
4. Escolha a superfície a converter em vegetação e observe a comparação.
5. Salve até 50 cenários na sessão. “Nova análise” reinicia o formulário; “Limpar cenários salvos” remove a lista da sessão.

Os cenários são temporários e não são gravados em disco. O nome da região é texto de exibição e não determina as características físicas da área.

## Modelo

`I = (-0,35 V + 0,40 P + 0,30 E + 0,15 S - 0,20 A) / 100`

`ΔT = limitar(10 I, -2, +3)` e `T_simulada = T_referência + ΔT`.

A referência aceita valores entre -90 e 60 °C, como limite amplo de validação. Coberturas devem estar entre 0 e 100, totalizando 100 com tolerância máxima de 0,01 ponto percentual. Booleanos, textos, NaN e infinitos são rejeitados. Pesos personalizados devem conter as cinco classes e valores finitos entre -1 e 1. A interface permite converter até 50 pontos percentuais por intervenção, respeitando a área disponível.

## Dados da FUNCEME

O cliente usa exclusivamente o endpoint HTTPS fixo e a estação 35852 (Baturité - APA), período de 24 horas. A validação TLS permanece habilitada. Redirecionamentos não são seguidos. A consulta tem timeout de conexão de 5 segundos e de leitura de 10 segundos, limite de 2 MB descomprimidos e de 10.000 registros. Há verificação de prazo de 20 segundos entre blocos; isso não representa um prazo total rígido, pois uma leitura em andamento ainda depende do timeout de leitura.

A referência usa a última observação completa com mínima ≤ média ≤ máxima. Registros inválidos são descartados; conflitos no mesmo sensor/horário invalidam a resposta. Observações com mais de 3 horas ou mais de 15 minutos no futuro acionam a entrada manual. Horários sem offset são interpretados como America/Fortaleza, hipótese que deve ser confirmada com o contrato oficial da API antes de uso científico. Máxima e mínima são da observação horária, não do dia.

Sucessos e indisponibilidades são cacheados por 10 minutos. A aplicação não expõe detalhes das exceções de transporte na interface. Os testes da integração usam respostas simuladas e não demonstram disponibilidade do serviço externo.

## Testes e auditoria

```powershell
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m unittest discover -s tests -v
.\.venv\Scripts\python -m bandit -r main.py models services components config
.\.venv\Scripts\python -m pip_audit -r requirements-lock.txt
```

A suíte cobre o modelo original, entradas adversariais, 500 cenários com três tipos de intervenção, respostas meteorológicas simuladas e fluxos da interface com AppTest. Não acessa a FUNCEME durante os testes. A auditoria de dependências precisa de internet e reflete apenas as vulnerabilidades conhecidas na data da consulta.

## Estrutura

- `main.py`: interface e estado da sessão.
- `models/modelo_termico.py`: cálculo e validação do modelo.
- `config/model_config.py`: parâmetros didáticos.
- `services/funceme.py`: consulta limitada e validação dos dados externos.
- `components/styles.py`: CSS estático; não recebe HTML do usuário.
- `tests/`: testes automatizados do modelo, serviço e interface.

Nenhum arquivo `.pyc` é necessário para distribuir ou executar o projeto. Não use binários de origem desconhecida. Para publicação pública, mantenha as proteções padrão do Streamlit, TLS e limites de recursos no provedor. A revisão do código não equivale a um teste de invasão de uma implantação pública.
