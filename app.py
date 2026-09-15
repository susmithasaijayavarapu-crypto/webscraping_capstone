import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="Weather Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished metric cards
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# DATA LOADING FUNCTION
# ==========================================
@st.cache_data
def load_data_from_sqlite(db_path="weather_data.db"):
    """Connects to SQLite database and pulls records into Pandas DataFrames."""
    conn = sqlite3.connect(db_path)
    df_records = pd.read_sql("SELECT * FROM weather_records", conn)
    df_summary = pd.read_sql("SELECT * FROM weather_summary", conn)
    conn.close()

    # Ensure datetime conversion
    df_records["scraped_at"] = pd.to_datetime(df_records["scraped_at"])
    return df_records, df_summary


try:
    df, df_summary = load_data_from_sqlite()
except Exception as e:
    st.error(f"Error loading database: {e}")
    st.info(
        "Ensure 'weather_data.db' is located in the root folder of your application."
    )
    st.stop()


# ==========================================
# SIDEBAR FILTERS & INTERACTION
# ==========================================
st.sidebar.header("🔍 Filter Options")
st.sidebar.markdown(
    "Use the controls below to filter the global weather records."
)

# 1. Temperature Unit Toggle
unit_choice = st.sidebar.radio(
    "Display Temperature In:", options=["Celsius (°C)", "Fahrenheit (°F)"]
)
temp_col = "temp_celsius" if unit_choice == "Celsius (°C)" else "temperature"
unit_symbol = "°C" if unit_choice == "Celsius (°C)" else "°F"

# 2. Category Multi-Select Filter
all_categories = df["temp_category"].dropna().unique().tolist()
selected_categories = st.sidebar.multiselect(
    "Filter by Weather Category:",
    options=all_categories,
    default=all_categories,
)

# 3. Range Slider Filter
min_temp = float(df[temp_col].min())
max_temp = float(df[temp_col].max())
temp_range = st.sidebar.slider(
    f"Temperature Range ({unit_symbol}):",
    min_value=min_temp,
    max_value=max_temp,
    value=(min_temp, max_temp),
)

# Apply Filters
filtered_df = df[
    (df["temp_category"].isin(selected_categories))
    & (df[temp_col] >= temp_range[0])
    & (df[temp_col] <= temp_range[1])
]


# ==========================================
# DASHBOARD HEADER & KPI METRICS
# ==========================================
st.title("🌐 Global City Weather Analytics")
st.markdown(
    "An interactive dashboard displaying live-scraped temperature records across global cities stored in a **SQLite** database."
)

st.markdown("---")

# Top KPI Columns
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="Total Cities Filtered", value=len(filtered_df))

with kpi2:
    avg_val = (
        filtered_df[temp_col].mean() if not filtered_df.empty else 0
    )
    st.metric(
        label=f"Avg Temperature ({unit_symbol})", value=f"{avg_val:.1f} {unit_symbol}"
    )

with kpi3:
    if not filtered_df.empty:
        max_row = filtered_df.loc[filtered_df[temp_col].idxmax()]
        st.metric(
            label="Hottest City",
            value=f"{max_row['city']}",
            delta=f"{max_row[temp_col]:.1f} {unit_symbol}",
        )
    else:
        st.metric(label="Hottest City", value="N/A")

with kpi4:
    if not filtered_df.empty:
        min_row = filtered_df.loc[filtered_df[temp_col].idxmin()]
        st.metric(
            label="Coldest City",
            value=f"{min_row['city']}",
            delta=f"{min_row[temp_col]:.1f} {unit_symbol}",
            delta_color="inverse",
        )
    else:
        st.metric(label="Coldest City", value="N/A")

st.markdown("---")


# ==========================================
# DATA VISUALIZATIONS (3 RELEVANT CHARTS)
# ==========================================

tab1, tab2 = st.tabs(["📊 Visual Analytics", "📋 Raw Database View"])

with tab1:
    col_left, col_right = st.columns(2)

    # VISUALIZATION 1: Distribution Histogram
    with col_left:
        st.subheader("1. Temperature Distribution")
        st.markdown("Frequency distribution of city temperatures.")
        fig_hist = px.histogram(
            filtered_df,
            x=temp_col,
            color="temp_category",
            nbins=15,
            labels={
                temp_col: f"Temperature ({unit_symbol})",
                "temp_category": "Category",
            },
            color_discrete_map={
                "Cold": "#1f77b4",
                "Mild": "#2ca02c",
                "Hot": "#d62728",
            },
            template="plotly_white",
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # VISUALIZATION 2: Category Breakdown Donut Chart
    with col_right:
        st.subheader("2. Weather Category Share")
        st.markdown("Proportion of cities across climate thresholds.")
        fig_pie = px.pie(
            filtered_df,
            names="temp_category",
            hole=0.4,
            color="temp_category",
            color_discrete_map={
                "Cold": "#1f77b4",
                "Mild": "#2ca02c",
                "Hot": "#d62728",
            },
            template="plotly_white",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # VISUALIZATION 3: Top 15 Extremes Bar Chart
    st.subheader("3. Top 15 Highest Temperature Cities")
    st.markdown("Ranking of the top cities matching your selected filter parameters.")
    top_cities = filtered_df.nlargest(15, temp_col).sort_values(
        temp_col, ascending=True
    )

    fig_bar = px.bar(
        top_cities,
        x=temp_col,
        y="city",
        orientation="h",
        color=temp_col,
        color_continuous_scale="Reds",
        labels={
            temp_col: f"Temperature ({unit_symbol})",
            "city": "City Name",
        },
        template="plotly_white",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.subheader("SQLite Table: `weather_records`")
    st.dataframe(filtered_df, use_container_width=True)

    st.subheader("SQLite Summary Table: `weather_summary`")
    st.dataframe(df_summary, use_container_width=True)