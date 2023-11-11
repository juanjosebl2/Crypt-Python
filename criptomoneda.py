from binance.client import Client
from datetime import datetime, timedelta
import dateutil.parser as dp
import requests

# Reemplaza con tu propia API key y secret key
api_key = 'bcqgdcTNFFObwMDmJR6qHWwZgmngeZiCcYJgDbGu6VyRJYmGquJTk7iNcjaE4BUi'
api_secret = 'GTeCIIQKW6Cfdmp4dAxX9cTyl6LS8t0K1TZOJiMv3TKnWFAgZ1zh525jnoPscvn5'

client = Client(api_key, api_secret)
#symbol = "CYBERUSDT"
symbol = "MEMETUSD"

def get_historical_prices(symbol, start_date):
    # Convierte la fecha en milisegundos desde la época
    start_epoch_date = int(dp.parse(start_date).timestamp() * 1000)

    # Obtiene los precios históricos de Bitcoin
    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, "2017-01-01")

    historical_prices = {}
    for kline in klines:
        timestamp = kline[0]
        date = datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
        historical_prices[date] = kline[4]  # El precio de cierre está en la quinta posición de la lista

    return historical_prices

def find_last_valid_price(symbol, historical_prices):
    today = datetime.now().date()
    date = today

    last_valid_price = None
    while True:
        formatted_date = date.strftime("%Y-%m-%d")
        price = historical_prices.get(formatted_date)

        if price is not None:
            last_valid_price = f"El precio de cierre de {symbol} el {formatted_date} fue {price}"
        else:
            break

        date -= timedelta(days=1)

    return last_valid_price

start_date = "2017-01-01"
historical_prices = get_historical_prices(symbol, start_date)
result = find_last_valid_price(symbol, historical_prices)
print(result)


def get_all_symbols():
    base_url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(base_url)
    exchange_info = response.json()

    symbols = exchange_info["symbols"]
    return [symbol["symbol"] for symbol in symbols]

#all_symbols = get_all_symbols()

# Contador de símbolos
#symbol_count = len(all_symbols)

#print("Número total de símbolos:", symbol_count)
#print("Lista de símbolos:")
#for symbol in all_symbols:
#    print(symbol)