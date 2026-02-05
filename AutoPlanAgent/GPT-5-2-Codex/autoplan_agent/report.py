from typing import Dict, Any, List, Optional
import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import Settings
from .schemas import AnalysisReport


class ReportRenderer:
    def __init__(self, settings: Settings):
        self.settings = settings
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def _build_report_model(self, context: Dict[str, Any]) -> AnalysisReport:
        eda = context.get("eda", {})
        modeling = context.get("modeling", {})
        visuals: List[str] = context.get("visuals", [])
        findings = []
        if "describe" in eda:
            findings.append("已完成描述性统计与字段概览")
        if "correlation" in eda:
            findings.append("已完成相关性分析")
        if modeling:
            findings.append(f"异常检测数量: {modeling.get('anomaly_count', 0)}")
        return AnalysisReport(
            executive_summary="本次分析完成数据获取、清洗、EDA、建模与可视化输出。",
            data_sources=["MySQL", "公开数据"],
            methods=["描述性统计", "相关性分析", "异常检测"],
            findings=findings,
            recommendations=["关注异常样本与关键指标趋势变化"],
            artifacts=visuals,
        )

    def render(self, context: Dict[str, Any], template_path: Optional[str] = None) -> Dict[str, Any]:
        os.makedirs(self.settings.output_dir, exist_ok=True)
        report = self._build_report_model(context)
        md_path = os.path.join(self.settings.output_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        html_path = md_path.replace(".md", ".html")
        template_name = "report.md.j2"
        if template_path:
            template_dir, template_name = os.path.split(template_path)
            env = Environment(loader=FileSystemLoader(template_dir))
            md = env.get_template(template_name).render(report=report.model_dump())
        else:
            md = self.env.get_template("report.md.j2").render(report=report.model_dump())
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md)
        html = self.env.get_template("report.html.j2").render(report=report.model_dump())
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        pdf_path = self._render_pdf(report)
        return {"markdown": md_path, "html": html_path, "pdf": pdf_path, "summary": report.model_dump()}

    def _render_pdf(self, report: AnalysisReport) -> Optional[str]:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except Exception:
            return None
        pdf_path = os.path.join(self.settings.output_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        y = height - 40
        c.setFont("Helvetica", 14)
        c.drawString(40, y, "数据分析报告")
        c.setFont("Helvetica", 10)
        y -= 30
        c.drawString(40, y, report.executive_summary)
        y -= 20
        for item in report.findings:
            c.drawString(40, y, f"- {item}")
            y -= 14
            if y < 60:
                c.showPage()
                y = height - 40
        c.save()
        return pdf_path
