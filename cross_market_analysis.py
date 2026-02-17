import streamlit as st

st.title("Cross-Market Analysis: Crypto, Oil & Stocks with SQL")

import pandas as pd
from sqlalchemy import create_engine

st.subheader("Cross-Market Analysis Dashboard")

st.write("Crypto Data Preview")

# Database connection
engine = create_engine(
    "mysql+pymysql://iatXFmXH7cy5Eyv.root:ndGScqvE2B1dpP9p@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/market_analysis",
    connect_args={"ssl": {"ssl": True}}
)

st.set_page_config(page_title="Market Analysis", layout="wide")

page = st.sidebar.radio(
    "Navigation",
    [
        "Filters & Data Exploration",
        "Analysis",
        "Insights"
    ]
)
if page == "Filters & Data Exploration":

    st.title("Filters & Data Exploration")

    st.write("Select Date Range")

    start_date = st.date_input("Start date")
    end_date = st.date_input("End date")

    if st.button("Bitcoin Average Price Analysis"):
        btc_avg = pd.read_sql(
            """
            SELECT AVG(current_price) AS avg_bitcoin
            FROM api_data
            WHERE id = 'bitcoin'
              AND DATE(last_updated) BETWEEN %s AND %s
            """,
            engine,
            params=(start_date, end_date)
        )
        st.write(btc_avg)

    if st.button("Oil Average Price Analysis"):
        oil_avg = pd.read_sql(
            """
            SELECT AVG(price) AS avg_oil_price
            FROM oil_data
            WHERE DATE(date) BETWEEN %s AND %s
            """,
            engine,
            params=(start_date, end_date)
        )
        st.write(oil_avg)

    if st.button("^GSPC Average Price Analysis"):
        sp500_avg = pd.read_sql(
            """
            SELECT AVG(close) AS avg_sp500_price
            FROM stock_data
            WHERE source = '^GSPC'
              AND DATE(date) BETWEEN %s AND %s
            """,
            engine,
            params=(start_date, end_date)
        )
        st.write(sp500_avg)

    if st.button("^NSEI Average Price Analysis"):
        nifty_avg = pd.read_sql(
            """
            SELECT AVG(close) AS avg_nifty_price
            FROM stock_data
            WHERE source = '^NSEI'
              AND DATE(date) BETWEEN %s AND %s
            """,
            engine,
            params=(start_date, end_date)
        )
        st.write(nifty_avg)

    snapshot_df = pd.read_sql(
        """
        SELECT
            DATE(c.last_updated) AS date,
            c.current_price AS bitcoin_price,
            o.price AS oil_price,
            sp.close AS sp500_close,
            ni.close AS nifty_close
        FROM api_data c
        LEFT JOIN oil_data o
            ON DATE(c.last_updated) = o.date
        LEFT JOIN stock_data sp
            ON DATE(c.last_updated) = sp.date
           AND sp.source = '^GSPC'
        LEFT JOIN stock_data ni
            ON DATE(c.last_updated) = ni.date
           AND ni.source = '^NSEI'
        WHERE c.id = 'bitcoin'
        ORDER BY date
        """,
        engine
    )

    st.subheader("Daily market snapshot table")
    st.dataframe(snapshot_df)


elif page == "Analysis":
    st.title("Analysis")
    st.write("Select a predefined SQL query and click **Run Query**")
    query_option = st.selectbox(
        "Choose a query",
        (
            "Bitcoin Average Price",
            "Oil Average Price",
            "S&P 500 Average Closing Price",
            "NIFTY Average Closing Price",
            "Bitcoin vs Oil (Daily)",
            "Bitcoin vs S&P 500 (Daily)",
            "Find the top 3 cryptocurrencies by market cap",
            "Get coins that are within 10 percent of their all-time-high (ATH).",
            "Get the most recently updated coin.",
            "Find the highest daily price of Bitcoin in the last 365 days.",
            "Show oil prices during COVID crash (March-April 2020)."
        )
    )
    if st.button("Run Query"):
        if query_option == "Bitcoin Average Price":
            sql = """
                SELECT AVG(current_price) AS avg_bitcoin_price
                FROM api_data
                WHERE id = 'bitcoin'
            """

        elif query_option == "Oil Average Price":
            sql = """
                SELECT AVG(price) AS avg_oil_price
                FROM oil_data
            """

        elif query_option == "S&P 500 Average Closing Price":
            sql = """
                SELECT AVG(close) AS avg_sp500_price
                FROM stock_data
                WHERE source = '^GSPC'
            """
        elif query_option == "NIFTY Average Closing Price":
            sql = """
                SELECT AVG(close) AS avg_nifty_price
                FROM stock_data
                WHERE source = '^NSEI'
            """

        elif query_option == "Bitcoin vs Oil (Daily)":
            sql = """
                SELECT
                    DATE(c.last_updated) AS date,
                    c.current_price AS bitcoin_price,
                    o.price AS oil_price
                FROM api_data c
                LEFT JOIN oil_data o
                    ON DATE(c.last_updated) = o.date
                WHERE c.id = 'bitcoin'
                ORDER BY date
            """

        elif query_option == "Bitcoin vs S&P 500 (Daily)":
            sql = """
                SELECT
                    DATE(c.last_updated) AS date,
                    c.current_price AS bitcoin_price,
                    s.close AS sp500_close
                FROM api_data c
                LEFT JOIN stock_data s
                    ON DATE(c.last_updated) = s.date
                   AND s.source = '^GSPC'
                WHERE c.id = 'bitcoin'
                ORDER BY date
            """
        elif query_option == "Find the top 3 cryptocurrencies by market cap": 
            sql = "SELECT * FROM api_data order by market_cap desc Limit 5"

        elif query_option == "Get coins that are within 10 percent of their all-time-high (ATH).":
            sql = "select * from api_data where (current_price/ath)*100 > 90 " 

        elif query_option == "Get the most recently updated coin.":
            sql = "select * from api_data order by last_updated desc limit 1"  

        elif query_option == "Find the highest daily price of Bitcoin in the last 365 days.":
            sql = "select max(current_price) as highest_daily_price from api_data where id = 'bitcoin' and last_updated >=now() - interval 365 day "
               
        elif query_option == "Show oil prices during COVID crash (March-April 2020).":
            sql = "select price, date from oil_data where year(date) = 2020 AND month(date) in (3,4)"

        df = pd.read_sql(sql, engine)

        st.subheader("Query Result")
        st.dataframe(df)

elif page == "Insights":
    st.title("Insights")
    st.write("Select a coin and date range to view price trends")

    coin = st.selectbox(
        "Select Coin",
        ("bitcoin", "ethereum", "tether")
    )

    start_date = st.date_input("Start date", key="p3_start")
    end_date = st.date_input("End date", key="p3_end")

    if st.button("View Price Trend"):
        df = pd.read_sql(
            """
            SELECT
                DATE(last_updated) AS date,
                current_price
            FROM api_data
            WHERE id = %s
              AND DATE(last_updated) BETWEEN %s AND %s
            ORDER BY date
            """,
            engine,
            params=(coin, start_date, end_date)
        )

        if df.empty:
            st.warning("No data available for the selected coin and date range.")

        else:

            # --- Table ---
            st.subheader("Daily Price Table")
            st.dataframe(df)    

