from binance.client import Client
from datetime import datetime, timedelta
import dateutil.parser as dp
import requests

# Reemplaza con tu propia API key y secret key
api_key = 'bcqgdcTNFFObwMDmJR6qHWwZgmngeZiCcYJgDbGu6VyRJYmGquJTk7iNcjaE4BUi'
api_secret = 'GTeCIIQKW6Cfdmp4dAxX9cTyl6LS8t0K1TZOJiMv3TKnWFAgZ1zh525jnoPscvn5'

client = Client(api_key, api_secret)

def imp_all_symbols(num_symbols=10):
    all_symbols = get_all_symbols()

    # Asegurarse de que num_symbols no exceda la cantidad total de símbolos
    num_symbols = min(num_symbols, len(all_symbols))

    # Obtener los últimos num_symbols símbolos
    last_symbols = all_symbols[-num_symbols:]

    print(f"Número total de símbolos: {len(all_symbols)}")
    print(f"Lista de últimos {num_symbols} símbolos:")
    
    for symbol in last_symbols:
        print(symbol)
        
def get_all_symbols():
    base_url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(base_url)
    exchange_info = response.json()

    symbols = exchange_info["symbols"]
    return [symbol["symbol"] for symbol in symbols]

def get_historical_prices(symbol, start_date):
    start_epoch_date = int(dp.parse(start_date).timestamp() * 1000)
    end_epoch_date = int(datetime.now().timestamp() * 1000)

    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, start_date, end_str=str(end_epoch_date))

    historical_prices = {}
    for kline in klines:
        timestamp = kline[0]
        date = datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
        historical_prices[date] = {
            'open': float(kline[1]),    # Precio de apertura
            'close': float(kline[4]),    # Precio de cierre
            'high': float(kline[2]),    # Precio máximo
            'low': float(kline[3])    # Precio mínimo
        }

    return historical_prices


def find_last_valid_prices(symbol, historical_prices):
    today = datetime.now().date()
    date = today

    last_valid_prices = None
    while True:
        formatted_date = date.strftime("%Y-%m-%d")
        prices = historical_prices.get(formatted_date)

        if prices is not None:
            open_price = prices['open']
            close_price = prices['close']
            high_price = prices['high']
            low_price = prices['low']
            percentage_change = ((close_price - open_price) / open_price) * 100
            percentage_change_hl = ((high_price - low_price) / low_price) * 100

            last_valid_prices = (
                f"El precio de \033[94m{symbol}\033[0m el \033[94m{formatted_date}\033[0m fue:\n"
                f"- \033[92mApertura\033[0m: {open_price}\n"
                f"- \033[91mCierre\033[0m: {close_price}\n"
                f"- \033[92mMáximo\033[0m: {high_price}\n"
                f"- \033[91mMínimo\033[0m: {low_price}\n"
                f"Cambio porcentual: {percentage_change:.2f}%"
            )
            
        else:
            break

        date -= timedelta(days=1)

    return last_valid_prices


def imp_last_valid_prices_and_stats_for_symbols(num_symbols=10):
    all_symbols = get_all_symbols()

    # Asegurarse de que num_symbols no exceda la cantidad total de símbolos
    num_symbols = min(num_symbols, len(all_symbols))

    # Obtener los últimos num_symbols símbolos
    last_symbols = all_symbols[-num_symbols:]

    total_percentage_change = 0
    min_percentage_change = float('inf')  # Inicializar con un valor muy grande
    max_percentage_change = float('-inf')  # Inicializar con un valor muy pequeño

    # Iterar sobre los últimos símbolos y obtener los precios históricos y último precio válido
    for symbol in last_symbols:
        start_date = "2017-01-01"
        historical_prices = get_historical_prices(symbol, start_date)
        result = find_last_valid_prices(symbol, historical_prices)

        try:
            # Intentar obtener el porcentaje de cambio del resultado
            percentage_change_str = result.split("Cambio porcentual: ")[1]
            percentage_change = float(percentage_change_str[:-1])  # Eliminar el '%' al final

            # Actualizar el mínimo y el máximo
            min_percentage_change = min(min_percentage_change, percentage_change)
            max_percentage_change = max(max_percentage_change, percentage_change)

            total_percentage_change += percentage_change
        except AttributeError as e:
            # Manejar la excepción si result es None
            print(f"Error al procesar el símbolo {symbol}: {e}")
            continue

        print(result)
        print('-' * 50)  # Separador para mayor claridad

    # Calcular y mostrar la media, el mínimo y el máximo de los porcentajes de cambio
    if num_symbols > 0:
        average_percentage_change = total_percentage_change / num_symbols
        print(f"\nMedia de cambio porcentual para los últimos {num_symbols} símbolos: {average_percentage_change:.2f}%")
        print(f"Porcentaje mínimo de cambio: {min_percentage_change:.2f}%")
        print(f"Porcentaje máximo de cambio: {max_percentage_change:.2f}%")

def filter_symbols_with_profit(num_symbols=10, porcentaje_minimo=50):
    all_symbols = get_all_symbols()

    # Asegurarse de que num_symbols no exceda la cantidad total de símbolos
    num_symbols = min(num_symbols, len(all_symbols))

    # Obtener los últimos num_symbols símbolos
    last_symbols = all_symbols[-num_symbols:]

    symbols_with_profit = []

    # Iterar sobre los últimos símbolos y obtener los precios históricos y último precio válido
    for symbol in last_symbols:
        start_date = "2017-01-01"
        historical_prices = get_historical_prices(symbol, start_date)
        result = find_last_valid_prices(symbol, historical_prices)

        # Obtener el porcentaje de cambio del resultado
        percentage_change_str = result.split("Cambio porcentual: ")[1]
        percentage_change = float(percentage_change_str[:-1])  # Eliminar el '%' al final

        print('-' * 50)  # Separador para mayor claridad

        # Filtrar los símbolos con más del 50% de beneficio
        if percentage_change > porcentaje_minimo:
            symbols_with_profit.append(symbol)
            print(result)

    return symbols_with_profit

def info_symbol(symbol):

    # Obtener información del libro de órdenes (depth)
    #depth = client.get_order_book(symbol=symbol)
    #print(f"Libro de órdenes para {symbol}: {depth}")

    # Obtener información del ticker
    ticker = client.get_ticker(symbol=symbol)
    print(f"Información del ticker para {symbol}: {ticker}")

#Resultado de una cripto el dia de su lanzamiento en binance apertura, cierre, porcentaje perdida o ganancia  
#symbol = "MEMEUSDT"    
# start_date = "2017-01-01"
# historical_prices = get_historical_prices(symbol, start_date)
# result = find_last_valid_prices(symbol, historical_prices)
# print(result)

#Coge n criptomonedas ultimamente sacadas 
#imp_all_symbols(num_symbols=10)  

#Coge n criptomonedas ultimamente sacadas y realiza un porentaje de perdida o ganancia el primer dia de lanzamiento
# Llama a la función con manejo de excepciones
try:
    imp_last_valid_prices_and_stats_for_symbols(num_symbols=200)
except Exception as e:
    print(f"Error general: {e}")

# Llamada a la función con la cantidad de símbolos que deseas procesar (por ejemplo, 5)
# porcentaje_minimo_requerido=50
# symbols_with_profit = filter_symbols_with_profit(num_symbols=50, porcentaje_minimo=porcentaje_minimo_requerido)
# print("\nSímbolos con más del 50% de beneficio:")
# print(symbols_with_profit)

#informacion de un symbol
#symbol = "MEMEUSDT" 
#info_symbol(symbol)