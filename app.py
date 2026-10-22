
from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Afficionado Coffee Roasters",
    page_icon="☕",
    layout="wide"
)


# ============================================================
# 2. LOAD CLEANED DATA AUTOMATICALLY
# ============================================================

DATA_FILE = Path(__file__).parent / "cleaned_coffee_sales.csv"


@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)

    # Ensure numeric columns have correct types
    data["transaction_qty"] = pd.to_numeric(
        data["transaction_qty"], errors="coerce"
    )
    data["unit_price"] = pd.to_numeric(
        data["unit_price"], errors="coerce"
    )

    # Parse transaction time whether saved as HH:MM:SS or another
    # pandas-compatible time representation.
    data["transaction_time"] = pd.to_datetime(
        data["transaction_time"].astype(str),
        format="mixed",
        errors="coerce"
    )

    # Recalculate derived columns for consistency
    data["Revenue"] = data["transaction_qty"] * data["unit_price"]
    data["hour"] = data["transaction_time"].dt.hour

    def get_time_bucket(hour):
        if pd.isna(hour):
            return "Unknown"
        hour = int(hour)

        if 6 <= hour <= 11:
            return "Morning"
        elif 12 <= hour <= 16:
            return "Afternoon"
        elif 17 <= hour <= 21:
            return "Evening"
        return "Late hours"

    data["time_bucket"] = data["hour"].apply(get_time_bucket)

    data = data.dropna(
        subset=[
            "transaction_id",
            "transaction_qty",
            "unit_price",
            "store_location",
            "hour"
        ]
    )

    return data


st.title("☕ Afficionado Coffee Roasters")
st.subheader("Sales Trend and Time-Based Performance Analysis")

st.write(
    "Interactive dashboard for analyzing transaction volume, revenue, "
    "time-of-day demand, and store-level performance."
)

if not DATA_FILE.exists():
    st.error(
        "The cleaned dataset was not found. Please ensure "
        "'cleaned_coffee_sales.csv' is committed to the same "
        "GitHub repository folder as app.py."
    )
    st.stop()

try:
    df = load_data(str(DATA_FILE))
except Exception as error:
    st.error(f"Unable to load the cleaned dataset: {error}")
    st.stop()

if df.empty:
    st.error("The cleaned dataset contains no usable transactions.")
    st.stop()


# ============================================================
# 3. SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Dashboard Filters")

store_options = ["All Stores"] + sorted(
    df["store_location"].dropna().unique().tolist()
)

selected_store = st.sidebar.selectbox(
    "Select Store Location",
    store_options
)

filtered_df = df.copy()

if selected_store != "All Stores":
    filtered_df = filtered_df[
        filtered_df["store_location"] == selected_store
    ]

min_hour = int(filtered_df["hour"].min())
max_hour = int(filtered_df["hour"].max())

hour_range = st.sidebar.slider(
    "Select Hour Range",
    min_value=min_hour,
    max_value=max_hour,
    value=(min_hour, max_hour)
)

filtered_df = filtered_df[
    filtered_df["hour"].between(hour_range[0], hour_range[1])
]

metric = st.sidebar.radio(
    "Select Metric",
    ["Revenue", "Quantity"]
)

if metric == "Revenue":
    y_value = "revenue"
    y_label = "Revenue"
else:
    y_value = "quantity"
    y_label = "Quantity Sold"


# ============================================================
# 4. DATASET LIMITATION
# ============================================================

st.info(
    "Note: The available dataset contains transaction time but does "
    "not contain the actual transaction date. Therefore, genuine "
    "day-of-week and weekday-versus-weekend analysis cannot be "
    "performed reliably."
)


# ============================================================
# 5. OVERALL SALES SUMMARY
# ============================================================

st.header("📊 Overall Sales Summary")

total_transactions = filtered_df["transaction_id"].count()
total_quantity = filtered_df["transaction_qty"].sum()
total_revenue = filtered_df["Revenue"].sum()

col1, col2, col3 = st.columns(3)

col1.metric("Total Transactions", f"{total_transactions:,}")
col2.metric("Total Quantity Sold", f"{total_quantity:,.0f}")
col3.metric("Total Revenue", f"{total_revenue:,.2f}")


# ============================================================
# 6. HOURLY DEMAND ANALYSIS
# ============================================================

st.header("⏰ Hourly Demand Analysis")

hourly_dashboard = (
    filtered_df.groupby("hour")
    .agg(
        transactions=("transaction_id", "count"),
        revenue=("Revenue", "sum"),
        quantity=("transaction_qty", "sum")
    )
    .reset_index()
)

if not hourly_dashboard.empty:
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        hourly_dashboard["hour"],
        hourly_dashboard[y_value],
        marker="o"
    )

    ax.set_xlabel("Hour")
    ax.set_ylabel(y_label)
    ax.set_title(f"Hourly {y_label}")
    ax.set_xticks(sorted(hourly_dashboard["hour"].unique()))
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# ============================================================
# 7. TIME-OF-DAY PERFORMANCE
# ============================================================

st.header("🕐 Time-of-Day Performance")

bucket_order = ["Morning", "Afternoon", "Evening", "Late hours"]

time_dashboard = (
    filtered_df.groupby("time_bucket")
    .agg(
        transactions=("transaction_id", "count"),
        revenue=("Revenue", "sum"),
        quantity=("transaction_qty", "sum")
    )
    .reindex(bucket_order)
    .dropna(how="all")
    .reset_index()
)

if not time_dashboard.empty:
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(
        time_dashboard["time_bucket"],
        time_dashboard[y_value]
    )

    ax.set_xlabel("Time of Day")
    ax.set_ylabel(y_label)
    ax.set_title(f"{y_label} by Time of Day")

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# ============================================================
# 8. HOURLY DEMAND HEATMAP
# ============================================================

st.header("🔥 Hourly Demand Heatmap")

store_hour_dashboard = (
    filtered_df.groupby(["store_location", "hour"])
    .agg(transactions=("transaction_id", "count"))
    .reset_index()
)

if not store_hour_dashboard.empty:
    heatmap_data = store_hour_dashboard.pivot(
        index="store_location",
        columns="hour",
        values="transactions"
    ).fillna(0)

    fig, ax = plt.subplots(figsize=(12, 6))

    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".0f",
        cmap="YlOrBr",
        ax=ax
    )

    ax.set_xlabel("Hour")
    ax.set_ylabel("Store Location")
    ax.set_title("Hourly Transactions by Store")

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# ============================================================
# 9. STORE LOCATION COMPARISON
# ============================================================

st.header("🏪 Store Location Comparison")

location_comparison = (
    filtered_df.groupby("store_location")
    .agg(
        transactions=("transaction_id", "count"),
        quantity=("transaction_qty", "sum"),
        revenue=("Revenue", "sum")
    )
    .reset_index()
)

st.dataframe(location_comparison, use_container_width=True)


# ============================================================
# 10. STORE COMPARISON CHART
# ============================================================

if not location_comparison.empty:
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(
        location_comparison["store_location"],
        location_comparison[y_value]
    )

    ax.set_xlabel("Store Location")
    ax.set_ylabel(y_label)
    ax.set_title(f"{y_label} by Store Location")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# ============================================================
# 11. PEAK HOUR
# ============================================================

st.header("⭐ Peak Hour")

if not hourly_dashboard.empty:
    peak_row = hourly_dashboard.loc[
        hourly_dashboard[y_value].idxmax()
    ]

    st.success(
        f"Peak {y_label.lower()} occurs at "
        f"{int(peak_row['hour'])}:00"
    )

    st.write(f"{y_label}: {peak_row[y_value]:,.2f}")


# ============================================================
# 12. DATASET PREVIEW
# ============================================================

st.header("📋 Dataset Preview")

st.dataframe(
    filtered_df.head(20),
    use_container_width=True
)

st.caption(
    f"Showing up to 20 rows from {len(filtered_df):,} filtered transactions."
)
