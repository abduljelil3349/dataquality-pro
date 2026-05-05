# app/streamlit_app.py
import sys
import os
sys.path.append(
    os.path.dirname(os.path.dirname(__file__))
)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.quality_checks import DataQualityChecker
from core.loader import DataLoader
from core.reporter import QualityReporter
import json
import tempfile

# ── PAGE CONFIGURATION ────────────────────────────────
st.set_page_config(
    page_title="DataQuality Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1A4731;
    }
    .sub-header {
        font-size: 1rem;
        color: #6B9E7E;
        margin-bottom: 1rem;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #6B9E7E;
    }
    div[data-testid="stMetric"] {
        background: #F8FAF9;
        border: 1px solid #E8F0EC;
        border-radius: 10px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────
st.markdown(
    '<p class="main-header">🔍 DataQuality Pro</p>',
    unsafe_allow_html=True
)
st.markdown(
    '<p class="sub-header">Automated Data Quality '
    'Audit & Monitoring System — '
    'by Abduljelil Olalekan</p>',
    unsafe_allow_html=True
)
st.divider()

# ── SIDEBAR ───────────────────────────────────────────
st.sidebar.image(
    "https://img.icons8.com/color/96/data-quality.png",
    width=60
)
st.sidebar.title("DataQuality Pro")
st.sidebar.markdown("---")
st.sidebar.header("📥 Choose Data Source")

source = st.sidebar.radio(
    "Input type:",
    [
        "📁 Upload CSV / Excel",
        "🗄️ PostgreSQL Database",
        "🌐 API Endpoint"
    ]
)

dataset_name = st.sidebar.text_input(
    "Dataset name",
    "My Dataset"
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Built with:** Python · Streamlit · "
    "Plotly · pandas"
)

df = None

# ── INPUT: FILE UPLOAD ────────────────────────────────
if source == "📁 Upload CSV / Excel":
    st.subheader("📁 Upload Your Dataset")
    file = st.file_uploader(
        "Drag and drop or browse — "
        "CSV and Excel supported",
        type=["csv", "xlsx", "xls"]
    )
    if file:
        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            else:
                sheet = st.text_input(
                    "Sheet name "
                    "(leave blank for first sheet)",
                    ""
                )
                df = pd.read_excel(
                    file,
                    sheet_name=sheet if sheet else 0
                )
            st.success(
                f"✅ Successfully loaded "
                f"**{len(df):,} rows** and "
                f"**{len(df.columns)} columns** "
                f"from {file.name}"
            )
        except Exception as e:
            st.error(f"❌ Error loading file: {e}")

# ── INPUT: POSTGRESQL ─────────────────────────────────
elif source == "🗄️ PostgreSQL Database":
    st.subheader("🗄️ Connect to PostgreSQL")
    col1, col2 = st.columns(2)
    with col1:
        host = st.text_input("Host", "localhost")
        dbname = st.text_input("Database name", "")
        user = st.text_input("Username", "")
    with col2:
        port = st.text_input("Port", "5432")
        password = st.text_input(
            "Password", type="password"
        )
    query = st.text_area(
        "SQL Query",
        "SELECT * FROM your_table LIMIT 1000",
        height=100
    )
    if st.button(
        "🔌 Connect & Load Data",
        type="primary"
    ):
        conn_str = (
            f"postgresql://{user}:{password}"
            f"@{host}:{port}/{dbname}"
        )
        try:
            with st.spinner("Connecting..."):
                df = DataLoader.from_postgres(
                    conn_str, query
                )
            st.success(
                f"✅ Loaded {len(df):,} rows "
                f"from database"
            )
        except Exception as e:
            st.error(f"❌ Connection failed: {e}")

# ── INPUT: API ────────────────────────────────────────
elif source == "🌐 API Endpoint":
    st.subheader("🌐 Fetch from API")
    url = st.text_input(
        "API URL",
        "https://jsonplaceholder.typicode.com/users"
    )
    col1, col2 = st.columns(2)
    with col1:
        data_key = st.text_input(
            "JSON data key (optional)",
            ""
        )
    with col2:
        st.markdown(" ")
        st.markdown(" ")
        fetch = st.button(
            "🌐 Fetch Data", type="primary"
        )
    if fetch:
        try:
            with st.spinner("Fetching data..."):
                df = DataLoader.from_api(
                    url,
                    data_key=(
                        data_key if data_key else None
                    )
                )
            st.success(
                f"✅ Loaded {len(df):,} rows from API"
            )
        except Exception as e:
            st.error(f"❌ API failed: {e}")

# ── MAIN DASHBOARD ────────────────────────────────────
if df is not None and len(df) > 0:

    st.divider()

    # Run all checks
    with st.spinner("Running quality audit..."):
        checker = DataQualityChecker(
            df, dataset_name
        )
        score_data = checker.calculate_score()
        completeness = checker.check_completeness()
        duplicates = checker.check_duplicates()
        outliers = checker.check_outliers()
        dtypes = checker.check_dtypes()

    # ── KPI ROW ───────────────────────────────────────
    st.subheader("📊 Quality Overview")
    k1,k2,k3,k4,k5,k6 = st.columns(6)

    score = score_data['overall_score']
    score_delta = (
        "🟢 Excellent" if score >= 90 else
        "🟡 Good" if score >= 75 else
        "🟠 Needs Work" if score >= 60 else
        "🔴 Critical"
    )

    k1.metric("📋 Total Rows", f"{len(df):,}")
    k2.metric("📐 Columns", len(df.columns))
    k3.metric(
        "🏆 Quality Score",
        f"{score}/100"
    )
    k4.metric("🎓 Grade", score_data['grade'])
    k5.metric(
        "❌ Missing Cells",
        f"{completeness['total_missing_cells']:,}"
    )
    k6.metric(
        "♻️ Duplicates",
        f"{duplicates['duplicate_rows']:,}"
    )

    st.divider()

    # ── GAUGE + RADAR ─────────────────────────────────
    col_g, col_r = st.columns(2)

    with col_g:
        st.subheader("🎯 Quality Score Gauge")
        gauge_color = (
            "#639922" if score >= 75 else
            "#EF9F27" if score >= 50 else
            "#E24B4A"
        )
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            delta={
                'reference': 75,
                'increasing': {'color': "#639922"},
                'decreasing': {'color': "#E24B4A"}
            },
            domain={'x': [0, 1], 'y': [0, 1]},
            title={
                'text': (
                    f"Status: {score_data['status']}"
                ),
                'font': {'size': 16}
            },
            gauge={
                'axis': {
                    'range': [0, 100],
                    'tickwidth': 1
                },
                'bar': {'color': gauge_color},
                'bgcolor': "white",
                'steps': [
                    {
                        'range': [0, 45],
                        'color': '#FDECEA'
                    },
                    {
                        'range': [45, 75],
                        'color': '#FEF3E2'
                    },
                    {
                        'range': [75, 100],
                        'color': '#EAF3DE'
                    }
                ],
                'threshold': {
                    'line': {
                        'color': "#1A4731",
                        'width': 4
                    },
                    'thickness': 0.75,
                    'value': 75
                }
            }
        ))
        fig_gauge.update_layout(
            height=320,
            margin=dict(t=60, b=20, l=30, r=30)
        )
        st.plotly_chart(
            fig_gauge, use_container_width=True
        )

    with col_r:
        st.subheader("🕸️ Quality Dimensions")
        categories = [
            'Completeness', 'Uniqueness',
            'Consistency', 'Validity', 'Timeliness'
        ]
        values = [
            score_data['completeness_score'],
            score_data['uniqueness_score'],
            score_data['consistency_score'],
            85, 70
        ]
        fig_radar = go.Figure(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(99, 153, 34, 0.2)',
            line=dict(color='#639922', width=2),
            name='Quality Score'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[75] * 6,
            theta=categories + [categories[0]],
            fill=None,
            line=dict(
                color='#E24B4A',
                width=1,
                dash='dash'
            ),
            name='Target (75)'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            height=320,
            showlegend=True,
            legend=dict(x=0.8, y=1.1),
            margin=dict(t=60, b=20, l=40, r=40)
        )
        st.plotly_chart(
            fig_radar, use_container_width=True
        )

    st.divider()

    # ── MISSING VALUES + OUTLIERS ─────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🕳️ Missing Values by Column")
        miss_df = pd.DataFrame({
            "Column": list(
                completeness["missing_pct"].keys()
            ),
            "Missing %": list(
                completeness["missing_pct"].values()
            )
        }).sort_values("Missing %", ascending=False)
        miss_df = miss_df[
            miss_df["Missing %"] > 0
        ]

        if len(miss_df) > 0:
            miss_df["Color"] = miss_df[
                "Missing %"
            ].apply(
                lambda x:
                "#E24B4A" if x > 20 else
                "#EF9F27" if x > 5 else
                "#639922"
            )
            fig_miss = px.bar(
                miss_df,
                x="Column",
                y="Missing %",
                color="Color",
                color_discrete_map="identity",
                title=(
                    "Red > 20% · Amber > 5% · "
                    "Green ≤ 5%"
                ),
                text="Missing %"
            )
            fig_miss.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside'
            )
            fig_miss.update_layout(
                showlegend=False,
                height=350
            )
            st.plotly_chart(
                fig_miss, use_container_width=True
            )
        else:
            st.success(
                "✅ No missing values found — "
                "perfect completeness!"
            )

    with col2:
        st.subheader("📦 Outliers by Column")
        if outliers:
            out_df = pd.DataFrame([
                {
                    "Column": k,
                    "Outlier Count": v["count"],
                    "Outlier %": v["pct"]
                }
                for k, v in outliers.items()
                if v["count"] > 0
            ])
            if len(out_df) > 0:
                out_df["Color"] = out_df[
                    "Outlier %"
                ].apply(
                    lambda x:
                    "#E24B4A" if x > 10 else
                    "#EF9F27" if x > 3 else
                    "#639922"
                )
                fig_out = px.bar(
                    out_df,
                    x="Column",
                    y="Outlier Count",
                    color="Color",
                    color_discrete_map="identity",
                    title=(
                        "Red > 10% · Amber > 3% · "
                        "Green ≤ 3%"
                    ),
                    text="Outlier Count"
                )
                fig_out.update_traces(
                    textposition='outside'
                )
                fig_out.update_layout(
                    showlegend=False,
                    height=350
                )
                st.plotly_chart(
                    fig_out,
                    use_container_width=True
                )
            else:
                st.success(
                    "✅ No outliers detected!"
                )

    st.divider()

    # ── DATA TYPES TABLE ──────────────────────────────
    st.subheader("🔠 Column Data Types")
    dtype_df = pd.DataFrame([
        {
            "Column": col,
            "Data Type": dtype,
            "Category": (
                "Numeric" if col in
                dtypes["numeric_columns"]
                else "Text" if col in
                dtypes["text_columns"]
                else "DateTime"
            )
        }
        for col, dtype
        in dtypes["dtypes"].items()
    ])
    st.dataframe(
        dtype_df, use_container_width=True,
        height=200
    )

    st.divider()

    # ── KEY INSIGHT BOX ───────────────────────────────
    st.subheader("💡 Key Insight & Recommendation")
    box_color = (
        "#EAF3DE" if score >= 75 else
        "#FEF3E2" if score >= 50 else
        "#FDECEA"
    )
    border_color = (
        "#639922" if score >= 75 else
        "#EF9F27" if score >= 50 else
        "#E24B4A"
    )

    missing_cols = [
        col for col, pct
        in completeness["missing_pct"].items()
        if pct > 0
    ]
    top_missing = (
        max(
            completeness["missing_pct"].items(),
            key=lambda x: x[1]
        )
        if missing_cols else None
    )

    finding = (
        f"**{dataset_name}** scored "
        f"**{score}/100** "
        f"(Grade **{score_data['grade']}** — "
        f"{score_data['status']}). "
        f"Dataset contains {len(df):,} rows across "
        f"{len(df.columns)} columns."
    )
    impact = (
        f"{completeness['columns_with_missing']} "
        f"column(s) have missing values "
        f"({completeness['total_missing_cells']:,} "
        f"total missing cells). "
        f"{duplicates['duplicate_rows']} duplicate "
        f"row(s) detected."
    )
    if top_missing:
        impact += (
            f" Worst column: **{top_missing[0]}** "
            f"with {top_missing[1]:.1f}% missing."
        )

    st.markdown(
        f"""<div style='background:{box_color};
        border-left: 5px solid {border_color};
        padding:20px;border-radius:8px;
        line-height:1.9;font-size:14px;color:#1A1A2E'>
        <strong>FINDING:</strong><br>{finding}
        <br><br>
        <strong>IMPACT:</strong><br>{impact}
        <br><br>
        <strong>RECOMMENDED ACTION:</strong><br>
        {score_data['recommendation']}
        </div>""",
        unsafe_allow_html=True
    )

    st.divider()

    # ── DATA PREVIEW ──────────────────────────────────
    st.subheader("📋 Data Preview")
    st.dataframe(
        df.head(100), use_container_width=True
    )

    st.divider()

    # ── EXPORT ────────────────────────────────────────
    st.subheader("⬇️ Export Reports")
    dl1, dl2 = st.columns(2)

    reporter = QualityReporter(checker)

    with dl1:
        report_dict = {
            "score": score_data,
            "completeness": completeness,
            "duplicates": duplicates,
            "outliers": {
                k: v
                for k, v in outliers.items()
            }
        }
        st.download_button(
            "⬇️ Download JSON Report",
            data=json.dumps(
                report_dict,
                indent=2,
                default=str
            ),
            file_name="dq_report.json",
            mime="application/json",
            use_container_width=True,
            type="primary"
        )

    with dl2:
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.csv',
            delete=False
        ) as tmp:
            tmp_path = tmp.name
        reporter.export_csv_for_powerbi(tmp_path)
        with open(tmp_path, 'r') as f:
            csv_data = f.read()
        os.unlink(tmp_path)
        st.download_button(
            "⬇️ Download Power BI CSV",
            data=csv_data,
            file_name="powerbi_data.csv",
            mime="text/csv",
            use_container_width=True
        )

# ── WELCOME SCREEN ────────────────────────────────────
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(
            "**📁 Upload a file**\n\n"
            "CSV or Excel — any dataset, "
            "any industry"
        )
    with col2:
        st.info(
            "**🗄️ Connect a database**\n\n"
            "PostgreSQL — query your "
            "live data directly"
        )
    with col3:
        st.info(
            "**🌐 Pull from an API**\n\n"
            "Any REST API — fetch and "
            "audit in seconds"
        )

    st.markdown("### 📊 What gets checked:")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            "✅ **Completeness**\n\n"
            "Missing values per column"
        )
        st.markdown(
            "✅ **Uniqueness**\n\n"
            "Duplicate row detection"
        )
    with c2:
        st.markdown(
            "✅ **Outliers**\n\n"
            "IQR-based outlier detection"
        )
        st.markdown(
            "✅ **Consistency**\n\n"
            "Value range validation"
        )
    with c3:
        st.markdown(
            "✅ **Data Types**\n\n"
            "Column type classification"
        )
        st.markdown(
            "✅ **Quality Score**\n\n"
            "0–100 score with A–F grade"
        )

    st.markdown("---")
    st.markdown(
        "*👈 Choose a data source from "
        "the left to get started*"
    )