# Relatório de Validação

Status geral: OK

## Validações Técnicas

- DC power: OK - Potência CC instalada 5.50 kWp versus limite do inversor 9.00 kWp.
- DC/AC ratio: OK - Relação CC/CA 0.92; faixa preliminar configurada de 0.80 a 1.35.
- String maximum voltage: OK - Voc da string em frio 525.9 V versus limite configurado 950.0 V.
- Startup voltage: OK - Vmp da string em quente 357.0 V versus tensão de partida 180.0 V.
- MPPT minimum voltage: OK - Vmp da string em quente 357.0 V versus tensão mínima MPPT 160.0 V.
- MPPT maximum voltage: OK - Vmp da string em frio 443.7 V versus tensão máxima MPPT 850.0 V.
- Input operating current: OK - Imp máxima por entrada 13.2 A versus limite 16.0 A.
- Input short-circuit current: OK - Isc máxima por entrada 14.3 A versus limite 20.0 A.
- MPPT operating current: OK - Imp máxima por MPPT 13.2 A versus limite 30.
- MPPT short-circuit current: OK - Isc máxima por MPPT 14.3 A versus limite 40.
- Available inputs: OK - 1 strings necessárias versus 4 entradas disponíveis.
- Module allocation: OK - 10 módulos alocados exatamente em 1 strings.
- Energy target: OK - Geração anual 7892 kWh versus meta 7140 kWh.
- Available area: OK - Área técnica necessária 31.0 m² versus área disponível 60.0 m².

## Itens Críticos Corrigidos

- Vmp usa coeficiente próprio de Vmp.
- Voc em frio e Vmp em quente/frio são avaliados.
- Potência CC máxima do inversor é limite de datasheet e não é alterada automaticamente.
- Strings são alocadas com quantidade inteira exata de módulos.
- Correntes por entrada e por MPPT são suportadas.
- PR direto e PR por perdas compostas estão disponíveis.
