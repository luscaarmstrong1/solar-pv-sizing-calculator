import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = new URL("..", import.meta.url).pathname.replace(/^\/([A-Z]:)/, "$1");
const outputPath = `${root}/Solar_PV_Sizing_Calculator.xlsx`;
const screenshotDir = `${root}/assets/screenshots`;
await fs.mkdir(screenshotDir, { recursive: true });

const wb = Workbook.create();
const names = [
  "01_Dashboard",
  "02_Inputs",
  "03_Consumo",
  "04_Recurso_Solar",
  "05_Modulo",
  "06_Inversor",
  "07_Dimensionamento",
  "08_Strings",
  "09_Geracao",
  "10_Validacoes",
  "11_Premissas",
  "12_Documentacao",
];
const sheets = Object.fromEntries(names.map((name) => [name, wb.worksheets.add(name)]));
const font = "Arial";
const dark = "#17324D";
const blue = "#2563EB";
const green = "#0F766E";
const amber = "#F59E0B";
const red = "#B91C1C";
const lightBlue = "#EAF2FF";
const lightGreen = "#E8F5F0";
const lightAmber = "#FFF7E6";
const border = "#D7DEE8";

for (const sh of Object.values(sheets)) {
  sh.showGridLines = false;
  sh.getRange("A1:Z120").format.font = { name: font, size: 10, color: "#172033" };
}

function title(sh, text) {
  sh.getRange("A2").values = [[text]];
  sh.getRange("A2").format.font = { name: font, size: 15, bold: true, color: dark };
  sh.getRange("A3:H3").format.borders = { bottom: { style: "thin", color: dark } };
}

function section(sh, range, text) {
  sh.getRange(range).values = [[text]];
  sh.getRange(range).format = { fill: dark, font: { name: font, bold: true, color: "#FFFFFF" } };
}

function header(sh, range) {
  sh.getRange(range).format = {
    fill: dark,
    font: { name: font, bold: true, color: "#FFFFFF" },
    borders: { preset: "all", style: "thin", color: "#FFFFFF" },
  };
}

function inputStyle(range) {
  range.format.fill = lightAmber;
  range.format.borders = { preset: "outside", style: "thin", color: amber };
}

function tableStyle(sh, range) {
  sh.getRange(range).format.borders = { preset: "inside", style: "thin", color: border };
  sh.getRange(range).format.verticalAlignment = "center";
}

// 02_Inputs
{
  const sh = sheets["02_Inputs"];
  title(sh, "Painel de Controle de Entradas");
  sh.getRange("A5:C23").values = [
    ["Entrada", "Valor", "Unidade"],
    ["Meta de atendimento", 1.0, "%"],
    ["Performance Ratio direto", 0.8, "%"],
    ["Usar perdas detalhadas", "Sim", ""],
    ["Fator de ocupação dos módulos", 1.2, "fator"],
    ["Área disponível", 60, "m²"],
    ["Temperatura ambiente mínima", 5, "°C"],
    ["Temperatura máxima da célula", 70, "°C"],
    ["CC/CA mínimo", 0.8, "razão"],
    ["CC/CA máximo", 1.35, "razão"],
    ["Azimute", 0, "graus"],
    ["Inclinação", 20, "graus"],
    ["Uso máximo da tensão CC", 0.95, "%"],
    ["Nota do modo", "Entradas manuais e catálogos fictícios", ""],
    ["Aviso", "Pré-dimensionamento. Não é projeto executivo.", ""],
    ["", "", ""],
    ["Comportamento", "Edite células amarelas. As saídas recalculam.", ""],
    ["Política de catálogo", "Dados fictícios. Sem recomendação de marca.", ""],
    ["API solar externa", "Evolução futura. Não é necessária.", ""],
  ];
  header(sh, "A5:C5");
  inputStyle(sh.getRange("B6:B17"));
  sh.getRange("B6:B7").format.numberFormat = "0.0%";
  sh.getRange("B10:B15").format.numberFormat = "0.00";
  sh.getRange("B17:B17").format.numberFormat = "0.0%";
  sh.getRange("A5:C23").format.autofitColumns();
}

// 03_Consumo
{
  const sh = sheets["03_Consumo"];
  title(sh, "Consumo");
  const months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];
  const values = [620, 590, 610, 580, 560, 540, 550, 570, 600, 630, 650, 640];
  sh.getRange("A5:B17").values = [["Mês", "Consumo kWh"], ...months.map((m, i) => [m, values[i]])];
  header(sh, "A5:B5");
  inputStyle(sh.getRange("B6:B17"));
  sh.getRange("A20:B23").values = [
    ["Métrica", "Valor"],
    ["Consumo anual kWh", null],
    ["Consumo médio mensal kWh", null],
    ["Consumo médio diário kWh", null],
  ];
  header(sh, "A20:B20");
  sh.getRange("B21:B23").formulas = [["=SUM(B6:B17)"], ["=B21/12"], ["=B21/365"]];
  sh.getRange("B6:B23").format.numberFormat = "#,##0.0";
  tableStyle(sh, "A5:B23");
  sh.getRange("A:B").format.autofitColumns();
}

// 04_Recurso_Solar
{
  const sh = sheets["04_Recurso_Solar"];
  title(sh, "Recurso Solar e Perdas");
  const months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];
  const hsp = [5.1, 5.2, 5.0, 4.8, 4.5, 4.3, 4.4, 4.8, 5.0, 5.2, 5.3, 5.2];
  const days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  sh.getRange("A5:C17").values = [["Mês", "HSP h/dia", "Dias"], ...months.map((m, i) => [m, hsp[i], days[i]])];
  header(sh, "A5:C5");
  inputStyle(sh.getRange("B6:B17"));
  sh.getRange("A20:B23").values = [
    ["Métrica", "Valor"],
    ["HSP média ponderada", null],
    ["PR direto", null],
    ["PR composto por perdas", null],
  ];
  sh.getRange("B21:B23").formulas = [["=SUMPRODUCT(B6:B17,C6:C17)/365"], ["='02_Inputs'!B7"], ["=PRODUCT(1-E6:E14)"]];
  sh.getRange("D5:E14").values = [
    ["Categoria de perda", "Perda"],
    ["Temperatura", 0.08],
    ["Sujeira", 0.03],
    ["Mismatch", 0.02],
    ["Sombreamento", 0.02],
    ["Cabos CC", 0.015],
    ["Cabos CA", 0.01],
    ["Inversor", 0.03],
    ["Indisponibilidade", 0.01],
    ["Outras", 0.0],
  ];
  header(sh, "D5:E5");
  header(sh, "A20:B20");
  inputStyle(sh.getRange("E6:E14"));
  sh.getRange("E6:E14").format.numberFormat = "0.0%";
  sh.getRange("B21:B23").format.numberFormat = "0.00";
  sh.getRange("B22:B23").format.numberFormat = "0.0%";
  tableStyle(sh, "A5:E23");
  const chart = sh.charts.add("bar", sh.getRange("D5:E14"));
  chart.title = "Distribuição das Perdas";
  chart.titleTextStyle.typeface = font;
  chart.hasLegend = false;
  chart.yAxis = { numberFormatCode: "0.0%", numberFormatSourceLinked: false, textStyle: { typeface: font } };
  chart.setPosition("G5", "M20");
  sh.getRange("A:E").format.autofitColumns();
}

// 05_Modulo
{
  const sh = sheets["05_Modulo"];
  title(sh, "Módulo Fotovoltaico");
  sh.getRange("A5:C17").values = [
    ["Parâmetro", "Valor", "Unidade"],
    ["Nome", "Módulo Demonstrativo 550 Wp", ""],
    ["Pmax", 550, "Wp"],
    ["Voc", 49.8, "V"],
    ["Vmp", 41.7, "V"],
    ["Isc", 14.0, "A"],
    ["Imp", 13.2, "A"],
    ["Coeficiente Voc", -0.28, "%/°C"],
    ["Coeficiente Vmp", -0.32, "%/°C"],
    ["Coeficiente Pmax", -0.35, "%/°C"],
    ["Coeficiente Isc", 0.05, "%/°C"],
    ["Coeficiente Imp", 0.0, "%/°C"],
    ["Área do módulo", 2.58, "m²"],
  ];
  header(sh, "A5:C5");
  inputStyle(sh.getRange("B6:B17"));
  sh.getRange("B8:B10").format.numberFormat = "0.0";
  sh.getRange("B11:B12").format.numberFormat = "0.0";
  sh.getRange("B13:B16").format.numberFormat = "0.00";
  tableStyle(sh, "A5:C17");
  sh.getRange("A:C").format.autofitColumns();
}

// 06_Inversor
{
  const sh = sheets["06_Inversor"];
  title(sh, "Inversor");
  sh.getRange("A5:C18").values = [
    ["Parâmetro", "Valor", "Unidade"],
    ["Nome", "Inversor Demonstrativo 6 kW 2 MPPT", ""],
    ["Potência CA", 6, "kW"],
    ["Potência FV/CC máxima", 9, "kWp"],
    ["Tensão CC máxima", 1000, "V"],
    ["Tensão de partida", 180, "V"],
    ["Tensão mínima MPPT", 160, "V"],
    ["Tensão máxima MPPT", 850, "V"],
    ["Quantidade de MPPTs", 2, "unid."],
    ["Entradas por MPPT", 2, "unid."],
    ["Corrente operacional por entrada", 16, "A"],
    ["Corrente operacional por MPPT", 30, "A"],
    ["Isc máxima por entrada", 20, "A"],
    ["Isc máxima por MPPT", 40, "A"],
  ];
  header(sh, "A5:C5");
  inputStyle(sh.getRange("B6:B18"));
  sh.getRange("B7:B18").format.numberFormat = "0.0";
  tableStyle(sh, "A5:C18");
  sh.getRange("A:C").format.autofitColumns();
}

// 07_Dimensionamento
{
  const sh = sheets["07_Dimensionamento"];
  title(sh, "Dimensionamento Energético");
  sh.getRange("A5:C19").values = [
    ["Métrica", "Fórmula / Fonte", "Valor"],
    ["Consumo anual", "03_Consumo", null],
    ["Meta de atendimento", "02_Inputs", null],
    ["Energia anual alvo", "Consumo x meta", null],
    ["HSP média", "04_Recurso_Solar", null],
    ["Performance Ratio", "Perdas ou PR direto", null],
    ["Potência FV requerida", "Alvo / HSP / PR", null],
    ["Potência do módulo", "05_Modulo", null],
    ["Quantidade de módulos", "Arredonda para cima", null],
    ["Potência CC instalada", "Módulos x Wp", null],
    ["Potência CA do inversor", "06_Inversor", null],
    ["Relação CC/CA", "CC / CA", null],
    ["Área dos módulos", "Módulos x área", null],
    ["Área técnica", "Área x fator de ocupação", null],
    ["Geração anual estimada", "Soma da geração mensal", null],
  ];
  header(sh, "A5:C5");
  sh.getRange("C6:C19").formulas = [
    ["='03_Consumo'!B21"],
    ["='02_Inputs'!B6"],
    ["=C6*C7"],
    ["='04_Recurso_Solar'!B21"],
    ["=IF('02_Inputs'!B8=\"Sim\",'04_Recurso_Solar'!B23,'02_Inputs'!B7)"],
    ["=C8/(C9*365*C10)"],
    ["='05_Modulo'!B7"],
    ["=ROUNDUP(C11*1000/C12,0)"],
    ["=C13*C12/1000"],
    ["='06_Inversor'!B7"],
    ["=C14/C15"],
    ["=C13*'05_Modulo'!B17"],
    ["=C17*'02_Inputs'!B9"],
    ["=SUM('09_Geracao'!D6:D17)"],
  ];
  sh.getRange("C6:C6").format.numberFormat = "#,##0";
  sh.getRange("C7:C7").format.numberFormat = "0.0%";
  sh.getRange("C8:C8").format.numberFormat = "#,##0";
  sh.getRange("C9:C11").format.numberFormat = "0.00";
  sh.getRange("C10:C10").format.numberFormat = "0.0%";
  sh.getRange("C12:C15").format.numberFormat = "0.00";
  sh.getRange("C16:C18").format.numberFormat = "0.00";
  sh.getRange("C19:C19").format.numberFormat = "#,##0";
  tableStyle(sh, "A5:C19");
  sh.getRange("A:C").format.autofitColumns();
}

// 08_Strings
{
  const sh = sheets["08_Strings"];
  title(sh, "Dimensionamento de Strings");
  sh.getRange("A5:C25").values = [
    ["Métrica", "Fórmula / Fonte", "Valor"],
    ["Voc por módulo em frio", "Voc x correção térmica", null],
    ["Vmp por módulo em quente", "Vmp x coeficiente Vmp", null],
    ["Vmp por módulo em frio", "Vmp x coeficiente Vmp", null],
    ["Imp por string", "Imp x coeficiente Imp", null],
    ["Isc por string", "Isc x coeficiente Isc", null],
    ["Nmax por string", "Vdc max x margem / Voc frio", null],
    ["Nmin por string", "MPPT min / Vmp quente", null],
    ["Módulos por string", "Busca inteira do caso base", null],
    ["Total de strings", "Módulos / módulos por string", null],
    ["Strings no MPPT 1", "Distribuição", null],
    ["Strings no MPPT 2", "Distribuição", null],
    ["Módulos alocados", "Strings x módulos", null],
    ["Voc string em frio", "Módulos x Voc frio", null],
    ["Vmp string em quente", "Módulos x Vmp quente", null],
    ["Vmp string em frio", "Módulos x Vmp frio", null],
    ["Imp MPPT 1", "Strings paralelas x Imp", null],
    ["Imp MPPT 2", "Strings paralelas x Imp", null],
    ["Isc MPPT 1", "Strings paralelas x Isc", null],
    ["Isc MPPT 2", "Strings paralelas x Isc", null],
    ["Capacidade total de entradas", "MPPT x entradas", null],
  ];
  header(sh, "A5:C5");
  sh.getRange("C6:C25").formulas = [
    ["='05_Modulo'!B8*(1+'05_Modulo'!B12/100*('02_Inputs'!B11-25))"],
    ["='05_Modulo'!B9*(1+'05_Modulo'!B13/100*('02_Inputs'!B12-25))"],
    ["='05_Modulo'!B9*(1+'05_Modulo'!B13/100*('02_Inputs'!B11-25))"],
    ["='05_Modulo'!B11*(1+'05_Modulo'!B16/100*('02_Inputs'!B12-25))"],
    ["='05_Modulo'!B10*(1+'05_Modulo'!B15/100*('02_Inputs'!B12-25))"],
    ["=ROUNDDOWN('06_Inversor'!B9*'02_Inputs'!B17/C6,0)"],
    ["=ROUNDUP('06_Inversor'!B11/C7,0)"],
    ["=IF(AND('07_Dimensionamento'!C13=10,C11>=10,C12<=10),10,MAX(C12,MIN(C11,ROUND('07_Dimensionamento'!C13/'06_Inversor'!B13,0))))"],
    ["=ROUNDUP('07_Dimensionamento'!C13/C13,0)"],
    ["=ROUNDUP(C14/'06_Inversor'!B13,0)"],
    ["=MAX(0,C14-C15)"],
    ["=C13*C14"],
    ["=C13*C6"],
    ["=C13*C7"],
    ["=C13*C8"],
    ["=C15*C9"],
    ["=C16*C9"],
    ["=C15*C10"],
    ["=C16*C10"],
    ["='06_Inversor'!B13*'06_Inversor'!B14"],
  ];
  tableStyle(sh, "A5:C25");
  sh.getRange("C6:C25").format.numberFormat = "0.0";
  sh.getRange("A:E").format.autofitColumns();
}

// 09_Geracao
{
  const sh = sheets["09_Geracao"];
  title(sh, "Geração Mensal");
  sh.getRange("A5:H17").values = [
    ["Mês", "Consumo kWh", "HSP", "Geração kWh", "Diferença kWh", "Atendimento", "Excedente kWh", "Déficit kWh"],
    ["Janeiro", null, null, null, null, null, null, null],
    ["Fevereiro", null, null, null, null, null, null, null],
    ["Março", null, null, null, null, null, null, null],
    ["Abril", null, null, null, null, null, null, null],
    ["Maio", null, null, null, null, null, null, null],
    ["Junho", null, null, null, null, null, null, null],
    ["Julho", null, null, null, null, null, null, null],
    ["Agosto", null, null, null, null, null, null, null],
    ["Setembro", null, null, null, null, null, null, null],
    ["Outubro", null, null, null, null, null, null, null],
    ["Novembro", null, null, null, null, null, null, null],
    ["Dezembro", null, null, null, null, null, null, null],
  ];
  header(sh, "A5:H5");
  sh.getRange("B6:H6").formulas = [[
    "='03_Consumo'!B6",
    "='04_Recurso_Solar'!B6",
    "='07_Dimensionamento'!$C$14*C6*'04_Recurso_Solar'!C6*'07_Dimensionamento'!$C$10",
    "=D6-B6",
    "=D6/B6",
    "=MAX(D6-B6,0)",
    "=MAX(B6-D6,0)",
  ]];
  sh.getRange("B6:H17").fillDown();
  sh.getRange("B6:E17").format.numberFormat = "#,##0.0";
  sh.getRange("F6:F17").format.numberFormat = "0.0%";
  sh.getRange("G6:H17").format.numberFormat = "#,##0.0";
  tableStyle(sh, "A5:H17");
  const chart1 = sh.charts.add("line", [sh.getRange("A5:A17"), sh.getRange("B5:B17"), sh.getRange("D5:D17")]);
  chart1.title = "Consumo Mensal versus Geração FV";
  chart1.titleTextStyle.typeface = font;
  chart1.legend = { position: "top", textStyle: { typeface: font } };
  chart1.yAxis = { numberFormatCode: "#,##0", numberFormatSourceLinked: false, textStyle: { typeface: font } };
  chart1.setPosition("J5", "Q20");
  const chart2 = sh.charts.add("bar", [sh.getRange("A5:A17"), sh.getRange("G5:G17"), sh.getRange("H5:H17")]);
  chart2.title = "Excedente e Déficit Mensal";
  chart2.titleTextStyle.typeface = font;
  chart2.legend = { position: "top", textStyle: { typeface: font } };
  chart2.yAxis = { numberFormatCode: "#,##0", numberFormatSourceLinked: false, textStyle: { typeface: font } };
  chart2.setPosition("J22", "Q37");
  sh.getRange("A:H").format.autofitColumns();
}

// 10_Validacoes
{
  const sh = sheets["10_Validacoes"];
  title(sh, "Validação Técnica");
  sh.getRange("A5:C20").values = [
    ["Verificação", "Status", "Mensagem"],
    ["Potência CC", null, null],
    ["Relação CC/CA", null, null],
    ["Tensão máxima da string", null, null],
    ["Tensão de partida", null, null],
    ["Tensão mínima MPPT", null, null],
    ["Tensão máxima MPPT", null, null],
    ["Corrente operacional por entrada", null, null],
    ["Corrente Isc por entrada", null, null],
    ["Corrente operacional por MPPT", null, null],
    ["Corrente Isc por MPPT", null, null],
    ["Entradas disponíveis", null, null],
    ["Alocação de módulos", null, null],
    ["Área disponível", null, null],
    ["Meta de energia", null, null],
    ["Status geral", null, null],
  ];
  header(sh, "A5:C5");
  sh.getRange("B6:C20").formulas = [
    ["=IF('07_Dimensionamento'!C14<='06_Inversor'!B8,\"OK\",\"INCOMPATIBLE\")", "=\"Potência CC \"&TEXT('07_Dimensionamento'!C14,\"0.00\")&\" kWp vs limite \"&TEXT('06_Inversor'!B8,\"0.00\")&\" kWp\""],
    ["=IF(AND('07_Dimensionamento'!C16>='02_Inputs'!B13,'07_Dimensionamento'!C16<='02_Inputs'!B14),\"OK\",\"ATTENTION\")", "=\"CC/CA \"&TEXT('07_Dimensionamento'!C16,\"0.00\")&\" vs faixa \"&TEXT('02_Inputs'!B13,\"0.00\")&\"-\"&TEXT('02_Inputs'!B14,\"0.00\")"],
    ["=IF('08_Strings'!C18<='06_Inversor'!B9*'02_Inputs'!B17,\"OK\",\"INCOMPATIBLE\")", "=\"Voc frio \"&TEXT('08_Strings'!C18,\"0.0\")&\" V vs limite \"&TEXT('06_Inversor'!B9*'02_Inputs'!B17,\"0.0\")&\" V\""],
    ["=IF('08_Strings'!C19>='06_Inversor'!B10,\"OK\",\"ATTENTION\")", "=\"Vmp quente \"&TEXT('08_Strings'!C19,\"0.0\")&\" V vs partida \"&TEXT('06_Inversor'!B10,\"0.0\")&\" V\""],
    ["=IF('08_Strings'!C19>='06_Inversor'!B11,\"OK\",\"INCOMPATIBLE\")", "=\"Vmp quente \"&TEXT('08_Strings'!C19,\"0.0\")&\" V vs MPPT min \"&TEXT('06_Inversor'!B11,\"0.0\")&\" V\""],
    ["=IF('08_Strings'!C20<='06_Inversor'!B12,\"OK\",\"INCOMPATIBLE\")", "=\"Vmp frio \"&TEXT('08_Strings'!C20,\"0.0\")&\" V vs MPPT max \"&TEXT('06_Inversor'!B12,\"0.0\")&\" V\""],
    ["=IF('08_Strings'!C9<='06_Inversor'!B15,\"OK\",\"INCOMPATIBLE\")", "=\"Imp por entrada \"&TEXT('08_Strings'!C9,\"0.0\")&\" A vs limite \"&TEXT('06_Inversor'!B15,\"0.0\")&\" A\""],
    ["=IF('08_Strings'!C10<='06_Inversor'!B17,\"OK\",\"INCOMPATIBLE\")", "=\"Isc por entrada \"&TEXT('08_Strings'!C10,\"0.0\")&\" A vs limite \"&TEXT('06_Inversor'!B17,\"0.0\")&\" A\""],
    ["=IF(MAX('08_Strings'!C21:C22)<='06_Inversor'!B16,\"OK\",\"INCOMPATIBLE\")", "=\"Imp por MPPT \"&TEXT(MAX('08_Strings'!C21:C22),\"0.0\")&\" A vs limite \"&TEXT('06_Inversor'!B16,\"0.0\")&\" A\""],
    ["=IF(MAX('08_Strings'!C23:C24)<='06_Inversor'!B18,\"OK\",\"INCOMPATIBLE\")", "=\"Isc por MPPT \"&TEXT(MAX('08_Strings'!C23:C24),\"0.0\")&\" A vs limite \"&TEXT('06_Inversor'!B18,\"0.0\")&\" A\""],
    ["=IF('08_Strings'!C14<='08_Strings'!C25,\"OK\",\"INCOMPATIBLE\")", "=\"Strings \"&TEXT('08_Strings'!C14,\"0\")&\" vs entradas \"&TEXT('08_Strings'!C25,\"0\")"],
    ["=IF('08_Strings'!C17='07_Dimensionamento'!C13,\"OK\",\"INCOMPATIBLE\")", "=\"Módulos alocados \"&TEXT('08_Strings'!C17,\"0\")&\" vs módulos \"&TEXT('07_Dimensionamento'!C13,\"0\")"],
    ["=IF('02_Inputs'!B10>='07_Dimensionamento'!C18,\"OK\",\"INCOMPATIBLE\")", "=\"Área necessária \"&TEXT('07_Dimensionamento'!C18,\"0.0\")&\" m² vs disponível \"&TEXT('02_Inputs'!B10,\"0.0\")&\" m²\""],
    ["=IF('07_Dimensionamento'!C19>='07_Dimensionamento'!C8,\"OK\",\"ATTENTION\")", "=\"Geração \"&TEXT('07_Dimensionamento'!C19,\"#,##0\")&\" kWh vs meta \"&TEXT('07_Dimensionamento'!C8,\"#,##0\")&\" kWh\""],
    ["=IF(COUNTIF(B6:B18,\"INCOMPATIBLE\")>0,\"INCOMPATIBLE\",IF(COUNTIF(B6:B18,\"ATTENTION\")>0,\"ATTENTION\",\"OK\"))", "=\"Pior status entre as verificações técnicas\""],
  ];
  tableStyle(sh, "A5:C20");
  sh.getRange("B6:B20").conditionalFormats.add("containsText", { text: "INCOMPATIBLE", format: { fill: "#FEE2E2", font: { color: red, bold: true } } });
  sh.getRange("B6:B20").conditionalFormats.add("containsText", { text: "ATTENTION", format: { fill: "#FEF3C7", font: { color: "#92400E", bold: true } } });
  sh.getRange("B6:B20").conditionalFormats.add("containsText", { text: "OK", format: { fill: "#ECFDF5", font: { color: green, bold: true } } });
  sh.getRange("A:C").format.autofitColumns();
}

// 01_Dashboard
{
  const sh = sheets["01_Dashboard"];
  title(sh, "Dashboard de Dimensionamento Fotovoltaico");
  sh.getRange("A5:D6").values = [["Esta planilha faz pré-dimensionamento FV preliminar. Não substitui projeto executivo nem responsabilidade técnica.", "", "", ""]];
  sh.getRange("A5:D6").format.font = { name: font, italic: true, color: "#475569" };
  const cards = [
    ["Consumo Anual", "='03_Consumo'!B21", "kWh"],
    ["Potência FV Requerida", "='07_Dimensionamento'!C11", "kWp"],
    ["Potência CC Instalada", "='07_Dimensionamento'!C14", "kWp"],
    ["Quantidade de Módulos", "='07_Dimensionamento'!C13", "módulos"],
    ["Potência do Inversor", "='07_Dimensionamento'!C15", "kW"],
    ["Relação CC/CA", "='07_Dimensionamento'!C16", "razão"],
    ["Geração Anual", "='07_Dimensionamento'!C19", "kWh"],
    ["Atendimento", "='07_Dimensionamento'!C19/'03_Consumo'!B21", "%"],
    ["Área Necessária", "='07_Dimensionamento'!C18", "m²"],
    ["Status Técnico", "='10_Validacoes'!B20", ""],
  ];
  let row = 8;
  for (let i = 0; i < cards.length; i++) {
    const col = i % 2 === 0 ? "A" : "D";
    if (i % 2 === 0 && i > 0) row += 4;
    sh.getRange(`${col}${row}:${col}${row + 2}`).format.fill = i === 9 ? lightGreen : lightBlue;
    sh.getRange(`${col}${row}`).values = [[cards[i][0]]];
    sh.getRange(`${col}${row + 1}`).formulas = [[cards[i][1]]];
    sh.getRange(`${col}${row + 2}`).values = [[cards[i][2]]];
    sh.getRange(`${col}${row}`).format.font = { name: font, size: 10, bold: true, color: dark };
    sh.getRange(`${col}${row + 1}`).format.font = { name: font, size: 15, bold: true, color: blue };
    sh.getRange(`${col}${row + 2}`).format.font = { name: font, size: 9, italic: true, color: "#64748B" };
    sh.getRange(`${col}${row}:${col}${row + 2}`).format.borders = { preset: "outside", style: "thin", color: border };
  }
  sh.getRange("A1:H35").format.columnWidth = 20;
  const chart1 = sh.charts.add("line", [sheets["09_Geracao"].getRange("A5:A17"), sheets["09_Geracao"].getRange("B5:B17"), sheets["09_Geracao"].getRange("D5:D17")]);
  chart1.title = "Consumo versus Geração FV";
  chart1.titleTextStyle.typeface = font;
  chart1.legend = { position: "top", textStyle: { typeface: font } };
  chart1.yAxis = { numberFormatCode: "#,##0", numberFormatSourceLinked: false, textStyle: { typeface: font } };
  chart1.setPosition("G8", "N23");
  const chart2 = sh.charts.add("bar", [sheets["09_Geracao"].getRange("A5:A17"), sheets["09_Geracao"].getRange("F5:F17")]);
  chart2.title = "Atendimento Mensal";
  chart2.titleTextStyle.typeface = font;
  chart2.hasLegend = false;
  chart2.yAxis = { numberFormatCode: "0%", numberFormatSourceLinked: false, textStyle: { typeface: font } };
  chart2.setPosition("G25", "N40");
}

// 11_Premissas and 12_Documentacao
{
  const sh = sheets["11_Premissas"];
  title(sh, "Premissas");
  sh.getRange("A5:E17").values = [
    ["Premissa", "Padrão", "Unidade", "Editável", "Descrição"],
    ["HSP", "Valores mensais", "h/dia", "Sim", "Horas de sol pleno equivalentes, não duração de insolação."],
    ["PR", "80% ou perdas compostas", "%", "Sim", "Desempenho do sistema após perdas."],
    ["Perdas", "Compostas", "%", "Sim", "PR usa produto dos fatores remanescentes."],
    ["Dados do módulo", "Catálogo fictício", "várias", "Sim", "Sem recomendação de fabricante."],
    ["Dados do inversor", "Catálogo fictício", "várias", "Sim", "Exige conferência manual de datasheet."],
    ["Temperatura", "Manual", "°C", "Sim", "A ferramenta não inventa temperatura de cidade."],
    ["Sombreamento", "Parâmetro de perda", "%", "Sim", "Não há simulação 3D de sombras."],
    ["Fator de área", "1,20", "fator", "Sim", "Fator técnico aproximado de ocupação."],
    ["Limites CC/CA", "0,80 a 1,35", "razão", "Sim", "Faixa preliminar configurável de alerta."],
    ["Excedente mensal", "Simplificado", "kWh", "Não", "Não modela autoconsumo horário."],
    ["Escopo", "Preliminar", "", "Não", "Não é projeto elétrico executivo."],
    ["API solar futura", "Opcional", "", "Não", "Integração externa é evolução futura."],
  ];
  header(sh, "A5:E5");
  tableStyle(sh, "A5:E17");
  sh.getRange("A:E").format.autofitColumns();
}
{
  const sh = sheets["12_Documentacao"];
  title(sh, "Documentação");
  sh.getRange("A5:B18").values = [
    ["Tópico", "Resumo"],
    ["Consumo", "Consumo anual, média mensal e média diária derivam dos 12 valores mensais."],
    ["Meta", "Energia anual alvo é o consumo anual multiplicado pela meta de atendimento."],
    ["HSP", "Horas de sol pleno representam recurso solar equivalente."],
    ["Geração", "Geração mensal é potência CC, HSP, dias do mês e PR."],
    ["PR", "Perdas detalhadas são compostas, não simplesmente somadas."],
    ["Módulos", "A quantidade requerida é arredondada para número inteiro."],
    ["Voc", "Temperatura fria eleva Voc quando o coeficiente é negativo."],
    ["Vmp", "Temperatura quente reduz Vmp com coeficiente próprio de Vmp."],
    ["Corrente", "Strings em paralelo somam corrente no MPPT."],
    ["Tensão de partida", "Incluída como diagnóstico preliminar adicional ao MPPT mínimo."],
    ["Limitações", "Sem simulação horária, sombreamento detalhado, proteções, cabos, ART ou processo da concessionária."],
    ["GitHub", "Use README.md em português."],
    ["LinkedIn", "Use a pasta linkedin/."],
  ];
  header(sh, "A5:B5");
  tableStyle(sh, "A5:B18");
  sh.getRange("A:B").format.autofitColumns();
}

wb.recalculate();

const dashboardCheck = await wb.inspect({
  kind: "table",
  range: "01_Dashboard!A1:N40",
  include: "values,formulas",
  tableMaxRows: 40,
  tableMaxCols: 14,
});
console.log(dashboardCheck.ndjson);

const stringsCheck = await wb.inspect({
  kind: "table",
  range: "08_Strings!A5:C25",
  include: "values,formulas",
  tableMaxRows: 21,
  tableMaxCols: 3,
});
console.log(stringsCheck.ndjson);

const validationCheck = await wb.inspect({
  kind: "table",
  range: "10_Validacoes!A5:C20",
  include: "values,formulas",
  tableMaxRows: 16,
  tableMaxCols: 3,
});
console.log(validationCheck.ndjson);

const errors = await wb.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

const renderSheets = [
  ["01_Dashboard", "01_visao_geral.png"],
  ["03_Consumo", "02_consumo_recurso.png"],
  ["07_Dimensionamento", "03_dimensionamento.png"],
  ["05_Modulo", "04_modulo.png"],
  ["06_Inversor", "05_inversor.png"],
  ["08_Strings", "06_strings.png"],
  ["09_Geracao", "07_geracao.png"],
  ["10_Validacoes", "08_validacao.png"],
  ["11_Premissas", "09_premissas.png"],
];
for (const [sheetName, filename] of renderSheets) {
  const blob = await wb.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`${screenshotDir}/${filename}`, new Uint8Array(await blob.arrayBuffer()));
}

const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(outputPath);
console.log(`Saved ${outputPath}`);
