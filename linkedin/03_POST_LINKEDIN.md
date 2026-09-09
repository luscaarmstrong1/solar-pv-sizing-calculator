Dimensionar um sistema fotovoltaico não é apenas dividir consumo por geração específica.

Nesse projeto, desenvolvi uma Calculadora de Dimensionamento Fotovoltaico em Python, Excel e Streamlit para pré-dimensionar sistemas FV conectados à rede.

A ferramenta calcula consumo anual, HSP, Performance Ratio, potência FV requerida, quantidade de módulos, potência instalada, relação CC/CA, área técnica e geração mensal estimada.

O ponto principal está nas validações elétricas: o modelo verifica Voc em frio, Vmp em quente e frio, tensão de partida, janela MPPT, corrente por entrada, corrente por MPPT, Isc, quantidade de entradas e alocação inteira de strings sem criar módulos fictícios.

Também criei uma planilha Excel auditável com as mesmas premissas do Python, além de testes automatizados para proteger casos críticos como Vmp no calor, Voc no frio, limite CC do inversor e configurações incompatíveis.

Resultado do cenário base: 5.50 kWp instalados, 10 módulos, relação CC/CA de 0.92 e geração anual estimada de 7892 kWh.

Projeto de portfólio técnico para aplicação de cálculos de Engenharia Elétrica em sistemas fotovoltaicos. Não é projeto executivo.

Link: ver repositório público do projeto.

#EngenhariaEletrica #EnergiaSolar #Fotovoltaica #Python #EnergiaRenovavel
