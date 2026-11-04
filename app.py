import pandas as pd
import streamlit as st
import plotly.express as px
st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("Electronics Store Sales Dashboard - 2019")
def load_and_clean_data():
    data = pd.read_csv("Sales Data.csv")
    original_rows = len(data)
    data = data.drop(columns="Unnamed: 0", errors="ignore")
    data["Order Date"] = pd.to_datetime(
        data["Order Date"], errors="coerce"
    )
    data["Quantity Ordered"] = pd.to_numeric(
        data["Quantity Ordered"], errors="coerce"
    )
    data["Price Each"] = pd.to_numeric(
        data["Price Each"], errors="coerce"
    )
    required_columns = [
        "Order ID",
        "Product",
        "Quantity Ordered",
        "Price Each",
        "Order Date",
        "Purchase Address"
    ]
    before = len(data)
    data = data.dropna(subset=required_columns).copy()
    missing_removed = before - len(data)
    before = len(data)
    data = data.drop_duplicates().copy()
    duplicates_removed = before - len(data)
    before = len(data)
    data = data[data["Order Date"].dt.year == 2019].copy()
    outside_year_removed = before - len(data)
    data["Sales"] = (
        data["Quantity Ordered"] * data["Price Each"]
    )
    data["Month"] = data["Order Date"].dt.month_name()
    data["Hour"] = data["Order Date"].dt.hour
    data["Weekday"] = data["Order Date"].dt.day_name()
    address_parts = data["Purchase Address"].str.split(",")

    data["City"] = (
        address_parts.str[1].str.strip()
        + " ("
        + address_parts.str[2].str.strip().str[:2]
        + ")"
    )
    cleaning_counts = {
        "original_rows": original_rows,
        "missing_removed": missing_removed,
        "duplicates_removed": duplicates_removed,
        "outside_year_removed": outside_year_removed,
        "final_rows": len(data)
    }

    return data, cleaning_counts
df, cleaning_counts = load_and_clean_data()
st.sidebar.header("Filters")
month_list = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]
city_list = sorted(df["City"].unique())
product_list = sorted(df["Product"].unique())

months = st.sidebar.multiselect(
    "Select Month",
    month_list,
    default=month_list
)
cities = st.sidebar.multiselect(
    "Select City",
    city_list,
    default=city_list
)
products = st.sidebar.multiselect(
    "Select Product",
    product_list,
    default=product_list
)

filtered = df[
    df["Month"].isin(months)
    & df["City"].isin(cities)
    & df["Product"].isin(products)
].copy()
if filtered.empty:
    st.warning(
        "No data available for the selected filters. "
        "Please change your selections."
    )
    st.stop()
orders = (
    filtered.groupby("Order ID")["Sales"]
    .sum()
    .reset_index()
)
tab1, tab2 = st.tabs(["Dashboard", "Data Cleaning"])
with tab1:
    st.header("Sales Overview")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Sales",
        f"${filtered['Sales'].sum():,.2f}"
    )

    col2.metric(
        "Number of Orders",
        f"{filtered['Order ID'].nunique():,}"
    )

    col3.metric(
        "Items Sold",
        f"{filtered['Quantity Ordered'].sum():,}"
    )

    col4.metric(
        "Average Order Value",
        f"${orders['Sales'].mean():,.2f}"
    )
    st.header("Univariate Analysis")

    col1, col2 = st.columns(2)
    with col1:
        quantity_data = (
            filtered.groupby("Quantity Ordered")
            .size()
            .reset_index(name="Records")
        )
        fig = px.bar(
            quantity_data,
            x="Quantity Ordered",
            y="Records",
            title="Quantity Ordered Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.write(
            "Observation: Quantity 1 is the most frequently "
            "ordered quantity, while quantity 9 is the least "
            "frequent. This shows that customers generally "
            "purchase smaller quantities of products."
        )
    with col2:

        fig = px.histogram(
            filtered,
            x="Price Each",
            nbins=30,
            title="Price Each Distribution"
        )

        fig.update_xaxes(title="Price Each (USD)")
        fig.update_yaxes(title="Number of Records")

        st.plotly_chart(fig, use_container_width=True)

        st.write(
            "Observation: Product prices are spread across "
            "different ranges, but most are concentrated in "
            "the lower price ranges. The tallest bar appears "
            "between $0 and $100."
        )


    col1, col2 = st.columns(2)
    with col1:

        fig = px.histogram(
            filtered,
            x="Sales",
            nbins=30,
            title="Sales Distribution"
        )

        fig.update_xaxes(title="Sales (USD)")
        fig.update_yaxes(title="Number of Records")

        st.plotly_chart(fig, use_container_width=True)

        st.write(
            "Observation: Most sales transactions have "
            "relatively low sales values, with the highest "
            "frequency occurring between $0 and $200."
        )
    with col2:

        product_data = (
            filtered.groupby("Product")
            .size()
            .reset_index(name="Records")
            .sort_values("Records")
        )

        fig = px.bar(
            product_data,
            x="Records",
            y="Product",
            orientation="h",
            title="Product Purchase Frequency"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.write(
            "Observation: USB-C Charging Cable has the "
            "highest purchase frequency, while LG Dryer has "
            "the lowest. There is a noticeable decrease in "
            "bar heights after Bose SoundSport Headphones."
        )


    col1, col2 = st.columns(2)
    with col1:

        city_data = (
            filtered.groupby("City")
            .size()
            .reset_index(name="Records")
            .sort_values("Records")
        )

        fig = px.bar(
            city_data,
            x="Records",
            y="City",
            orientation="h",
            title="Sales Records by City"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.write(
            "Observation: San Francisco has the highest "
            "number of sales records, while Portland has "
            "the lowest. Differences vary across cities, "
            "with some showing noticeably higher record counts."
        )
    with col2:

        month_data = (
            filtered.groupby("Month")
            .size()
            .reindex(month_list, fill_value=0)
            .rename_axis("Month")
            .reset_index(name="Records")
        )

        fig = px.bar(
            month_data,
            x="Month",
            y="Records",
            title="Sales Records by Month"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.write(
            "Observation: December has the highest number "
            "of sales records, while January has the lowest. "
            "Sales activity generally increases towards "
            "the end of the year."
        )
    hour_data = (
        filtered.groupby("Hour")
        .size()
        .reindex(range(24), fill_value=0)
        .rename_axis("Hour")
        .reset_index(name="Records")
    )

    fig = px.bar(
        hour_data,
        x="Hour",
        y="Records",
        title="Sales Records by Hour"
    )

    fig.update_xaxes(
        title="Hour of the Day",
        dtick=1
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write(
        "Observation: 7 PM (hour 19) has the highest "
        "number of sales records, while 3 AM (hour 3) "
        "has the lowest. Overall, activity is higher "
        "during the afternoon and evening."
    )
    st.header("Bivariate Analysis")
    city_orders = (
        filtered.groupby(["City", "Order ID"])["Sales"]
        .sum()
        .reset_index()
    )
    city_average = (
        city_orders.groupby("City")["Sales"]
        .mean()
        .reset_index()
        .sort_values("Sales")
    )
    fig = px.bar(
        city_average,
        x="Sales",
        y="City",
        orientation="h",
        title="Average Sales per Order by City"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write(
        "Observation: Atlanta has the highest average "
        "sales per order, while Portland has the lowest. "
        "The differences between cities are relatively small."
    )
    product_quantity = (
        filtered.groupby("Product")["Quantity Ordered"]
        .sum()
        .reset_index()
        .sort_values("Quantity Ordered")
    )

    fig = px.bar(
        product_quantity,
        x="Quantity Ordered",
        y="Product",
        orientation="h",
        title="Total Quantity Ordered by Product"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write(
        "Observation: AAA Batteries have the highest "
        "total quantity ordered, while LG Dryer has the "
        "lowest. The difference between products is noticeable."
    )
    sales_heatmap = filtered.pivot_table(
        index="Month",
        columns="Hour",
        values="Sales",
        aggfunc="sum",
        fill_value=0
    )

    sales_heatmap = sales_heatmap.reindex(
        index=month_list,
        columns=range(24),
        fill_value=0
    )

    fig = px.imshow(
        sales_heatmap,
        x=sales_heatmap.columns,
        y=sales_heatmap.index,
        aspect="auto",
        color_continuous_scale="Blues",
        labels={
            "x": "Hour",
            "y": "Month",
            "color": "Sales"
        },
        title="Total Sales by Month and Hour"
    )

    st.plotly_chart(fig, use_container_width=True)

    peak_month, peak_hour = sales_heatmap.stack().idxmax()
    peak_sales = sales_heatmap.loc[peak_month, peak_hour]

    st.write(
        f"Highest sales: {peak_month} at "
        f"{peak_hour}:00 (${peak_sales:,.2f})."
    )

    st.write(
        "Observation: December at 7 PM (hour 19) is "
        "the highest-value month-and-hour combination, "
        "at approximately $322,000. Other combinations "
        "also show strong sales, but are below $300,000."
    )
    price_quantity = (
        filtered.groupby("Product")
        .agg({
            "Price Each": "mean",
            "Quantity Ordered": "sum"
        })
        .reset_index()
    )

    fig = px.scatter(
        price_quantity,
        x="Price Each",
        y="Quantity Ordered",
        hover_name="Product",
        title="Product Price vs Quantity Purchased"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write(
        "Observation: Lower-priced products are generally "
        "purchased in larger quantities, while higher-priced "
        "products tend to be purchased in smaller quantities. "
        "However, the points are scattered, so there is no "
        "strong relationship."
    )

    st.header("Research Questions")
    st.subheader(
        "Question 1: Which day of the week generates "
        "the highest sales?"
    )

    weekday_list = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]

    weekday_sales = (
        filtered.groupby("Weekday")["Sales"]
        .sum()
        .reindex(weekday_list, fill_value=0)
        .rename_axis("Weekday")
        .reset_index()
    )

    fig = px.bar(
        weekday_sales,
        x="Weekday",
        y="Sales",
        title="Total Sales by Day of the Week"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write(
        "Insight: Tuesday generates the highest total "
        "sales, while Thursday records the lowest. The "
        "differences are not very noticeable, suggesting "
        "that sales are fairly consistent across weekdays."
    )
    st.subheader(
        "Question 2: Which products are most frequently "
        "purchased in different cities?"
    )
    city_product = (
        filtered.groupby(["City", "Product"])
        .size()
        .reset_index(name="Records")
    )

    fig = px.bar(
        city_product,
        x="City",
        y="Records",
        color="Product",
        barmode="group",
        title="Product Purchase Frequency by City"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write(
        "Insight: USB-C Charging Cable appears to be "
        "the most frequently purchased product overall. "
        "Product-purchasing patterns are fairly similar "
        "across cities, although San Francisco stands out "
        "for USB-C Charging Cable purchases."
    )
    st.header("Conclusion")

    st.write(
        "1. Smaller quantities are purchased most often, "
        "and lower-priced products are more common in "
        "the dataset."
    )

    st.write(
        "2. USB-C Charging Cable is the most frequently "
        "recorded product, while AAA Batteries have the "
        "highest total quantity ordered."
    )

    st.write(
        "3. San Francisco has the most sales records, "
        "while December has the highest monthly "
        "sales-record count."
    )

    st.write(
        "4. The busiest sales hour is 7 PM, and December "
        "at 7 PM is the strongest month-and-hour "
        "combination in the heatmap."
    )

    st.write(
        "5. Tuesday has the highest total sales by weekday, "
        "but weekday differences are small. Lower-priced "
        "products tend to be purchased in larger quantities, "
        "although the scatter plot does not show a strong "
        "relationship."
    )
with tab2:

    st.header("Data Cleaning Summary")

    cleaning = pd.DataFrame({
        "Cleaning Step": [
            "Original Rows",
            "Missing / Invalid Rows Removed",
            "Duplicate Rows Removed",
            "Rows Outside 2019 Removed",
            "Final Rows"
        ],

        "Number of Rows": [
            cleaning_counts["original_rows"],
            cleaning_counts["missing_removed"],
            cleaning_counts["duplicates_removed"],
            cleaning_counts["outside_year_removed"],
            cleaning_counts["final_rows"]
        ]
    })

    st.table(cleaning)
    st.subheader("Missing Values After Cleaning")
    st.write(df.isnull().sum())

    st.subheader("Order Date Range")

    st.write(
        "Earliest Order:",
        df["Order Date"].min()
    )

    st.write(
        "Latest Order:",
        df["Order Date"].max()
    )
    st.subheader("Outlier Detection")

    col1, col2 = st.columns(2)

    with col1:

        fig = px.box(
            df,
            y="Quantity Ordered",
            title="Quantity Ordered - Box Plot"
        )

        fig.update_yaxes(title="Quantity Ordered")

        st.plotly_chart(fig, use_container_width=True)


    with col2:

        fig = px.box(
            df,
            y="Sales",
            title="Sales - Box Plot"
        )

        fig.update_yaxes(title="Sales (USD)")

        st.plotly_chart(fig, use_container_width=True)


    col1, col2 = st.columns(2)

    with col1:

        fig = px.histogram(
            df,
            x="Quantity Ordered",
            title="Quantity Ordered Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)
    with col2:

        fig = px.histogram(
            df,
            x="Sales",
            nbins=30,
            title="Sales Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)
    st.subheader("Outlier Decision")

    st.write(
        "The box plots show potential outliers in both "
        "Quantity Ordered and Sales. Most customers "
        "purchase smaller quantities, while some "
        "transactions have unusually high sales values. "
        "These outliers are retained because they may "
        "represent genuine customer purchases. Removing "
        "them could result in losing important sales information."
    )
    st.subheader("Cleaned Dataset")
    st.dataframe(df.head(100), use_container_width=True)