from pathlib import Path
import pandas as pd
import re, unicodedata

RAW = Path("data/raw")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

INPUT = RAW / "secmca_remesas_hn.xlsx"   # <- si tu nombre cambia, ajusta aquí
SHEET = 0                                # o el nombre de la hoja si lo sabes

def norm(s: str) -> str:
    s = (s or "").strip()
    s = s.lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^\w]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

def looks_like_period(x: str) -> bool:
    if not isinstance(x, str): x = str(x)
    x = x.strip()
    pats = [
        r"^\d{4}$",                # 2001
        r"^\d{4}[-/]\d{1,2}$",     # 2001-01
        r"^\d{4}\d{2}$",           # 200101
        r"^\d{4}[mM]\d{2}$",       # 2001M01
        r"^\d{4}[qQtT]\d$",        # 2001Q1
    ]
    return any(re.match(p, x) for p in pats)

def parse_period(x: str) -> pd.Timestamp:
    s = str(x).strip()
    m = re.match(r"^(\d{4})$", s)
    if m: return pd.Timestamp(int(m.group(1)), 12, 31)
    m = re.match(r"^(\d{4})[-/](\d{1,2})$", s)
    if m: return pd.Timestamp(int(m.group(1)), int(m.group(2)), 1)
    m = re.match(r"^(\d{4})(\d{2})$", s)
    if m: return pd.Timestamp(int(m.group(1)), int(m.group(2)), 1)
    m = re.match(r"^(\d{4})[mM](\d{2})$", s)
    if m: return pd.Timestamp(int(m.group(1)), int(m.group(2)), 1)
    m = re.match(r"^(\d{4})[qQtT](\d)$", s)
    if m:
        y, q = int(m.group(1)), int(m.group(2))
        return pd.Timestamp(y, (q-1)*3+1, 1)
    return pd.NaT

def main():
    # 1) Lee sin encabezado para detectar dónde empieza la tabla real
    df0 = pd.read_excel(INPUT, sheet_name=SHEET, header=None, dtype=str, engine="openpyxl")
    df0 = df0.fillna("")
    # hfila: fila de encabezados reales (busca "País" o la fila anterior a "Honduras")
    hfila = None
    for i, row in df0.iterrows():
        joined = " | ".join(row.astype(str).tolist()).lower()
        if "país" in joined or "pais" in joined:
            hfila = i; break
    if hfila is None:
        for i, row in df0.iterrows():
            joined = " | ".join(row.astype(str).tolist()).lower()
            if "honduras" in joined:
                hfila = max(0, i-1); break
    if hfila is None:
        # fallback: primera fila con ≥3 “periodos”
        for i, row in df0.iterrows():
            vals = [str(v).strip() for v in row.tolist()]
            if sum(looks_like_period(v) for v in vals) >= 3:
                hfila = i-1 if i>0 else i; break
    if hfila is None:
        raise SystemExit("No pude localizar encabezados. Abre el XLSX y dime la fila donde están (ej. 6).")

    # 2) Relee usando esa fila como header
    df = pd.read_excel(INPUT, sheet_name=SHEET, header=hfila, dtype=str, engine="openpyxl")
    df.columns = [norm(str(c)) for c in df.columns]

    # 3) Filtra Honduras si existe columna pais
    if "pais" in df.columns:
        df = df[df["pais"].astype(str).str.contains("honduras", case=False, na=False)]

    # 4) Identifica columnas de periodo (ancho → largo)
    id_cols, period_cols = [], []
    for c in df.columns:
        if c in ("pais","serie","variable","unidad","medida","concepto"):
            id_cols.append(c); continue
        # ¿la cabecera parece periodo?
        if looks_like_period(c):
            period_cols.append(c)
    if not period_cols:
        # intenta detectar por contenido de las primeras filas
        for c in df.columns:
            sample = df[c].head(8).astype(str).tolist()
            if sum(looks_like_period(v) for v in sample) >= 3:
                period_cols.append(c)
        # si aún nada, asume todas menos la primera son periodos
        if not period_cols and len(df.columns) > 1:
            id_cols = df.columns[:1].tolist()
            period_cols = df.columns[1:].tolist()

    if not period_cols:
        raise SystemExit("No detecté columnas de periodo. Revisa el archivo.")

    long = df.melt(id_vars=id_cols, value_vars=period_cols,
                   var_name="periodo", value_name="valor")

    # 5) Limpia números y parsea fecha
    s = (long["valor"].astype(str)
         .str.replace("\u00a0", "", regex=False)
         .str.replace(" ", "", regex=False)
         .str.replace(",", "", regex=False)
         .str.replace(";", "", regex=False)
         .str.replace(r"[^0-9\.-]", "", regex=True))
    long["valor"] = pd.to_numeric(s, errors="coerce")
    long["fecha"] = long["periodo"].map(parse_period)

    out = (long[["fecha","valor"]]
           .dropna(subset=["fecha","valor"])
           .sort_values("fecha")
           .rename(columns={"valor":"remesas_ingreso_usd"})
           .reset_index(drop=True))

    out.to_csv(OUT/"remesas_hn_mensual.csv", index=False)

    if not out.empty:
        y = out.copy()
        y["anio"] = y["fecha"].dt.year
        y = y.groupby("anio", as_index=False)["remesas_ingreso_usd"].sum()
        y.to_csv(OUT/"remesas_hn_anual.csv", index=False)

        q = out.copy()
        q["anio"] = q["fecha"].dt.year
        q["tri"]  = q["fecha"].dt.quarter
        q = q.groupby(["anio","tri"], as_index=False)["remesas_ingreso_usd"].sum()
        q["fecha"] = pd.PeriodIndex(year=q["anio"], quarter=q["tri"]).to_timestamp(how="end")
        q = q[["fecha","anio","tri","remesas_ingreso_usd"]]
        q.to_csv(OUT/"remesas_hn_trimestral.csv", index=False)

    print("✅ Listo (desde XLSX): data/processed/remesas_hn_mensual.csv + anual/trimestral")

if __name__ == "__main__":
    main()
