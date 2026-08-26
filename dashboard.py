
import streamlit as st
import pandas as pd
import MetaTrader5 as mt5

from app.backtesting.backtest_runner import BacktestRunner
from app.reporting.equity_curve import EquityCurve
from app.strategy.strategy_config import StrategyConfig
from app.reporting.candlestick_chart import CandlestickChart
from app.reporting.trade_table import TradeTable
from app.reporting.database_trade_table import DatabaseTradeTable
from app.database.migrations import migrate
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(
    page_title="TraderVaultAI",
    page_icon="📈",
    layout="wide",
)
migrate()
st.title("📈 TraderVaultAI Dashboard")

# ==========================
# Strategy Settings
# ==========================

st.sidebar.header("Strategy Settings")

symbol = st.sidebar.selectbox(
    "Symbol",
    [
        "XAUUSD",
        "EURUSD",
        "GBPUSD",
        "USDJPY",
    ],
)

timeframe_name = st.sidebar.selectbox(
    "Timeframe",
    [
        "M1",
        "M5",
        "M15",
        "M30",
        "H1",
        "H4",
        "D1",
    ],
)

bars = st.sidebar.slider(
    "Historical Bars",
    min_value=1000,
    max_value=20000,
    value=5000,
    step=1000,
)

risk_percent = st.sidebar.number_input(
    "Risk Per Trade (%)",
    min_value=0.1,
    max_value=10.0,
    value=1.0,
    step=0.1,
)

risk_reward = st.sidebar.slider(
    "Risk Reward Ratio",
    min_value=1,
    max_value=10,
    value=2,
)

max_layers = st.sidebar.slider(
    "Maximum Layers",
    min_value=1,
    max_value=10,
    value=5,
)

break_even = st.sidebar.checkbox(
    "Enable Break Even",
    value=True,
)

layering = st.sidebar.checkbox(
    "Enable Layering",
    value=True,
)

TIMEFRAMES = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}

config = StrategyConfig(
    risk_percent=risk_percent,
    risk_reward=risk_reward,
    max_layers=max_layers,
    break_even=break_even,
    layering=layering,
)

st.write(f"### Current Risk Reward: **{risk_reward}:1**")

# ==========================
# Run Backtest
# ==========================

if st.button("🚀 Run Backtest"):

    runner = BacktestRunner()

    with st.spinner("Running Backtest..."):

        result = runner.run(
            symbol=symbol,
            timeframe=TIMEFRAMES[timeframe_name],
            bars=bars,
            config=config,
        )

    report = result["report"]

    st.success("Backtest Complete")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Trades", report.total_trades)
        st.metric("Wins", report.wins)
        st.metric("Losses", report.losses)

    with col2:
        st.metric("Win Rate", f"{report.win_rate}%")
        st.metric("Profit Factor", report.profit_factor)
        st.metric("Net Profit", report.net_profit)
        st.metric("Average Win", report.average_win)

    with col3:
        st.metric("Gross Profit", report.gross_profit)
        st.metric("Gross Loss", report.gross_loss)
        st.metric("Average Loss", report.average_loss)
        st.metric("Open Trades", result["positions"])

        chart = CandlestickChart()

        candles = runner.loader.load(
            symbol=symbol,
            timeframe=TIMEFRAMES[timeframe_name],
            bars=bars,
        )
        import app.reporting.candlestick_chart as cc

        st.write("Chart file:", cc.__file__)

        price_chart = chart.build(
            candles,
            runner.replay.engine.simulator.trades,
        )

    curve = EquityCurve()

    equity = curve.build(
        runner.replay.engine.simulator.trades
    )

    st.subheader("🕯 Price Chart")

    st.plotly_chart(
        price_chart,
        use_container_width=True,
        config={
            "scrollZoom": True,
            "displaylogo": False,
            "responsive": True,
        },
    )

    # =====================================
    # Trade History
    # =====================================

    trade_table = TradeTable()

    df = trade_table.build(
        runner.replay.engine.simulator.trades
    )

    st.subheader("📋 Trade History")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    # =====================================
    # Equity Curve
    # =====================================

    st.subheader("📈 Equity Curve")

    st.line_chart(equity)

    # =====================================
    # Database Trade Journal
    # =====================================

    st.subheader("📚 Trade Journal")

    db_table = DatabaseTradeTable()
    journal_df = db_table.build()

    if journal_df.empty:

        st.info("No trades saved in the database yet.")

    else:

        gb = GridOptionsBuilder.from_dataframe(journal_df)

        gb.configure_default_column(
            sortable=True,
            filter=True,
            resizable=True,
        )

        result_style = JsCode("""
        function(params){
            if(params.value == 'WIN'){
                return {
                    'color':'lime',
                    'fontWeight':'bold'
                }
            }
            if(params.value == 'LOSS'){
                return {
                    'color':'red',
                    'fontWeight':'bold'
                }
            }
            if(params.value == 'TP1'){
                return {
                    'color':'orange',
                    'fontWeight':'bold'
                }
            }
        };
        """)

        profit_style = JsCode("""
        function(params){
            if(params.value > 0){
                return {
                    'color':'lime',
                    'fontWeight':'bold'
                }
            }
            if(params.value < 0){
                return {
                    'color':'red',
                    'fontWeight':'bold'
                }
            }
        };
        """)

        gb.configure_column(
            "Result",
            cellStyle=result_style,
        )

        gb.configure_column(
            "Profit",
            cellStyle=profit_style,
        )

        AgGrid(
            journal_df,
            gridOptions=gb.build(),
            fit_columns_on_grid_load=True,
            height=400,
            allow_unsafe_jscode=True,
        )