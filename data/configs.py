# USER_RISK_LEVEL = 5

# MY_PORTFOLIO = {
#     'AAPL': [{'quantity': 1, 'transaction_date': '2024-03-05'}],
#     'GME': [{'quantity': 1, 'transaction_date': '2024-05-14'}],
#     'META': [{'quantity': 1, 'transaction_date': '2024-04-26'}],
#     'CMG': [{'quantity': 1, 'transaction_date': '2024-05-20'}],
#     'QQQ': [{'quantity': 1, 'transaction_date': '2024-06-07'}],
#     'UL': [{'quantity': 1, 'transaction_date': '2024-06-06'}],
#     'RDDT': [{'quantity': 1, 'transaction_date': '2024-03-26'}],
#     # 'GOOGL': [{'quantity': 5, 'transaction_date': '2024-06-15'}],
#     'MSFT': [{'quantity': 1, 'transaction_date': '2024-03-12'}],
#     'NVDA': [{'quantity': 3, 'transaction_date': '2024-03-05'}],
#     'GOOG': [{'quantity': 1, 'transaction_date': '2024-05-29'}],
#     'TSLA': [{'quantity': 2, 'transaction_date': '2024-03-05'}],
#     'PANW': [{'quantity': 1, 'transaction_date': '2024-03-06'}],
# }

STOCK_TICKERS_DICT = {
    'ABNB': 'Airbnb Inc',
    'ALB': 'Albermale Corporation',
    'APA': 'APA Corp',
    'BP': 'British Petroleum',
    'EXPE': 'Expedia Group Inc',
    'AXP': 'American Express Company',
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'AMZN': 'Amazon.com Inc.',
    'GOOG': 'Alphabet Inc. (Google Class C Shares)',
    'GOOGL': 'Alphabet Inc. (Google Class A Shares)',
    'META': 'Meta Platforms Inc. (Facebook)',
    'TSLA': 'Tesla Inc.',
    'NVDA': 'NVIDIA Corporation',
    'NFLX': 'Netflix Inc.',
    'PYPL': 'PayPal Holdings Inc.',
    'CRM': 'Salesforce.com Inc.',
    'INTC': 'Intel Corporation',
    'AMD': 'Advanced Micro Devices Inc.',
    'DIS': 'The Walt Disney Company',
    'BABA': 'Alibaba Group Holding Limited',
    'NKE': 'NIKE Inc.',
    'V': 'Visa Inc.',
    'JPM': 'JPMorgan Chase & Co.',
    'COF': 'Capital One Financial Corporation',
    'WMT': 'Walmart Inc.',
    'PG': 'Procter & Gamble Co.',
    'KO': 'The Coca-Cola Company',
    'PEP': 'PepsiCo Inc.',
    'UNH': 'UnitedHealth Group Incorporated',
    'MRK': 'Merck & Co. Inc.',
    'PFE': 'Pfizer Inc.',
    'MRNA': 'Moderna Inc.',
    'CSCO': 'Cisco Systems Inc.',
    'IBM': 'International Business Machines Corporation',
    'XOM': 'Exxon Mobil Corporation',
    'SU':'Suncor Energy Inc', 
    'CVX': 'Chevron Corporation',
    'AAP': 'Advance Auto Parts Inc.',
    'F': 'Ford Motor Company',
    'NFLX': 'Netflix',
    'NYT': 'New York Times Co',
    'PANW': 'Palo Alto Networks',
    'GME': 'Gamestop',
    'UL': 'Unilever',
    'CMG': 'Chipotle',
    'RDDT': 'Reddit Inc',
    'CART': 'Instacart (Maplebear Inc)',
    'UBER': 'Uber Technologies',
    'LYFT': 'LYFT Inc',
    'RIVN': 'Rivian Automative Inc',
    'LCID': 'Lucid Group Inc',
    'BAX': 'Baxter International',
    'CMCSA': 'Comcast',
    'DASH': 'DoorDash Inc',
    'VXX': 'Barclays iPath Series B S&P 500 VIX Short-Term Futures ETN',
    'UVXY': 'ProShares Ultra VIX Short-Term Futures ETF',
    'EL': 'Estee Lauder',
    'CING': 'Cingulate',
    'GOVX': 'GeoVax Labs',
    'APDN': 'Applied DNA Sciences',
    'VRAX': 'Virax Biolabs',
    'ZCAR': 'Zoomcar Holdings, Inc',
    'GTEC': 'Greenland Technologies',
    'SEEL': 'Seelos Therapeutics',
    'ISPO': 'Inspirato',
    'SATL': 'Stallogic',
    'VOR': 'Vor Biopharma',
    'PRTS': 'CarParts.com',
    'ATHA': 'Athira Pharma',
    'KRON': 'Kronos Bio',
    'ZVIA': 'Zevia PBC',
    'CTRM': 'Castor Maritime',
    'PASG': 'Passage Bio',
    'SES': 'SES AI',
    'EGRX': 'Eagle Pharmaceuticals',
    'TCEHY': 'Tencent',
    'ORCL': 'Oracle',
    'HD': 'Home Depot',
    'TMUS': 'T-Mobile',
    'INTU': 'Intuit',
    'OXY': 'Occidental Petroleum',
    'SIRI': 'Sirius XM Holdings Inc',
    'LSXMK': 'Liberty SiriusXM Series C',
    'LSXMA': 'Liberty SiriusXM Series A',
    'LPX': 'Louisiana-Pacific Corp',
    'LLYVK': 'Liberty Media Corp',
    'FND': 'Floor and Decor Holdings',
    'ULTA': 'Ulta Beauty'
}
STOCK_TICKERS_DICT.update({
    'COIN': 'Coinbase Global Inc',
    'PLTR': 'Palantir Technologies',
    'DELL': 'Dell Technologies Inc',
    'BA': 'The Boeing Company',
    'CAT': 'Caterpillar Inc.',
    'GS': 'The Goldman Sachs Group Inc.',
    'HD': 'The Home Depot Inc.',
    'MCD': "McDonald's Corporation",
    'MMM': '3M Company',
    'RTX': 'Raytheon Technologies Corporation',
    'VZ': 'Verizon Communications Inc.',
    'WBA': 'Walgreens Boots Alliance Inc.',
    'WFC': 'Wells Fargo & Company',
    'ADBE': 'Adobe Inc.',
    'ADP': 'Automatic Data Processing Inc.',
    'ALL': 'The Allstate Corporation',
    'AMAT': 'Applied Materials Inc.',
    'ANET': 'Arista Networks Inc.',
    'BKNG': 'Booking Holdings Inc.',
    'BK': 'The Bank of New York Mellon Corporation',
    'BLK': 'BlackRock Inc.',
    'BMY': 'Bristol-Myers Squibb Company',
    'BSX': 'Boston Scientific Corporation',
    'CB': 'Chubb Limited',
    'CI': 'Cigna Corporation',
    'CL': 'Colgate-Palmolive Company',
    'COST': 'Costco Wholesale Corporation',
    'DHR': 'Danaher Corporation',
    'DUK': 'Duke Energy Corporation',
    'EBAY': 'eBay Inc.',
    'EL': 'The Estée Lauder Companies Inc.',
    'GE': 'General Electric Company',
    'GM': 'General Motors Company',
    'GILD': 'Gilead Sciences Inc.',
    'HSY': 'The Hershey Company',
    'HON': 'Honeywell International Inc.',
    'IBM': 'International Business Machines Corporation',
    'ISRG': 'Intuitive Surgical Inc.',
    'JNJ': 'Johnson & Johnson',
    'QQQ': 'Invesco QQQ ETF',
    'V': 'VISA Inc',
    'FMAO': 'Farmers & Merchants Bancorp Inc',
    'NOW': 'ServiceNow',
    'THC': 'Tenet Healthcare',
    'MU': 'Micron Technology',
    'BTI': 'British American Tobacco',
    'CPB': 'Campbell Soup',
    'SHOP': 'Shopify',
    'SQ': 'Block',
    'ETSY': 'Etsy',
    'LUMN': 'Lumen Technologies Inc',
    'WIX': 'Wix.Com Ltd',
    'TRIP': 'Tripadvisor Inc',
    'SPOT': 'Spotify Technology',
    'PGR': 'The Progressive Corporation',
    'TPR': 'Tapestry Inc',
    'BLD': 'TopBuild Corp',
    'C': 'Citigroup Inc',
    'KHC': 'The Kraft Heinz Company',
    'FIS': 'Fidelity National Information Services Inc',
    'SHAK': 'Shake Shack Inc',
    # 'LIN': 'Linde plc',
    # 'LMT': 'Lockheed Martin Corporation',
    # 'LOW': "Lowe's Companies Inc.",
    # 'LRCX': 'Lam Research Corporation',
    # 'MA': 'Mastercard Incorporated',
    # 'MDT': 'Medtronic plc',
    # 'MO': 'Altria Group Inc.',
    # 'MS': 'Morgan Stanley',
    # 'NEE': 'NextEra Energy Inc.',
    # 'NOC': 'Northrop Grumman Corporation',
    # 'ORCL': 'Oracle Corporation',
    # 'PM': 'Philip Morris International Inc.',
    # 'QCOM': 'QUALCOMM Incorporated',
    # 'RTX': 'Raytheon Technologies Corporation',
    # 'SBUX': 'Starbucks Corporation',
    # 'SO': 'The Southern Company',
    # 'SPG': 'Simon Property Group Inc.',
    # 'SRE': 'Sempra Energy',
    # 'T': 'AT&T Inc.',
    # 'TMO': 'Thermo Fisher Scientific Inc.',
    # 'TXN': 'Texas Instruments Incorporated',
    # 'UNP': 'Union Pacific Corporation',
    # 'UPS': 'United Parcel Service Inc.',
    # 'USB': 'U.S. Bancorp',
    # 'VLO': 'Valero Energy Corporation',
    # 'VRTX': 'Vertex Pharmaceuticals Incorporated',
    # 'WM': 'Waste Management Inc.',
    # 'ZTS': 'Zoetis Inc.',
    # 'ABBV': 'AbbVie Inc.',
    # 'AIG': 'American International Group Inc.',
    # 'AON': 'Aon plc',
    # 'APH': 'Amphenol Corporation',
    # 'BBY': 'Best Buy Co. Inc.',
    # 'BIIB': 'Biogen Inc.',
    # 'BK': 'The Bank of New York Mellon Corporation',
    # 'BKR': 'Baker Hughes Company',
    # 'C': 'Citigroup Inc.',
    # 'CDNS': 'Cadence Design Systems Inc.',
    # 'CERN': 'Cerner Corporation',
    # 'CHD': 'Church & Dwight Co. Inc.',
    # 'CMCSA': 'Comcast Corporation',
    # 'COST': 'Costco Wholesale Corporation',
    # 'CSX': 'CSX Corporation',
    # 'CTAS': 'Cintas Corporation',
    # 'CTSH': 'Cognizant Technology Solutions Corporation',
    # 'D': 'Dominion Energy Inc.',
    # 'DHI': 'D.R. Horton Inc.',
    # 'DLR': 'Digital Realty Trust Inc.',
    # 'DTE': 'DTE Energy Company',
    # 'DXCM': 'DexCom Inc.',
    # 'EA': 'Electronic Arts Inc.',
    # 'ECL': 'Ecolab Inc.',
    # 'EFX': 'Equifax Inc.',
    # 'EIX': 'Edison International',
    # 'EMR': 'Emerson Electric Co.',
    # 'EXC': 'Exelon Corporation',
    # 'FISV': 'Fiserv Inc.',
    # 'FLT': 'FleetCor Technologies Inc.',
    # 'FTNT': 'Fortinet Inc.',
    # 'GD': 'General Dynamics Corporation',
    # 'GPN': 'Global Payments Inc.',
    # 'HAS': 'Hasbro Inc.',
    # 'HCA': 'HCA Healthcare Inc.',
    # 'HES': 'Hess Corporation',
    # 'HOLX': 'Hologic Inc.',
    # 'HRL': 'Hormel Foods Corporation',
    # 'HUM': 'Humana Inc.',
    # 'IDXX': 'IDEXX Laboratories Inc.',
    # 'IT': 'Gartner Inc.',
    # 'JCI': 'Johnson Controls International plc',
    # 'K': 'Kellogg Company',
    # 'KEYS': 'Keysight Technologies Inc.',
    # 'KLAC': 'KLA Corporation',
    # 'KMB': 'Kimberly-Clark Corporation',
    # 'KMI': 'Kinder Morgan Inc.',
    # 'LHX': 'L3Harris Technologies Inc.',
    # 'LH': 'Laboratory Corporation of America Holdings',
    # 'MCHP': 'Microchip Technology Incorporated',
    # 'MKC': 'McCormick & Company Incorporated',
    # 'MMC': 'Marsh & McLennan Companies Inc.',
    # 'MNST': 'Monster Beverage Corporation',
    # 'MSCI': 'MSCI Inc.',
    # 'MTB': 'M&T Bank Corporation',
    # 'NEM': 'Newmont Corporation',
    # 'NDAQ': 'Nasdaq Inc.',
    # 'NTRS': 'Northern Trust Corporation',
    # 'OKE': 'ONEOK Inc.',
    # 'OTIS': 'Otis Worldwide Corporation',
    # 'PAYX': 'Paychex Inc.',
    # 'PCAR': 'PACCAR Inc.',
    # 'PLD': 'Prologis Inc.',
    # 'PXD': 'Pioneer Natural Resources Company',
    # 'ROK': 'Rockwell Automation Inc.',
    # 'ROL': 'Rollins Inc.',
    # 'ROST': 'Ross Stores Inc.',
    # 'RSG': 'Republic Services Inc.',
    # 'SBAC': 'SBA Communications Corporation',
    # 'SIVB': 'SVB Financial Group',
    # 'SNPS': 'Synopsys Inc.',
    # 'STT': 'State Street Corporation',
    # 'SWK': 'Stanley Black & Decker Inc.',
    # 'SYK': 'Stryker Corporation',
    # 'SYY': 'Sysco Corporation',
    # 'TDG': 'TransDigm Group Incorporated',
    # 'TRV': 'The Travelers Companies Inc.',
    # 'TSCO': 'Tractor Supply Company',
    # 'TT': 'Trane Technologies plc',
    # 'TYL': 'Tyler Technologies Inc.',
    # 'VRSN': 'VeriSign Inc.',
    # 'WAT': 'Waters Corporation',
    # 'WDC': 'Western Digital Corporation',
    # 'WEC': 'WEC Energy Group Inc.',
    # 'WELL': 'Welltower Inc.',
    # 'WMB': 'The Williams Companies Inc.',
    # 'XYL': 'Xylem Inc.',
    # 'YUM': 'Yum! Brands Inc.',
    # 'ZBH': 'Zimmer Biomet Holdings Inc.',
    # 'ZBRA': 'Zebra Technologies Corporation'
})