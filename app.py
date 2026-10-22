
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
# 2. TITLE
# ============================================================

st.title("☕ Afficionado Coffee Roasters")

st.subheader(
    "Sales Trend and Time-Based Performance Analysis"
)

st.write(
    "Interactive dashboard for analyzing transaction volume, "
    "revenue, time-of-day demand, and store-level performance."
)


# ============================================================
# 3. UPLOAD DATASET
# ============================================================

uploaded_file = st.file_uploader(
    "Upload Coffee Sales CSV Dataset",
    type=["csv"]
)


# ============================================================
# 4. RUN DASHBOARD AFTER FILE UPLOAD
# ============================================================

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)


    # ========================================================
    # 5. DATA PREPARATION
    # ========================================================

    df["transaction_time"] = pd.to_datetime(
        df["transaction_time"],
        format="%H:%M:%S"
    )

    # Revenue
    df["Revenue"] = (
        df["transaction_qty"] *
        df["unit_price"]
    )

    # Hour
    df["hour"] = df["transaction_time"].dt.hour


    # Time buckets
    def time_bucket(hour):

        if 6 <= hour <= 11:
            return "Morning"

        elif 12 <= hour <= 16:
            return "Afternoon"

        elif 17 <= hour <= 21:
            return "Evening"

        else:
            return "Late hours"


    df["time_bucket"] = df["hour"].apply(time_bucket)


    # ========================================================
    # 6. SIDEBAR FILTERS
    # ========================================================

    st.sidebar.header("Dashboard Filters")


    # Store Location
    store_options = [
        "All Stores"
    ] + sorted(
        df["store_location"].dropna().unique().tolist()
    )


    selected_store = st.sidebar.selectbox(
        "Select Store Location",
        store_options
    )


    # Copy dataframe
    filtered_df = df.copy()


    # Apply store filter
    if selected_store != "All Stores":

        filtered_df = filtered_df[
            filtered_df["store_location"] == selected_store
        ]


    # ========================================================
    # 7. HOUR RANGE FILTER
    # ========================================================

    min_hour = int(filtered_df["hour"].min())
    max_hour = int(filtered_df["hour"].max())


    hour_range = st.sidebar.slider(
        "Select Hour Range",
        min_value=min_hour,
        max_value=max_hour,
        value=(min_hour, max_hour)
    )


    # Apply hour filter
    filtered_df = filtered_df[
        (filtered_df["hour"] >= hour_range[0]) &
        (filtered_df["hour"] <= hour_range[1])
    ]


    # ========================================================
    # 8. REVENUE / QUANTITY TOGGLE
    # ========================================================

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


    # ========================================================
    # 9. DATASET LIMITATION
    # ========================================================

    st.info(
        "Note: The available dataset contains transaction time "
        "but does not contain the actual transaction date. "
        "Therefore, day-of-week and weekday-versus-weekend "
        "analysis cannot be performed reliably."
    )


    # ========================================================
    # 10. OVERALL SALES SUMMARY
    # ========================================================

    st.header("📊 Overall Sales Summary")


    total_transactions = (
        filtered_df["transaction_id"].count()
    )

    total_quantity = (
        filtered_df["transaction_qty"].sum()
    )

    total_revenue = (
        filtered_df["Revenue"].sum()
    )


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "Total Transactions",
        f"{total_transactions:,}"
    )


    col2.metric(
        "Total Quantity Sold",
        f"{total_quantity:,}"
    )


    col3.metric(
        "Total Revenue",
        f"{total_revenue:,.2f}"
    )


    # ========================================================
    # 11. HOURLY DEMAND ANALYSIS
    # ========================================================

    st.header("⏰ Hourly Demand Analysis")


    hourly_dashboard = filtered_df.groupby(
        "hour"
    ).agg(
        transactions=("transaction_id", "count"),
        revenue=("Revenue", "sum"),
        quantity=("transaction_qty", "sum")
    ).reset_index()


    if not hourly_dashboard.empty:

        fig, ax = plt.subplots(
            figsize=(10, 5)
        )


        ax.plot(
            hourly_dashboard["hour"],
            hourly_dashboard[y_value],
            marker="o"
        )


        ax.set_xlabel("Hour")

        ax.set_ylabel(y_label)

        ax.set_title(
            f"Hourly {y_label}"
        )

        ax.grid()


        st.pyplot(
            fig,
            width="stretch"
        )


    # ========================================================
    # 12. TIME-OF-DAY PERFORMANCE
    # ========================================================

    st.header("🕐 Time-of-Day Performance")


    time_dashboard = filtered_df.groupby(
        "time_bucket"
    ).agg(
        transactions=("transaction_id", "count"),
        revenue=("Revenue", "sum"),
        quantity=("transaction_qty", "sum")
    ).reset_index()


    fig, ax = plt.subplots(
        figsize=(8, 5)
    )


    ax.bar(
        time_dashboard["time_bucket"],
        time_dashboard[y_value]
    )


    ax.set_xlabel("Time of Day")

    ax.set_ylabel(y_label)

    ax.set_title(
        f"{y_label} by Time of Day"
    )


    st.pyplot(
        fig,
        width="stretch"
    )


    # ========================================================
    # 13. HOURLY DEMAND HEATMAP
    # ========================================================

    st.header("🔥 Hourly Demand Heatmap")


    store_hour_dashboard = filtered_df.groupby(
        ["store_location", "hour"]
    ).agg(
        transactions=("transaction_id", "count")
    ).reset_index()


    heatmap_data = store_hour_dashboard.pivot(
        index="store_location",
        columns="hour",
        values="transactions"
    )


    fig, ax = plt.subplots(
        figsize=(12, 6)
    )


    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".0f",
        ax=ax
    )


    ax.set_xlabel("Hour")

    ax.set_ylabel("Store Location")

    ax.set_title(
        "Hourly Transactions by Store"
    )


    st.pyplot(
        fig,
        width="stretch"
    )


    # ========================================================
    # 14. STORE LOCATION COMPARISON
    # ========================================================

    st.header("🏪 Store Location Comparison")


    location_comparison = filtered_df.groupby(
        "store_location"
    ).agg(
        transactions=("transaction_id", "count"),
        quantity=("transaction_qty", "sum"),
        revenue=("Revenue", "sum")
    ).reset_index()


    st.dataframe(
        location_comparison,
        width="stretch"
    )


    # ========================================================
    # 15. STORE COMPARISON CHART
    # ========================================================

    fig, ax = plt.subplots(
        figsize=(10, 5)
    )


    ax.bar(
        location_comparison["store_location"],
        location_comparison[y_value]
    )


    ax.set_xlabel("Store Location")

    ax.set_ylabel(y_label)

    ax.set_title(
        f"{y_label} by Store Location"
    )


    plt.xticks(
        rotation=20
    )


    st.pyplot(
        fig,
        width="stretch"
    )


    # ========================================================
    # 16. PEAK HOUR
    # ========================================================

    st.header("⭐ Peak Hour")


    if not hourly_dashboard.empty:

        peak_row = hourly_dashboard.loc[
            hourly_dashboard[y_value].idxmax()
        ]


        st.success(
            f"Peak {y_label.lower()} occurs at "
            f"{int(peak_row['hour'])}:00"
        )


        st.write(
            f"{y_label}: "
            f"{peak_row[y_value]:,.2f}"
        )


    # ========================================================
    # 17. DATASET PREVIEW
    # ========================================================

    st.header("📋 Dataset Preview")


    st.dataframe(
        filtered_df.head(20),
        width="stretch"
    )


else:

    st.warning(
        "Please upload the Coffee Sales CSV dataset "
        "to start the dashboard."
    )
