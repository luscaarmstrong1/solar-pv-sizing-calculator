from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parents[1] / "outputs"


def run(command: list[str]) -> None:
    subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


def clean() -> None:
    for path in ROOT.rglob("__pycache__"):
        shutil.rmtree(path, ignore_errors=True)
    for path in ROOT.rglob(".pytest_cache"):
        shutil.rmtree(path, ignore_errors=True)
    for path in ROOT.rglob("*.pyc"):
        path.unlink(missing_ok=True)
    for path in ROOT.rglob("*.inspect.ndjson"):
        path.unlink(missing_ok=True)


def package() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    zip_path = OUT / "solar-pv-sizing-calculator-FINAL-PTBR.zip"
    skip_dirs = {"node_modules", "__pycache__", ".pytest_cache", ".git"}
    skip_suffixes = {".pyc", ".ndjson"}
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as zf:
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or any(part in skip_dirs for part in path.parts):
                continue
            if path.suffix in skip_suffixes:
                continue
            zf.write(path, Path("solar-pv-sizing-calculator") / path.relative_to(ROOT))

    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    (OUT / "solar-pv-sizing-calculator-FINAL-PTBR.sha256.txt").write_text(
        f"{digest}  {zip_path.name}\n", encoding="utf-8"
    )
    shutil.copy2(ROOT / "Solar_PV_Sizing_Calculator.xlsx", OUT / "Solar_PV_Sizing_Calculator.xlsx")
    return zip_path


def main() -> None:
    run(["python", "scripts/run_sizing.py"])
    run(["python", "scripts/validate_model.py"])
    run(["pytest", "tests", "-q", "-p", "no:cacheprovider"])
    run(["python", "-m", "compileall", "app.py", "src", "scripts"])
    run(["node", "scripts/build_workbook.mjs"])
    run(["python", "scripts/gerar_materiais_portfolio.py"])
    clean()

    results = json.loads((ROOT / "outputs" / "sizing_results.json").read_text(encoding="utf-8"))
    resumo = {
        "status": "CONCLUÍDO",
        "zip_final": "outputs/solar-pv-sizing-calculator-FINAL-PTBR.zip",
        "planilha": "outputs/Solar_PV_Sizing_Calculator.xlsx",
        "cenario_base": {
            "nome": results["scenario_name"],
            "potencia_requerida_kwp": results["sizing"]["required_pv_power_kwp"],
            "potencia_instalada_kwp": results["sizing"]["installed_dc_power_kwp"],
            "modulos": results["sizing"]["module_count"],
            "geracao_anual_kwh": results["sizing"]["annual_generation_kwh"],
            "relacao_cc_ca": results["sizing"]["dc_ac_ratio"],
            "status_tecnico": results["technical_status"],
        },
        "validacoes": {
            "motor_python": "OK",
            "validacao_cenarios": "OK",
            "pytest": "OK",
            "compileall": "OK",
            "planilha_excel": "OK",
            "materiais_portfolio": "OK",
        },
    }
    (ROOT / "outputs" / "resumo_portfolio.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    zip_path = package()
    print(f"Projeto finalizado: {zip_path}")


if __name__ == "__main__":
    main()
