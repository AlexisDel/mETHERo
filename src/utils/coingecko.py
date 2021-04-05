import pycoingecko


def get_crypto_symbols_from_CoinGecko():
    """
    Returns list of CoinGecko listed coins
    """
    symbols = []
    coin_gecko_list = pycoingecko.CoinGeckoAPI().get_coins_list()
    for i in range(len(coin_gecko_list)):
        symbols.append(coin_gecko_list[i]['symbol'].upper())
    return symbols


def get_top_x_crypto(x):
    coin_per_page = 250
    number_of_page_to_load = x // coin_per_page + 1

    coin_gecko_list = []
    for i in range(number_of_page_to_load):
        coin_gecko_list += pycoingecko.CoinGeckoAPI().get_coins_markets(vs_currency="usd", order="market_cap_desc",
                                                                        per_page=coin_per_page, page=i + 1)
    symbols = []
    for i in range(x):
        symbols.append(coin_gecko_list[i]['symbol'].upper())
    return symbols


def filter_by_MC(trends, inout, top):
    if inout is not None and top is not None:
        top_market_cap = get_top_x_crypto(top)
        filtered_trends = []
        if inout == "in":
            for crypto, percent in trends:
                if crypto in top_market_cap:
                    filtered_trends.append((crypto, percent))
        elif inout == "out":
            for crypto, percent in trends:
                if crypto not in top_market_cap:
                    filtered_trends.append((crypto, percent))
        return filtered_trends

    else:
        return trends
