import yfinance as yf

def get_company_data(self,symbol):
    company = yf.Ticker(symbol)
    info = company.info
    name = info["longName"]
    values = company.history(period="2y", interval='1h')
    List = []
    for i in values.index:
        List.append((i.to_pydatetime().strftime('%Y-%m-%dT%H:%M:00'),values.at[i,"Open"]))
    return {'symbol':symbol, 'name':name, 'records':List}

