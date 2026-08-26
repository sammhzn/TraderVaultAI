import MetaTrader5 as mt5

print("Initializing MT5...")

if not mt5.initialize():
    print("❌ Initialization failed")
    print("Error:", mt5.last_error())
    quit()

print("✅ MT5 Connected!")

account = mt5.account_info()

if account:
    print("Account:", account.login)
    print("Server :", account.server)
else:
    print("⚠ No account information found.")

symbol = "XAUUSD"

if not mt5.symbol_select(symbol, True):
    print(f"❌ Cannot find symbol: {symbol}")
else:
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 5)

    if rates is None:
        print("❌ No historical data returned.")
    else:
        print(f"✅ Loaded {len(rates)} candles")
        print(rates[0])

mt5.shutdown()