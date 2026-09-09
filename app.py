from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.scenario import load_yaml, render_markdown_report, run_scenario


ROOT = Path(__file__).resolve().parent


st.set_page_config(page_title="Calculadora de Dimensionamento Fotovoltaico", layout="wide")
st.title("Calculadora de Dimensionamento Fotovoltaico")
st.caption("Pré-dimensionamento conectado à rede. Não substitui projeto executivo nem responsabilidade técnica.")

base = load_yaml(ROOT / "config" / "default_scenario.yaml")

with st.sidebar:
    st.header("Entradas")
    mode = st.selectbox("Modo", ["Simples", "Intermediário", "Avançado"], index=2)
    avg_consumption = st.number_input("Consumo médio mensal (kWh)", min_value=1.0, value=float(sum(base["monthly_consumption_kwh"]) / 12), step=10.0)
    coverage = st.slider("Meta de atendimento", 0.7, 1.2, float(base["coverage_target"]), 0.05)
    hsp = st.number_input("HSP média (h/dia)", min_value=0.1, value=float(sum(base["monthly_hsp"]) / 12), step=0.1)
    module_power = st.number_input("Potência do módulo (Wp)", min_value=100.0, value=float(base["module"]["power_wp"]), step=10.0)
    inverter_power = st.number_input("Potência CA do inversor (kW)", min_value=0.5, value=float(base["inverter"]["ac_power_kw"]), step=0.5)

config = dict(base)
config["monthly_consumption_kwh"] = [avg_consumption] * 12
config["monthly_hsp"] = [hsp] * 12
config["coverage_target"] = coverage
config["module"] = dict(base["module"])
config["module"]["power_wp"] = module_power
config["inverter"] = dict(base["inverter"])
config["inverter"]["ac_power_kw"] = inverter_power
config["performance_ratio"] = float(base["performance_ratio"])
config["losses"] = {}

with st.sidebar:
    if mode == "Simples":
        config["performance_ratio"] = st.slider("Performance Ratio", 0.50, 0.95, float(base["performance_ratio"]), 0.01)
    else:
        st.subheader("Consumo mensal")
        config["monthly_consumption_kwh"] = [
            st.number_input(f"Mês {idx + 1} (kWh)", min_value=1.0, value=float(value), step=10.0, key=f"consumo_{idx}")
            for idx, value in enumerate(base["monthly_consumption_kwh"])
        ]
        st.subheader("HSP mensal")
        config["monthly_hsp"] = [
            st.number_input(f"HSP mês {idx + 1}", min_value=0.1, value=float(value), step=0.1, key=f"hsp_{idx}")
            for idx, value in enumerate(base["monthly_hsp"])
        ]
        st.subheader("Perdas detalhadas")
        config["losses"] = {
            name: st.slider(label, 0.0, 0.30, float(base["losses"].get(name, 0.0)), 0.005)
            for name, label in [
                ("temperature", "Temperatura"),
                ("soiling", "Sujeira"),
                ("mismatch", "Mismatch"),
                ("shading", "Sombreamento"),
                ("dc_cables", "Cabos CC"),
                ("ac_cables", "Cabos CA"),
                ("inverter", "Inversor"),
                ("availability", "Indisponibilidade"),
                ("other", "Outras"),
            ]
        }
        config["available_area_m2"] = st.number_input("Área disponível (m²)", min_value=1.0, value=float(base["available_area_m2"]), step=5.0)
        config["minimum_temperature_c"] = st.number_input("Temperatura ambiente mínima (°C)", value=float(base["minimum_temperature_c"]), step=1.0)
        config["maximum_cell_temperature_c"] = st.number_input("Temperatura máxima da célula (°C)", value=float(base["maximum_cell_temperature_c"]), step=1.0)

if mode == "Avançado":
    with st.sidebar.expander("Dados elétricos do módulo", expanded=False):
        config["module"]["voc_v"] = st.number_input("Voc (V)", value=float(config["module"]["voc_v"]))
        config["module"]["vmp_v"] = st.number_input("Vmp (V)", value=float(config["module"]["vmp_v"]))
        config["module"]["isc_a"] = st.number_input("Isc (A)", value=float(config["module"]["isc_a"]))
        config["module"]["imp_a"] = st.number_input("Imp (A)", value=float(config["module"]["imp_a"]))
        config["module"]["voc_temp_coeff_pct_c"] = st.number_input("Coeficiente Voc (%/°C)", value=float(config["module"]["voc_temp_coeff_pct_c"]))
        config["module"]["vmp_temp_coeff_pct_c"] = st.number_input("Coeficiente Vmp (%/°C)", value=float(config["module"]["vmp_temp_coeff_pct_c"]))
        config["module"]["isc_temp_coeff_pct_c"] = st.number_input("Coeficiente Isc (%/°C)", value=float(config["module"]["isc_temp_coeff_pct_c"]))
        config["module"]["imp_temp_coeff_pct_c"] = st.number_input("Coeficiente Imp (%/°C)", value=float(config["module"].get("imp_temp_coeff_pct_c") or 0.0))
    with st.sidebar.expander("Dados elétricos do inversor", expanded=False):
        config["inverter"]["max_dc_power_kwp"] = st.number_input("Potência FV/CC máxima do inversor (kWp)", value=float(config["inverter"]["max_dc_power_kwp"]))
        config["inverter"]["max_dc_voltage_v"] = st.number_input("Tensão CC máxima (V)", value=float(config["inverter"]["max_dc_voltage_v"]))
        config["inverter"]["startup_voltage_v"] = st.number_input("Tensão de partida (V)", value=float(config["inverter"]["startup_voltage_v"]))
        config["inverter"]["mppt_min_voltage_v"] = st.number_input("Tensão mínima MPPT (V)", value=float(config["inverter"]["mppt_min_voltage_v"]))
        config["inverter"]["mppt_max_voltage_v"] = st.number_input("Tensão máxima MPPT (V)", value=float(config["inverter"]["mppt_max_voltage_v"]))
        config["inverter"]["max_operating_current_per_input_a"] = st.number_input("Corrente operacional máxima por entrada (A)", value=float(config["inverter"]["max_operating_current_per_input_a"]))
        config["inverter"]["max_operating_current_per_mppt_a"] = st.number_input("Corrente operacional máxima por MPPT (A)", value=float(config["inverter"]["max_operating_current_per_mppt_a"]))
        config["inverter"]["max_short_circuit_current_per_input_a"] = st.number_input("Corrente Isc máxima por entrada (A)", value=float(config["inverter"]["max_short_circuit_current_per_input_a"]))
        config["inverter"]["max_short_circuit_current_per_mppt_a"] = st.number_input("Corrente Isc máxima por MPPT (A)", value=float(config["inverter"]["max_short_circuit_current_per_mppt_a"]))
        config["inverter"]["mppt_count"] = st.number_input("Quantidade de MPPTs", min_value=1, value=int(config["inverter"]["mppt_count"]), step=1)
        config["inverter"]["inputs_per_mppt"] = st.number_input("Entradas por MPPT", min_value=1, value=int(config["inverter"]["inputs_per_mppt"]), step=1)
        config["max_voltage_utilization_pct"] = st.slider("Uso máximo da tensão CC", 0.80, 1.00, float(config.get("max_voltage_utilization_pct", 0.95)), 0.01)

try:
    results = run_scenario(config)
except Exception as exc:
    st.error(str(exc))
    st.stop()

tabs = st.tabs(["Visão geral", "Consumo e recurso", "Dimensionamento", "Módulo", "Inversor", "Strings", "Geração mensal", "Validação técnica", "Premissas"])

with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Potência FV requerida", f"{results['sizing']['required_pv_power_kwp']:.2f} kWp")
    c2.metric("Potência CC instalada", f"{results['sizing']['installed_dc_power_kwp']:.2f} kWp")
    c3.metric("Módulos", f"{results['sizing']['module_count']}")
    c4.metric("Status técnico", results["technical_status"])
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Potência do inversor", f"{results['inverter']['ac_power_kw']:.2f} kW")
    c6.metric("CC/CA", f"{results['sizing']['dc_ac_ratio']:.2f}")
    c7.metric("Geração anual", f"{results['sizing']['annual_generation_kwh']:.0f} kWh")
    c8.metric("Área técnica", f"{results['sizing']['technical_area_m2']:.1f} m²")

with tabs[1]:
    st.dataframe(pd.DataFrame(results["monthly"]), use_container_width=True)

with tabs[2]:
    st.dataframe(pd.DataFrame([results["consumption"] | results["resource"] | results["sizing"]]), use_container_width=True)

with tabs[3]:
    st.subheader("Módulo")
    st.json(results["module"])

with tabs[4]:
    st.subheader("Inversor")
    st.json(results["inverter"])

with tabs[5]:
    strings = results["strings"]
    st.metric("Total de strings", strings["total_strings"])
    for idx, string_modules in enumerate(strings["mppt_string_modules"], start=1):
        text = " | ".join([f"String {n + 1}: {modules} módulos" for n, modules in enumerate(string_modules)]) or "sem strings"
        st.write(f"MPPT {idx}: {text}")
    st.json(strings)

with tabs[6]:
    monthly_df = pd.DataFrame(results["monthly"])
    st.subheader("Consumo mensal versus geração FV")
    st.line_chart(monthly_df.set_index("month")[["consumption_kwh", "generation_kwh"]])
    st.subheader("Excedente e déficit mensal")
    st.bar_chart(monthly_df.set_index("month")[["surplus_kwh", "deficit_kwh"]])
    st.dataframe(monthly_df, use_container_width=True)

with tabs[7]:
    validation_df = pd.DataFrame(results["validations"])
    st.dataframe(validation_df, use_container_width=True)
    st.download_button("Baixar relatório em Markdown", render_markdown_report(results), file_name="relatorio_dimensionamento.md")

with tabs[8]:
    st.markdown(
        """
        - HSP é tratada como horas de sol pleno equivalentes.
        - PR pode ser informado diretamente no modo simples ou calculado por perdas compostas nos modos intermediário e avançado.
        - Coeficientes térmicos são informados em %/°C e convertidos internamente.
        - Vmp usa coeficiente próprio de Vmp; Isc não é usado para corrigir Vmp.
        - A ferramenta é preliminar e não substitui projeto executivo.
        """
    )
