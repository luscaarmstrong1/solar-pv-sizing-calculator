# Calculadora de Dimensionamento Fotovoltaico

Ferramenta de portfólio para pré-dimensionamento de sistemas fotovoltaicos conectados à rede, desenvolvida em Python, Excel e Streamlit.

## Resultado do Cenário Base

- Potência requerida: 4.98 kWp
- Potência instalada: 5.50 kWp
- Módulos: 10 x 550 Wp
- Inversor: 6.00 kW
- Strings: MPPT 1: 10 módulos; MPPT 2: sem strings
- CC/CA: 0.92
- Geração anual: 7892 kWh
- Área técnica: 31.0 m²
- Status: OK

## O Que a Ferramenta Calcula

- Consumo anual, consumo médio mensal e consumo médio diário.
- HSP média ponderada pelos dias de cada mês.
- Performance Ratio por entrada direta ou por composição multiplicativa de perdas.
- Potência FV requerida, quantidade inteira de módulos e potência CC instalada.
- Relação CC/CA com faixa preliminar configurável.
- Área ocupada pelos módulos e área técnica estimada.
- Geração mensal, excedente, déficit e atendimento mensal.
- Dimensionamento inteiro de strings sem criação de módulos fictícios.
- Voc em frio, Vmp em quente, Vmp em frio, tensão de partida e janela MPPT.
- Corrente operacional e corrente de curto-circuito por entrada e por MPPT.

## Tecnologias

- Python para o motor de cálculo e testes automatizados.
- Streamlit para demonstração interativa.
- Excel para planilha auditável com fórmulas e gráficos.
- Pytest para validação dos casos técnicos.

## Como Rodar

```bash
pip install -r requirements.txt
python scripts/run_sizing.py
streamlit run app.py
```

## Limitações

O projeto é preliminar e demonstrativo. Não substitui projeto executivo, vistoria de campo, estudo de sombreamento detalhado, análise estrutural, proteção elétrica, aprovação da concessionária, ART ou validação por engenheiro responsável.
