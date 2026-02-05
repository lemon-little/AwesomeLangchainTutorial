from typing import Callable, Dict, Any
import os
import json
import re
from datetime import datetime

from .config import Settings


ToolFunc = Callable[[Settings, Dict[str, Any], Dict[str, Any]], Dict[str, Any]]


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, ToolFunc] = {}

    def register(self, name: str, func: ToolFunc) -> None:
        self.tools[name] = func

    def get(self, name: str) -> ToolFunc:
        if name not in self.tools:
            raise ValueError(f"工具未注册: {name}")
        return self.tools[name]

    def all(self) -> Dict[str, ToolFunc]:
        return self.tools


def _safe_select(sql: str) -> bool:
    s = sql.strip().lower()
    if ";" in s:
        return False
    if not s.startswith("select"):
        return False
    return True


def _ensure_limit(sql: str, limit: int = 10000) -> str:
    if " limit " in sql.lower():
        return sql
    return f"{sql} limit {limit}"


def mysql_query(settings: Settings, context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    import pandas as pd
    import pymysql

    sql = params.get("sql") or "select * from sample_finance"
    if not _safe_select(sql):
        raise ValueError("仅允许单条 SELECT 语句")
    sql = _ensure_limit(sql)
    conn = pymysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_db,
        charset="utf8mb4",
    )
    df = pd.read_sql(sql, conn)
    conn.close()
    output_dir = settings.output_dir
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df.to_csv(path, index=False)
    context["dataframe"] = df
    return {"rows": len(df), "path": path}


def data_clean(settings: Settings, context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    import pandas as pd
    df: pd.DataFrame = context.get("dataframe")
    if df is None:
        raise ValueError("缺少待清洗数据")
    df = df.copy()
    df = df.drop_duplicates()
    df = df.fillna(method="ffill").fillna(method="bfill")
    context["dataframe"] = df
    output_dir = settings.output_dir
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df.to_csv(path, index=False)
    return {"rows": len(df), "path": path}


def eda(settings: Settings, context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    import pandas as pd
    df: pd.DataFrame = context.get("dataframe")
    if df is None:
        raise ValueError("缺少数据")
    desc = df.describe(include="all").fillna("").to_dict()
    corr = {}
    numeric_df = df.select_dtypes(include="number")
    if not numeric_df.empty:
        corr = numeric_df.corr().to_dict()
    result = {"describe": desc, "correlation": corr}
    output_dir = settings.output_dir
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"eda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    context["eda"] = result
    return {"path": path}


def modeling(settings: Settings, context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    import pandas as pd
    from sklearn.ensemble import IsolationForest
    df: pd.DataFrame = context.get("dataframe")
    if df is None:
        raise ValueError("缺少数据")
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        return {"message": "无数值字段，跳过建模"}
    numeric_df = numeric_df.fillna(0)
    model = IsolationForest(random_state=42, contamination=0.05)
    preds = model.fit_predict(numeric_df)
    df_out = df.copy()
    df_out["anomaly_flag"] = preds
    context["modeling"] = {"anomaly_count": int((preds == -1).sum())}
    output_dir = settings.output_dir
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df_out.to_csv(path, index=False)
    return {"path": path, "anomaly_count": context["modeling"]["anomaly_count"]}


def visualization(settings: Settings, context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    df: pd.DataFrame = context.get("dataframe")
    if df is None:
        raise ValueError("缺少数据")
    output_dir = settings.output_dir
    os.makedirs(output_dir, exist_ok=True)
    images = []
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        col = numeric_cols[0]
        plt.figure(figsize=(8, 4))
        sns.histplot(df[col].dropna(), kde=True)
        path = os.path.join(output_dir, f"hist_{col}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        images.append(path)
    if len(numeric_cols) >= 2:
        plt.figure(figsize=(6, 6))
        sns.scatterplot(data=df, x=numeric_cols[0], y=numeric_cols[1])
        path = os.path.join(output_dir, f"scatter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        images.append(path)
    context["visuals"] = images
    return {"images": images}


def report_tool(settings: Settings, context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    from .report import ReportRenderer
    renderer = ReportRenderer(settings)
    report = renderer.render(context, template_path=params.get("template_path"))
    return report


def web_search(settings: Settings, context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    query = params.get("query", "")
    if not query:
        return {"results": []}
    if settings.tavily_api_key:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.tavily_api_key)
        data = client.search(query=query, max_results=5)
        return {"results": data.get("results", [])}
    return {"results": []}


def _parse_number(value: str) -> float:
    return float(value.replace(",", ""))


def _unit_multiplier(unit: str) -> float:
    if unit in ["亿", "亿元"]:
        return 1e8
    if unit in ["万", "万元"]:
        return 1e4
    if unit in ["千", "千元"]:
        return 1e3
    return 1.0


def _extract_revenue_by_year(text: str, years: list[int]) -> Dict[int, float]:
    if not text:
        return {}
    pattern = re.compile(r"(20\d{2}).{0,20}?(营收|营业收入|收入).{0,20}?([0-9][0-9,\.]*)(亿|亿元|万|万元|千|千元|元)")
    results: Dict[int, float] = {}
    for match in pattern.finditer(text):
        year = int(match.group(1))
        if year not in years:
            continue
        value = _parse_number(match.group(3))
        unit = match.group(4)
        results[year] = value * _unit_multiplier(unit)
    return results


def public_data_ingest(settings: Settings, context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    import pandas as pd
    import pymysql
    import trafilatura
    names = params.get("companies", [])
    if not names:
        names = ["迈为股份", "捷佳伟创", "拉普拉斯", "奥特维", "晶盛机电", "连城数控"]
    years = params.get("years", [2024, 2023, 2022])
    years = [int(y) for y in years]
    urls = params.get("urls", [])
    rows = []
    for name in names:
        source_url = None
        snippet = None
        text_content = None
        if urls:
            for u in urls:
                if name in u:
                    source_url = u
                    break
        if settings.tavily_api_key:
            try:
                from tavily import TavilyClient
                client = TavilyClient(api_key=settings.tavily_api_key)
                data = client.search(query=f"{name} 年报 营业收入 数据", max_results=3)
                items = data.get("results", [])
                if items:
                    source_url = items[0].get("url")
                    snippet = items[0].get("content")
            except Exception:
                source_url = None
                snippet = None
        if source_url:
            try:
                downloaded = trafilatura.fetch_url(source_url)
                if downloaded:
                    text_content = trafilatura.extract(downloaded)
            except Exception:
                text_content = None
        extracted = _extract_revenue_by_year(text_content or "", years)
        if extracted:
            for year, revenue in extracted.items():
                rows.append(
                    {
                        "company": name,
                        "year": year,
                        "revenue": revenue,
                        "source": "tavily" if settings.tavily_api_key else "url",
                        "source_url": source_url,
                        "snippet": (text_content or snippet or "")[:500],
                    }
                )
        else:
            rows.append(
                {
                    "company": name,
                    "year": years[0],
                    "revenue": None,
                    "source": "tavily" if source_url else "pending",
                    "source_url": source_url,
                    "snippet": (text_content or snippet or "")[:500],
                }
            )
    df = pd.DataFrame(rows)
    conn = pymysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_db,
        charset="utf8mb4",
    )
    with conn.cursor() as cursor:
        cursor.execute(
            """
            create table if not exists sample_finance (
                company varchar(255),
                year int,
                revenue double,
                source varchar(255),
                source_url text,
                snippet text
            )
            """
        )
        cursor.execute("delete from sample_finance")
        for _, row in df.iterrows():
            cursor.execute(
                "insert into sample_finance (company, year, revenue, source, source_url, snippet) values (%s, %s, %s, %s, %s, %s)",
                (
                    row["company"],
                    int(row["year"]),
                    row["revenue"],
                    row["source"],
                    row["source_url"],
                    row["snippet"],
                ),
            )
    conn.commit()
    conn.close()
    context["dataframe"] = df
    return {"rows": len(df)}


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register("mysql_query", mysql_query)
    registry.register("data_clean", data_clean)
    registry.register("eda", eda)
    registry.register("modeling", modeling)
    registry.register("visualization", visualization)
    registry.register("report", report_tool)
    registry.register("web_search", web_search)
    registry.register("public_data_ingest", public_data_ingest)
    return registry
