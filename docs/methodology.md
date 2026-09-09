# Metodologia Técnica

## Convenção dos Coeficientes

Todos os coeficientes térmicos de módulo são informados em `%/°C`. O motor converte internamente para fração ao aplicar `valor_corrigido = valor_STC x (1 + coeficiente/100 x (T - 25))`.

## Vmp

Vmp usa `vmp_temp_coeff_pct_c`. A ferramenta não usa coeficiente de Isc para corrigir Vmp. Quando a temperatura da célula aumenta e o coeficiente de Vmp é negativo, a tensão de máxima potência diminui.

## Strings

O algoritmo busca alocações inteiras, respeitando Nmin, Nmax, número de MPPTs e entradas disponíveis. Strings paralelas no mesmo MPPT são mantidas com o mesmo comprimento. MPPTs diferentes podem ter alocações distintas quando os limites elétricos permanecem compatíveis.

## Critério de Seleção

As configurações candidatas priorizam uso exato dos módulos, equilíbrio entre MPPTs, baixa assimetria, tensão dentro de região adequada da janela MPPT e menor quantidade de strings.
