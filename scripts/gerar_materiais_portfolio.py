from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]


def load_results() -> dict:
    return json.loads((ROOT / "outputs" / "sizing_results.json").read_text(encoding="utf-8"))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def should_publish_file(path: Path) -> bool:
    ignored_dirs = {"node_modules", "__pycache__", ".pytest_cache", ".git"}
    ignored_suffixes = {".pyc", ".ndjson"}
    return not any(part in ignored_dirs for part in path.parts) and path.suffix not in ignored_suffixes


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


def image(path: Path, size: tuple[int, int], title: str, subtitle: str, footer: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, "#F7FAFC")
    draw = ImageDraw.Draw(img)
    w, h = size
    draw.rectangle((0, 0, w, h), fill="#F7FAFC")
    draw.rectangle((0, 0, w, int(h * 0.16)), fill="#0F766E")
    draw.rectangle((0, int(h * 0.16), w, int(h * 0.19)), fill="#F59E0B")
    for x in range(80, w, 180):
        draw.line((x, int(h * 0.27), x + 80, int(h * 0.78)), fill="#D7DEE8", width=2)
    for y in range(int(h * 0.30), int(h * 0.78), 85):
        draw.line((int(w * 0.55), y, int(w * 0.92), y + 28), fill="#CBD5E1", width=2)
    panel = (int(w * 0.07), int(h * 0.28), int(w * 0.50), int(h * 0.76))
    draw.rounded_rectangle(panel, radius=8, fill="#FFFFFF", outline="#CBD5E1", width=2)
    draw.text((int(w * 0.09), int(h * 0.34)), title, fill="#17324D", font=font(max(32, w // 22), True))
    draw.text((int(w * 0.09), int(h * 0.53)), subtitle, fill="#334155", font=font(max(18, w // 45)))
    draw.text((int(w * 0.09), int(h * 0.67)), footer, fill="#0F766E", font=font(max(18, w // 48), True))
    draw.text((int(w * 0.07), int(h * 0.08)), "ENGENHARIA ELÉTRICA | ENERGIA SOLAR", fill="#FFFFFF", font=font(max(16, w // 60), True))
    img.save(path)


def main() -> None:
    results = load_results()
    sizing = results["sizing"]
    strings = results["strings"]
    allocation = "; ".join(
        f"MPPT {idx}: " + (", ".join(f"{mods} módulos" for mods in mppt) if mppt else "sem strings")
        for idx, mppt in enumerate(strings["mppt_string_modules"], start=1)
    )
    summary_lines = [
        f"Potência requerida: {sizing['required_pv_power_kwp']:.2f} kWp",
        f"Potência instalada: {sizing['installed_dc_power_kwp']:.2f} kWp",
        f"Módulos: {sizing['module_count']} x {results['module']['power_wp']:.0f} Wp",
        f"Inversor: {results['inverter']['ac_power_kw']:.2f} kW",
        f"Strings: {allocation}",
        f"CC/CA: {sizing['dc_ac_ratio']:.2f}",
        f"Geração anual: {sizing['annual_generation_kwh']:.0f} kWh",
        f"Área técnica: {sizing['technical_area_m2']:.1f} m²",
        f"Status: {results['technical_status']}",
    ]
    resumo = "\n".join(f"- {line}" for line in summary_lines)

    readme = f"""
# Calculadora de Dimensionamento Fotovoltaico

Ferramenta de portfólio para pré-dimensionamento de sistemas fotovoltaicos conectados à rede, desenvolvida em Python, Excel e Streamlit.

## Resultado do Cenário Base

{resumo}

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
"""
    write(ROOT / "README.md", readme)
    write(ROOT / "README_PT-BR.md", readme)
    write(ROOT / "docs" / "portfolio_description.md", f"""
# Descrição do Projeto

Calculadora de pré-dimensionamento fotovoltaico criada como projeto de portfólio técnico em Engenharia Elétrica.

O projeto combina um motor de cálculo em Python, uma planilha Excel auditável e uma interface Streamlit em português. O objetivo é demonstrar raciocínio de dimensionamento, rastreabilidade de premissas e validações elétricas essenciais antes de qualquer etapa executiva.

Resultado do cenário base:

{resumo}
""")
    write(ROOT / "docs" / "linkedin_project.md", f"""
# Projeto Para LinkedIn

Calculadora de Dimensionamento Fotovoltaico

Ferramenta em Python, Excel e Streamlit para pré-dimensionar sistemas FV conectados à rede, com validações de Voc, Vmp, MPPT, tensão de partida, correntes por entrada, correntes por MPPT e alocação inteira de strings.

{resumo}
""")
    write(ROOT / "docs" / "linkedin_post.md", f"""
# Post Para LinkedIn

Dimensionar um sistema fotovoltaico vai além de dividir consumo por geração específica.

Neste projeto desenvolvi uma calculadora de pré-dimensionamento FV em Python, Excel e Streamlit. Ela estima potência requerida, quantidade de módulos, potência instalada, relação CC/CA, área técnica e geração mensal, além de validar limites elétricos do inversor e do arranjo.

O ponto técnico mais importante foi corrigir a modelagem térmica e elétrica: coeficientes separados para Voc, Vmp, Isc, Imp e Pmax, strings inteiras por MPPT, limite CC do inversor preservado e validações automatizadas.

{resumo}
""")
    write(ROOT / "docs" / "resume_bullet_points.md", f"""
# Pontos Para Currículo

- Desenvolvi uma calculadora fotovoltaica em Python, Excel e Streamlit para pré-dimensionamento de sistemas FV conectados à rede.
- Modelei consumo, recurso solar, Performance Ratio, perdas compostas, potência requerida, módulos, relação CC/CA e geração mensal.
- Implementei validações elétricas de Voc em frio, Vmp em quente/frio, janela MPPT, tensão de partida, corrente por entrada, corrente por MPPT e limite CC do inversor.
- Criei testes automatizados para proteger coeficientes térmicos, limites do inversor e alocação inteira de strings.
""")
    write(ROOT / "docs" / "interview_case.md", f"""
# Caso Para Entrevista

Este projeto pode ser apresentado como um caso prático de engenharia aplicada: transformar premissas de consumo e irradiação em uma ferramenta calculável, auditável e demonstrável.

Principais decisões:

- Separar motor de cálculo, interface e planilha.
- Usar coeficientes térmicos específicos para cada grandeza elétrica.
- Tratar limites de inversor como restrições de datasheet.
- Impedir arranjos com módulos fictícios.
- Criar testes para os riscos técnicos mais prováveis.
""")
    write(ROOT / "docs" / "future_evolutions.md", """
# Evoluções Futuras

- Banco de módulos e inversores com seleção por fabricante.
- Importação de consumo real por fatura ou CSV.
- Integração com dados meteorológicos por localização.
- Cálculo financeiro com tarifa, impostos, payback e VPL.
- Exportação automática de relatório técnico em PDF.
- Comparação de múltiplos cenários de inclinação, perdas e inversores.
""")

    methodology = f"""
# Metodologia Técnica

## Convenção dos Coeficientes

Todos os coeficientes térmicos de módulo são informados em `%/°C`. O motor converte internamente para fração ao aplicar `valor_corrigido = valor_STC x (1 + coeficiente/100 x (T - 25))`.

## Vmp

Vmp usa `vmp_temp_coeff_pct_c`. A ferramenta não usa coeficiente de Isc para corrigir Vmp. Quando a temperatura da célula aumenta e o coeficiente de Vmp é negativo, a tensão de máxima potência diminui.

## Strings

O algoritmo busca alocações inteiras, respeitando Nmin, Nmax, número de MPPTs e entradas disponíveis. Strings paralelas no mesmo MPPT são mantidas com o mesmo comprimento. MPPTs diferentes podem ter alocações distintas quando os limites elétricos permanecem compatíveis.

## Critério de Seleção

As configurações candidatas priorizam uso exato dos módulos, equilíbrio entre MPPTs, baixa assimetria, tensão dentro de região adequada da janela MPPT e menor quantidade de strings.
"""
    for doc in ["methodology.md", "formulas.md", "assumptions.md", "technical_validation.md"]:
        write(ROOT / "docs" / doc, methodology)

    questions = "\n".join(
        f"{idx}. {question}"
        for idx, question in enumerate(
            [
                "O que é HSP e por que ela não é igual a horas de sol?",
                "O que é Performance Ratio?",
                "Por que o PR por perdas deve ser composto?",
                "O que é kWp?",
                "Qual a diferença entre kW, kWp e kWh?",
                "Como calcular a potência FV requerida?",
                "Por que arredondar módulos para cima?",
                "O que é relação CC/CA?",
                "Por que não existe um CC/CA ideal universal?",
                "O que é Voc?",
                "Por que Voc aumenta no frio?",
                "O que é Vmp?",
                "Por que Vmp diminui no calor?",
                "Por que não usar coeficiente de Isc para Vmp?",
                "O que é Isc?",
                "O que é Imp?",
                "Como corrente se soma em strings paralelas?",
                "O que é MPPT?",
                "Qual a diferença entre tensão de partida e tensão mínima MPPT?",
                "Como calcular Nmax?",
                "Como calcular Nmin?",
                "Qual o risco de ultrapassar Vdc máxima?",
                "Qual o risco de Vmp abaixo do MPPT mínimo?",
                "Qual o risco de Vmp acima do MPPT máximo?",
                "Por que strings paralelas no mesmo MPPT devem ter comprimentos iguais?",
                "O que significa alocação inteira de módulos?",
                "Por que uma string parcial pode ser inconsistente?",
                "Como validar entradas físicas do inversor?",
                "Como validar corrente por entrada?",
                "Como validar corrente por MPPT?",
                "Como estimar geração mensal?",
                "Por que excedente mensal não representa crédito tarifário real?",
                "Por que área técnica é maior que área dos módulos?",
                "Quais dados devem vir de datasheet?",
                "Quais dados são demonstrativos neste projeto?",
                "Quais limitações impedem tratar isto como projeto executivo?",
                "Como evoluir para integração com API solar?",
                "Como evoluir para banco de módulos e inversores reais?",
                "Como validar Python contra Excel?",
                "Que testes unitários protegem regressões elétricas?",
                "Como explicar este projeto em entrevista técnica?",
                "Quais decisões de engenharia aparecem no algoritmo?",
            ],
            start=1,
        )
    )
    write(ROOT / "docs" / "perguntas_entrevista.md", "# Perguntas de Entrevista\n\n" + questions)

    write(ROOT / "docs" / "curriculo_projeto.md", f"""
# Currículo

## Versão Curta
Desenvolvi uma calculadora de pré-dimensionamento fotovoltaico em Python, Excel e Streamlit, com validações de módulos, inversores, strings, MPPT, tensão, corrente, área e geração mensal.

## Versão Média
Projeto de Engenharia Elétrica aplicado a sistemas fotovoltaicos: implementação de motor de cálculo em Python, planilha Excel auditável e dashboard Streamlit para estimar potência FV, módulos, inversor, relação CC/CA, strings, geração mensal e compatibilidade elétrica preliminar.

## Versão ATS
Energia Solar; Sistemas Fotovoltaicos; Dimensionamento Fotovoltaico; Python; Excel; Streamlit; Engenharia Elétrica; MPPT; Voc; Vmp; Isc; Imp; Relação CC/CA; Testes Automatizados.

## Seção Projetos
Calculadora de Dimensionamento Fotovoltaico - ferramenta de portfólio para pré-dimensionamento FV com validações térmicas e elétricas automatizadas. Resultado base: {sizing['installed_dc_power_kwp']:.2f} kWp, {sizing['module_count']} módulos, geração anual estimada de {sizing['annual_generation_kwh']:.0f} kWh e status {results['technical_status']}.
""")

    linkedin_dir = ROOT / "linkedin"
    write(linkedin_dir / "01_PROJETO_LINKEDIN.txt", f"""
NOME
Calculadora de Dimensionamento Fotovoltaico

NOME INTERNACIONAL OPCIONAL
Solar PV System Sizing Calculator

DATA DE INÍCIO
08/09/2026

DATA DE TÉRMINO
08/09/2026

URL
Ver linkedin/05_URLS.txt

DESCRIÇÃO
Desenvolvimento de uma ferramenta de pré-dimensionamento de sistemas fotovoltaicos utilizando Python, Excel e Streamlit. A solução integra análise de consumo, HSP, Performance Ratio, potência FV requerida, seleção preliminar de módulos e inversor, relação CC/CA, dimensionamento inteiro de strings, verificação de MPPT, tensão Voc em frio, tensão Vmp em quente e em frio, corrente operacional, corrente de curto-circuito, geração mensal, área técnica necessária e validações automatizadas.

O projeto foi desenvolvido com dados demonstrativos e tem finalidade de portfólio técnico em Engenharia Elétrica, destacando que o dimensionamento FV não se limita a dividir consumo por geração específica: também exige compatibilidade elétrica entre módulos, inversores, MPPTs, strings, temperatura e limites de datasheet.

Escopo: pré-dimensionamento técnico preliminar. Não substitui projeto executivo, ART ou validação por engenheiro responsável.
""")
    write(linkedin_dir / "02_COMPETENCIAS.txt", """
TOP 5
1. Energia Solar
2. Sistemas Fotovoltaicos
3. Engenharia Elétrica
4. Python
5. Projeto de Sistemas Fotovoltaicos

COMPLEMENTARES
Energias Renováveis
Excel
Cálculos de Engenharia
Engenharia de Energia
Streamlit
Data Analysis
""")
    write(linkedin_dir / "03_POST_LINKEDIN.md", f"""
Dimensionar um sistema fotovoltaico não é apenas dividir consumo por geração específica.

Nesse projeto, desenvolvi uma Calculadora de Dimensionamento Fotovoltaico em Python, Excel e Streamlit para pré-dimensionar sistemas FV conectados à rede.

A ferramenta calcula consumo anual, HSP, Performance Ratio, potência FV requerida, quantidade de módulos, potência instalada, relação CC/CA, área técnica e geração mensal estimada.

O ponto principal está nas validações elétricas: o modelo verifica Voc em frio, Vmp em quente e frio, tensão de partida, janela MPPT, corrente por entrada, corrente por MPPT, Isc, quantidade de entradas e alocação inteira de strings sem criar módulos fictícios.

Também criei uma planilha Excel auditável com as mesmas premissas do Python, além de testes automatizados para proteger casos críticos como Vmp no calor, Voc no frio, limite CC do inversor e configurações incompatíveis.

Resultado do cenário base: {sizing['installed_dc_power_kwp']:.2f} kWp instalados, {sizing['module_count']} módulos, relação CC/CA de {sizing['dc_ac_ratio']:.2f} e geração anual estimada de {sizing['annual_generation_kwh']:.0f} kWh.

Projeto de portfólio técnico para aplicação de cálculos de Engenharia Elétrica em sistemas fotovoltaicos. Não é projeto executivo.

Link: ver repositório público do projeto.

#EngenhariaEletrica #EnergiaSolar #Fotovoltaica #Python #EnergiaRenovavel
""")
    write(linkedin_dir / "04_COMO_ADICIONAR.txt", """
1. Abrir o LinkedIn.
2. Entrar no perfil.
3. Selecionar Adicionar seção ao perfil.
4. Escolher Projetos.
5. Colar o nome de linkedin/01_PROJETO_LINKEDIN.txt.
6. Colar a descrição de linkedin/01_PROJETO_LINKEDIN.txt.
7. Inserir a URL pública disponível em linkedin/05_URLS.txt.
8. Adicionar as competências de linkedin/02_COMPETENCIAS.txt.
9. Salvar.
""")
    write(linkedin_dir / "05_URLS.txt", """
GitHub: não publicado automaticamente neste ambiente
Streamlit: execução local com streamlit run app.py
Página do Projeto: site/index.html
""")
    write(linkedin_dir / "06_RESUMO_30_SEGUNDOS.txt", f"""
Desenvolvi uma calculadora de pré-dimensionamento fotovoltaico em Python, Excel e Streamlit. Ela estima potência FV, módulos, inversor, relação CC/CA, strings, geração mensal e área necessária, mas também valida Voc, Vmp, MPPT, tensão de partida e correntes por entrada e por MPPT. O cenário base resultou em {sizing['installed_dc_power_kwp']:.2f} kWp, {sizing['module_count']} módulos e {sizing['annual_generation_kwh']:.0f} kWh/ano.
""")
    write(linkedin_dir / "07_RESUMO_1_MINUTO.txt", f"""
Este projeto é uma ferramenta de portfólio para pré-dimensionamento de sistemas fotovoltaicos conectados à rede. O motor em Python calcula consumo, HSP ponderada, Performance Ratio, potência FV requerida, quantidade de módulos, potência instalada, relação CC/CA e geração mensal. A parte mais importante é a compatibilidade elétrica: o algoritmo dimensiona strings inteiras, não inventa módulos para fechar arranjos, separa corretamente coeficientes de Voc, Vmp, Isc e Imp, e valida tensão de partida, janela MPPT, Voc em frio, Vmp em quente/frio e correntes do inversor. Também há uma planilha Excel auditável e um dashboard Streamlit para demonstração.
""")
    write(linkedin_dir / "08_PRINCIPAIS_RESULTADOS.txt", "\n".join(summary_lines))

    write(ROOT / "RELATORIO_VALIDACAO.md", f"""
# Relatório de Validação

Status geral: {results['technical_status']}

## Validações Técnicas

{chr(10).join(f"- {item['item']}: {item['status']} - {item['message']}" for item in results['validations'])}

## Itens Críticos Corrigidos

- Vmp usa coeficiente próprio de Vmp.
- Voc em frio e Vmp em quente/frio são avaliados.
- Potência CC máxima do inversor é limite de datasheet e não é alterada automaticamente.
- Strings são alocadas com quantidade inteira exata de módulos.
- Correntes por entrada e por MPPT são suportadas.
- PR direto e PR por perdas compostas estão disponíveis.
""")
    write(ROOT / "RELATORIO_FINAL.md", f"""
# Relatório Final

Status Geral: CONCLUÍDO

## Motor de Cálculo
Python implementado com módulos separados para consumo, recurso solar, dimensionamento, módulo, inversor, strings, geração e validação.

## Excel
Planilha auditável recriada com fórmulas, gráficos e validações principais.

## Streamlit
Dashboard interativo em português com modos Simples, Intermediário e Avançado.

## LinkedIn
Pasta linkedin/ pronta para copiar e colar.

## Resultado
{resumo}

## URLs
Consultar linkedin/05_URLS.txt.
""")
    inventory = sorted(
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in ROOT.rglob("*")
        if path.is_file() and should_publish_file(path)
    )
    write(ROOT / "INVENTARIO_FINAL.txt", "\n".join(inventory))

    site_html = f"""
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Calculadora de Dimensionamento Fotovoltaico</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f7fafc; }}
    header {{ background: #0f766e; color: white; padding: 48px 8%; border-bottom: 8px solid #f59e0b; }}
    main {{ padding: 32px 8%; max-width: 1100px; margin: auto; }}
    h1 {{ margin: 0 0 12px; font-size: 42px; }}
    section {{ margin: 32px 0; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; }}
    .card {{ background: white; border: 1px solid #d7dee8; border-radius: 8px; padding: 18px; }}
    .metric {{ font-size: 28px; font-weight: 700; color: #0f766e; }}
    img {{ max-width: 100%; border: 1px solid #d7dee8; border-radius: 8px; background: white; }}
  </style>
</head>
<body>
  <header>
    <h1>Calculadora de Dimensionamento Fotovoltaico</h1>
    <p>Python, Excel e Streamlit aplicados ao pré-dimensionamento técnico de sistemas FV.</p>
  </header>
  <main>
    <section class="grid">
      <div class="card"><div>Potência FV requerida</div><div class="metric">{sizing['required_pv_power_kwp']:.2f} kWp</div></div>
      <div class="card"><div>Potência instalada</div><div class="metric">{sizing['installed_dc_power_kwp']:.2f} kWp</div></div>
      <div class="card"><div>Módulos</div><div class="metric">{sizing['module_count']}</div></div>
      <div class="card"><div>Geração anual</div><div class="metric">{sizing['annual_generation_kwh']:.0f} kWh</div></div>
    </section>
    <section>
      <h2>Validações</h2>
      <p>A ferramenta avalia Voc, Vmp, tensão de partida, MPPT, corrente por entrada, corrente por MPPT, entradas físicas, área, geração e relação CC/CA.</p>
    </section>
    <section>
      <h2>Arquitetura</h2>
      <img src="../assets/diagrams/arquitetura_projeto.png" alt="Arquitetura do projeto">
    </section>
  </main>
</body>
</html>
"""
    write(ROOT / "site" / "index.html", site_html)
    write(ROOT / "index.html", site_html)

    assets = ROOT / "assets" / "linkedin"
    image(assets / "capa_projeto_linkedin.png", (1200, 627), "DIMENSIONAMENTO\nFOTOVOLTAICO", "Engenharia Elétrica • Python • Excel • Sistemas Fotovoltaicos", f"{sizing['installed_dc_power_kwp']:.2f} kWp | {sizing['module_count']} módulos | {sizing['annual_generation_kwh']:.0f} kWh/ano")
    image(assets / "projeto_linkedin_1080x1080.png", (1080, 1080), "DIMENSIONAMENTO\nFOTOVOLTAICO", "Python • Excel • Streamlit", f"Status {results['technical_status']} | CC/CA {sizing['dc_ac_ratio']:.2f}")
    carousel = assets / "carrossel"
    for idx, title in enumerate(["Capa", "Consumo", "Dimensionamento", "Módulo e Inversor", "Strings", "Validações", "Resultados", "Tecnologias"], start=1):
        image(carousel / f"{idx:02d}_{title.lower().replace(' ', '_')}.png", (1080, 1080), title.upper(), "Calculadora de Dimensionamento Fotovoltaico", f"{sizing['installed_dc_power_kwp']:.2f} kWp | {sizing['annual_generation_kwh']:.0f} kWh/ano")
    image(ROOT / "assets" / "diagrams" / "arquitetura_projeto.png", (1400, 900), "ARQUITETURA\nDO PROJETO", "Consumo → Recurso Solar → Potência FV → Módulos → Inversor → Strings → Validação → Geração → Relatório", "Python • Excel • Streamlit")

    write(ROOT / "docs" / "insights_calculados.md", "\n".join(f"- {line}" for line in summary_lines + [
        f"Atendimento anual estimado: {sizing['annual_coverage_pct']:.1%}",
        f"PR efetivo: {results['resource']['performance_ratio']:.1%}",
        f"HSP média ponderada: {results['resource']['average_hsp']:.2f} h/dia",
        f"Voc frio máximo de string: {strings['voc_string_v']:.1f} V",
        f"Vmp quente de string: {strings['vmp_string_hot_v']:.1f} V",
    ]))


if __name__ == "__main__":
    main()
