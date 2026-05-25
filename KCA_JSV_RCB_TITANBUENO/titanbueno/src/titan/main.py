from pathlib import Path
import sys

if __name__ == "__main__" and __package__ is None:
    script_path = Path(__file__).resolve()
    sys.path.insert(0, str(script_path.parent.parent))
    __package__ = script_path.parent.name

from .config import DistrictScenario, FestivalScenario, NetworkConfig
from .instrumentation import assumptions_table, validation_checklist
from .plots import (
    save_district_radii_plot,
    save_district_tradeoff_plot,
    save_festival_radii_plot,
    save_festival_splitting_plot,
    save_link_budget_plot,
    save_solution_summary_plot,
)
from .radio_access import modulation_context_table, scenario_goal_table, system_parameter_table
from .report import (
    build_calculation_annex_markdown,
    build_defense_brief_markdown,
    build_report_markdown,
    write_docx_document,
    write_html_document,
    write_pdf_document,
)
from .scenario_a import analyze_financial_district
from .scenario_b import analyze_festival


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    outputs = project_root / "outputs"
    figures = outputs / "figures"
    outputs.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    config = NetworkConfig()
    district = DistrictScenario()
    festival = FestivalScenario()

    system_table = system_parameter_table(config)
    modulation_table = modulation_context_table()
    goal_table = scenario_goal_table(district, festival)
    assumptions = assumptions_table(config, district, festival)
    validation = validation_checklist()
    district_results = analyze_financial_district(district, config)
    festival_results = analyze_festival(festival, config)

    system_table.to_csv(outputs / "sistema_parametros.csv", index=False)
    modulation_table.to_csv(outputs / "contexto_mcs.csv", index=False)
    goal_table.to_csv(outputs / "objetivos_escenario.csv", index=False)
    assumptions.to_csv(outputs / "supuestos.csv", index=False)
    validation.to_csv(outputs / "validacion_rubrica.csv", index=False)
    district_results["coverage"].to_csv(outputs / "escenario_a_cobertura.csv", index=False)
    district_results["capacity"].to_csv(outputs / "escenario_a_capacidad.csv", index=False)
    festival_results["coverage"].to_csv(outputs / "escenario_b_cobertura.csv", index=False)
    festival_results["capacity"].to_csv(outputs / "escenario_b_capacidad.csv", index=False)
    festival_results["splitting"].to_csv(outputs / "escenario_b_cell_splitting.csv", index=False)

    save_link_budget_plot(district_results["coverage"], figures / "escenario_a_link_budget.png", "Scenario A: urban link budget and allowable path loss")
    save_district_radii_plot(district_results["capacity"], district_results["coverage"], figures / "escenario_a_radii.png")
    save_district_tradeoff_plot(district_results["capacity"], district.snr_required_db, figures / "escenario_a_tradeoff.png")
    save_link_budget_plot(festival_results["coverage"], figures / "escenario_b_link_budget.png", "Scenario B: festival link budget and allowable path loss")
    save_festival_radii_plot(festival_results["capacity"], figures / "escenario_b_radii.png")
    save_festival_splitting_plot(festival_results["splitting"], figures / "escenario_b_cell_splitting.png")
    save_solution_summary_plot(
        district_results["capacity"],
        festival_results["capacity"],
        festival_results["splitting"],
        figures / "resumen_solucion_operacion_nexo.png",
    )

    report_markdown = build_report_markdown(
        system_table,
        modulation_table,
        goal_table,
        district_results,
        festival_results,
        assumptions,
        validation,
    )
    annex_markdown = build_calculation_annex_markdown(district_results, festival_results, assumptions)
    defense_markdown = build_defense_brief_markdown(district_results, festival_results)

    (outputs / "informe_resultados.md").write_text(report_markdown, encoding="utf-8")
    (outputs / "anexo_calculos.md").write_text(annex_markdown, encoding="utf-8")
    (outputs / "guion_defensa.md").write_text(defense_markdown, encoding="utf-8")
    write_html_document(outputs / "informe_resultados.html", "Operacion Nexo 5G/6G - Informe tecnico", report_markdown)
    write_html_document(outputs / "anexo_calculos.html", "Operacion Nexo 5G/6G - Anexo de calculos", annex_markdown)
    write_html_document(outputs / "guion_defensa.html", "Operacion Nexo 5G/6G - Guion de defensa", defense_markdown)
    write_pdf_document(outputs / "informe_resultados.pdf", "Operacion Nexo 5G/6G - Informe tecnico", report_markdown, outputs)
    write_pdf_document(outputs / "anexo_calculos.pdf", "Operacion Nexo 5G/6G - Anexo de calculos", annex_markdown, outputs)
    write_pdf_document(outputs / "guion_defensa.pdf", "Operacion Nexo 5G/6G - Guion de defensa", defense_markdown, outputs)
    write_docx_document(outputs / "informe_resultados.docx", "Operacion Nexo 5G/6G - Informe tecnico", report_markdown, outputs)
    write_docx_document(outputs / "anexo_calculos.docx", "Operacion Nexo 5G/6G - Anexo de calculos", annex_markdown, outputs)
    write_docx_document(outputs / "guion_defensa.docx", "Operacion Nexo 5G/6G - Guion de defensa", defense_markdown, outputs)

    print("\n=== Scenario A - coverage ===")
    print(district_results["coverage"].to_string(index=False))
    print("\n=== Scenario A - capacity ===")
    print(district_results["capacity"].to_string(index=False))
    print("\n=== Scenario B - coverage ===")
    print(festival_results["coverage"].to_string(index=False))
    print("\n=== Scenario B - capacity ===")
    print(festival_results["capacity"].to_string(index=False))
    print("\n=== Scenario B - splitting ===")
    print(festival_results["splitting"].to_string(index=False))
    print(f"\nOutputs generated in: {outputs.resolve()}")
    print(f"Static dashboard ready at: {(project_root / 'index.html').resolve()}")


if __name__ == "__main__":
    main()
