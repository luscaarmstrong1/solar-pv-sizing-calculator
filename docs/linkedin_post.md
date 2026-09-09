# Post Para LinkedIn

Dimensionar um sistema fotovoltaico vai além de dividir consumo por geração específica.

Neste projeto desenvolvi uma calculadora de pré-dimensionamento FV em Python, Excel e Streamlit. Ela estima potência requerida, quantidade de módulos, potência instalada, relação CC/CA, área técnica e geração mensal, além de validar limites elétricos do inversor e do arranjo.

O ponto técnico mais importante foi corrigir a modelagem térmica e elétrica: coeficientes separados para Voc, Vmp, Isc, Imp e Pmax, strings inteiras por MPPT, limite CC do inversor preservado e validações automatizadas.

- Potência requerida: 4.98 kWp
- Potência instalada: 5.50 kWp
- Módulos: 10 x 550 Wp
- Inversor: 6.00 kW
- Strings: MPPT 1: 10 módulos; MPPT 2: sem strings
- CC/CA: 0.92
- Geração anual: 7892 kWh
- Área técnica: 31.0 m²
- Status: OK
