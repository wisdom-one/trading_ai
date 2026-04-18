import streamlit as st

st.set_page_config(page_title="Informations Marchés", layout="wide")

st.title("📚 Informations sur les Marchés et Tickers")

st.markdown("""
Cette page explique en détail chacun des tickers couverts par l'application Super Trader AI, selon la convention de nommage de Polygon.io.
""")

# Dictionnaire complet de descriptions
ticker_descriptions = {
    # Tech & Communications
    "AAPL": "AAPL : Actions Apple Inc. (Technologie, appareils grand public et services informatiques)",
    "GOOGL": "GOOGL : Actions Alphabet Inc. (Technologie, services internet et moteur de recherche Google)",
    "MSFT": "MSFT : Actions Microsoft Corp. (Technologie, logiciels, matériel et cloud computing)",
    "AMZN": "AMZN : Actions Amazon.com, Inc. (Commerce en ligne, cloud computing AWS)",
    "META": "META : Actions Meta Platforms Inc. (Réseaux sociaux: Facebook, Instagram, WhatsApp)",
    "TSLA": "TSLA : Actions Tesla Inc. (Automobile électrique et énergie propre)",
    "NVDA": "NVDA : Actions NVIDIA Corp. (Fabrication de processeurs graphiques et IA)",
    "AMD": "AMD : Actions Advanced Micro Devices (Conception de microprocesseurs informatiques)",
    "NFLX": "NFLX : Actions Netflix Inc. (Plateforme de streaming vidéo à la demande)",
    "INTC": "INTC : Actions Intel Corporation (Conception et fabrication de puces électroniques)",
    "CSCO": "CSCO : Actions Cisco Systems (Équipementier pour les réseaux, serveurs et télécoms)",
    "CRM": "CRM : Actions Salesforce Inc. (Éditeur de logiciels spécialisés dans le CRM et le cloud)",
    "ORCL": "ORCL : Actions Oracle Corporation (Logiciels de système de gestion de base de données)",
    "IBM": "IBM : Actions International Business Machines (Matériels informatiques, logiciels et cloud)",
    "QCOM": "QCOM : Actions Qualcomm Inc. (Technologie mobile et puces de télécommunication)",
    "TXN": "TXN : Actions Texas Instruments (Semi-conducteurs et conception de puces pour l'électronique)",
    "AVGO": "AVGO : Actions Broadcom Inc. (Conception et développement de composants semi-conducteurs)",
    "ADBE": "ADBE : Actions Adobe Inc. (Logiciels de création informatique)",
    
    # Finance
    "JPM": "JPM : Actions JPMorgan Chase & Co. (Banque, services financiers et d'investissement)",
    "BAC": "BAC : Actions Bank of America Corp (Banque universelle et services financiers mondiaux)",
    "WFC": "WFC : Actions Wells Fargo & Company (Banque de détail et de présence globale)",
    "C": "C : Actions Citigroup Inc. (Institution bancaire multinationale)",
    "GS": "GS : Actions Goldman Sachs (Banque d'investissement, services financiers institutionnels)",
    "MS": "MS : Actions Morgan Stanley (Banque d'investissement et multinationale de la finance)",
    "AXP": "AXP : Actions American Express (Solutions de paiement et cartes bancaires internationales)",
    "V": "V : Actions Visa Inc. (Fournisseur mondial de technologies de paiement électronique)",
    "MA": "MA : Actions Mastercard, Inc. (Systèmes de paiement et cartes de crédit)",
    "PYPL": "PYPL : Actions PayPal Holdings, Inc. (Paiements en ligne sécurisés)",
    
    # Healthcare
    "JNJ": "JNJ : Actions Johnson & Johnson (Fabricant de produits pharmaceutiques et de matériel médical)",
    "PFE": "PFE : Actions Pfizer Inc. (Leader mondial du secteur pharmaceutique et des médicaments)",
    "UNH": "UNH : Actions UnitedHealth Group (Entreprise spécialisée dans la santé et l'assurance maladie)",
    "MRK": "MRK : Actions Merck & Co. (Laboratoire pharmaceutique international)",
    "ABBV": "ABBV : Actions AbbVie Inc. (Laboratoire pharmaceutique, recherche en biologie/immunologie)",
    "LLY": "LLY : Actions Eli Lilly & Co. (Fabricant international de traitements pharmaceutiques)",
    "TMO": "TMO : Actions Thermo Fisher Scientific (Outils d'analyses, recherche scientifique et santé)",
    "MDT": "MDT : Actions Medtronic plc (Matériel et dispositifs médicaux implantables)",
    "DHR": "DHR : Actions Danaher Corp (Recherche médicale, scientifique et environnementale)",
    
    # Consumer
    "WMT": "WMT : Actions Walmart Inc. (Chaîne de grande distribution généraliste géante)",
    "KO": "KO : Actions The Coca-Cola Company (Fabrication de boissons sans alcool, sodas)",
    "PEP": "PEP : Actions PepsiCo Inc. (Boissons gazeuses et industrie agroalimentaire de snacks)",
    "PG": "PG : Actions Procter & Gamble (Biens de consommation courante et produits d'hygiène/beauté)",
    "COST": "COST : Actions Costco Wholesale (Magasins de gros à adhésion)",
    "NKE": "NKE : Actions Nike Inc. (Matériel et équipementier sportif mondial)",
    "MCD": "MCD : Actions McDonald's Corp (Chaîne internationale de restauration rapide)",
    "HD": "HD : Actions The Home Depot (Distribution de biens pour l'aménagement et la rénovation du foyer)",
    "LOW": "LOW : Actions Lowe's Companies (Concurrent de Home Depot, distribution de matériaux)",
    "SBUX": "SBUX : Actions Starbucks Corp (Chaîne internationale de cafés)",
    
    # Energy & Industrials
    "XOM": "XOM : Actions Exxon Mobil Corporation (Multinationale pétrolière et gazière)",
    "CVX": "CVX : Actions Chevron Corporation (Énergie pétrolière, gaz et carburants énergétiques)",
    "BA": "BA : Actions The Boeing Company (Conception aéronautique, défense et aérospatiale)",
    "CAT": "CAT : Actions Caterpillar Inc. (Machines pour la construction lourde et l'exploitation minière)",
    "GE": "GE : Actions General Electric (Conglomérat industriel aéronautique et aérospatial)",
    "MMM": "MMM : Actions 3M Company (Conglomérat de biens d'équipement, adhésifs industriels)",
    "HON": "HON : Actions Honeywell International (Conglomérat industriel dans l'énergie, aéronautique, et bâtiments)",
    "LMT": "LMT : Actions Lockheed Martin (Entreprise de défense et de sécurité et d'armement au monde)",
    "RTX": "RTX : Actions Raytheon Technologies (Défense, systèmes aérospatiaux, renseignement)",
    "UNP": "UNP : Actions Union Pacific Corp (Transport ferroviaire de marchandises en Amérique du Nord)",
    
    # ETFs
    "SPY": "SPY : ETF SPDR S&P 500 (Fonds qui réplique la performance de l'indice américain S&P 500)",
    "QQQ": "QQQ : ETF Invesco QQQ Trust (Fonds qui suit la performance du Nasdaq-100 concentré sur la Tech et l'Innovation)",
    "DIA": "DIA : ETF SPDR Dow Jones Industrial Average (Fonds calqué sur les 30 géants industriels du Dow Jones)",
    "IWM": "IWM : ETF iShares Russell 2000 (Fonds indexé sur 2000 petites capitalisations d'entreprises US)",
    "VTI": "VTI : ETF Vanguard Total Stock Market (Fonds offrant une large exposition globale sur les actions américaines)",
    "VOO": "VOO : ETF Vanguard S&P 500 (Alternative d'ETF ciblant le S&P 500 connu par de très bas frais)",
    "ARKK": "ARKK : ETF ARK Innovation (Fonds technologique actif géré sur entreprises disruptives: IA, robotique)",
    "XLK": "XLK : ETF Technology Select Sector SPDR (Fonds représentant le pôle tech et informatique du sommet de S&P 500)",
    "XLF": "XLF : ETF Financial Select Sector SPDR (Fonds reprenant les services et établissements financiers du S&P 500)",
    "XLV": "XLV : ETF Health Care Select Sect. SPDR (Fonds concentré sur le médical, pharmaceutique et techniciens de la santé au S&P 500)",

    # Forex
    "C:EURUSD": "C:EURUSD : Marché du Forex représentant le taux de change entre l'Euro européen et le Dollar américain.",
    "C:GBPUSD": "C:GBPUSD : Marché du Forex représentant le taux de change entre la Livre Sterling britannique et le Dollar américain.",
    "C:USDJPY": "C:USDJPY : Marché du Forex représentant le taux de change entre le Dollar américain et le Yen japonais.",
    "C:USDCHF": "C:USDCHF : Marché du Forex représentant le taux de change entre le Dollar américain et le Franc suisse.",
    "C:AUDUSD": "C:AUDUSD : Marché du Forex représentant le taux de change entre le Dollar australien et le Dollar américain.",
    "C:USDCAD": "C:USDCAD : Marché du Forex représentant le taux de change entre le Dollar américain et le Dollar canadien.",
    "C:NZDUSD": "C:NZDUSD : Marché du Forex représentant le taux de change entre le Dollar néo-zélandais et le Dollar américain.",
    "C:EURGBP": "C:EURGBP : Marché du Forex croisé (Cross) entre l'Euro européen et la Livre Sterling britannique.",
    "C:EURJPY": "C:EURJPY : Marché du Forex croisé (Cross) entre l'Euro européen et le Yen japonais.",
    "C:EURAUD": "C:EURAUD : Marché du Forex croisé (Cross) entre l'Euro européen et le Dollar australien.",
    "C:EURCAD": "C:EURCAD : Marché du Forex croisé (Cross) entre l'Euro européen et le Dollar canadien.",
    "C:EURCHF": "C:EURCHF : Marché du Forex croisé (Cross) entre l'Euro européen et le Franc suisse.",
    "C:GBPJPY": "C:GBPJPY : Marché du Forex croisé (Cross) entre la Livre Sterling britannique et le Yen japonais.",
    "C:GBPAUD": "C:GBPAUD : Marché du Forex croisé (Cross) entre la Livre Sterling britannique et le Dollar australien.",
    "C:GBPCAD": "C:GBPCAD : Marché du Forex croisé (Cross) entre la Livre Sterling britannique et le Dollar canadien.",
    "C:GBPCHF": "C:GBPCHF : Marché du Forex croisé (Cross) entre la Livre Sterling britannique et le Franc suisse.",
    "C:AUDJPY": "C:AUDJPY : Marché du Forex croisé (Cross) entre le Dollar australien et le Yen japonais.",
    "C:CADJPY": "C:CADJPY : Marché du Forex croisé (Cross) entre le Dollar canadien et le Yen japonais.",
    "C:CHFJPY": "C:CHFJPY : Marché du Forex croisé (Cross) entre le Franc suisse et le Yen japonais.",
    "C:NZDJPY": "C:NZDJPY : Marché du Forex croisé (Cross) entre le Dollar néo-zélandais et le Yen japonais.",

    # Crypto
    "X:BTCUSD": "X:BTCUSD : Marché du Bitcoin adossé au Dollar US.",
    "X:ETHUSD": "X:ETHUSD : Marché de l'Ethereum adossé au Dollar US.",
    "X:SOLUSD": "X:SOLUSD : Marché du Solana (blockchain ultra-rapide) adossé au Dollar US.",
    "X:XRPUSD": "X:XRPUSD : Marché du XRP (protocole Ripple) adossé au Dollar US.",
    "X:ADAUSD": "X:ADAUSD : Marché du Cardano (blockchain éco-responsable et scientifique) adossé au Dollar US.",
    "X:DOGEUSD": "X:DOGEUSD : Marché du Dogecoin (memecoin iconique) adossé au Dollar US.",
    "X:DOTUSD": "X:DOTUSD : Marché du Polkadot (réseau de blockchains interconnectées) adossé au Dollar US.",
    "X:AVAXUSD": "X:AVAXUSD : Marché d'Avalanche (plateforme contrats intelligents) adossé au Dollar US.",
    "X:MATICUSD": "X:MATICUSD : Marché du Polygon (solution de couche 2 d'Ethereum) adossé au Dollar US.",
    "X:LINKUSD": "X:LINKUSD : Marché du Chainlink (oracles blockchain décentralisés) adossé au Dollar US.",
    "X:UNIUSD": "X:UNIUSD : Marché de l'Uniswap (plateforme d'échange décentralisée) adossé au Dollar US.",
    "X:LTCUSD": "X:LTCUSD : Marché du Litecoin (alternative légère au Bitcoin) adossé au Dollar US.",
    "X:BCHUSD": "X:BCHUSD : Marché du Bitcoin Cash (fork axé sur les paiements de détail) adossé au Dollar US.",
    "X:XLMUSD": "X:XLMUSD : Marché du Stellar Lumens (paiements transfrontaliers) adossé au Dollar US.",
    "X:ATOMUSD": "X:ATOMUSD : Marché du Cosmos (réseau d'intéropérabilité des blockchains) adossé au Dollar US.",
    "X:NEARUSD": "X:NEARUSD : Marché du NEAR Protocol (blockchain bas carbone rapide et cloud dev-friendly) adossé au Dollar US.",
    "X:APTUSD": "X:APTUSD : Marché d'Aptos (blockchain L1 de nouvelle génération ultra-rapide) adossé au Dollar US.",
    "X:ALGOUSD": "X:ALGOUSD : Marché de l'Algorand (finance sans friction L1) adossé au Dollar US.",
    "X:AAVEUSD": "X:AAVEUSD : Marché d'Aave (protocole libre DeFi de liquidités) adossé au Dollar US.",
    "X:MKRUSD": "X:MKRUSD : Marché du Maker (protocole Ethereum pour les stablecoins) adossé au Dollar US.",
    "X:SHIBUSD": "X:SHIBUSD : Marché du Shiba Inu (deuxième plus grand memecoin) adossé au Dollar US.",
    "X:TRXUSD": "X:TRXUSD : Marché du TRON (système d'exploitation gratuit d'Internet décentralisé) adossé au Dollar US.",
    "X:FILUSD": "X:FILUSD : Marché de Filecoin (Réseau décentralisé de stockage peer-to-peer) adossé au Dollar US.",
    "X:VETUSD": "X:VETUSD : Marché de VeChain (technologie blockchain de l'IoT et traçabilité pour les entreprises) adossé au Dollar US."
}

st.subheader("Description détaillée des actifs Supportés")

st.markdown("### 📈 Actions d'Entreprises (Stocks) & ETFs")
for k in ticker_descriptions:
    if not (k.startswith("X:") or k.startswith("C:")):
        st.write(f"- **{ticker_descriptions[k]}**")

st.markdown("### 💱 Forex (Marché des devises fiduciaires)")
for k in ticker_descriptions:
    if k.startswith("C:"):
        st.write(f"- **{ticker_descriptions[k]}**")
        
st.markdown("### 🪙 Cryptomonnaies (Blockchain)")
for k in ticker_descriptions:
    if k.startswith("X:"):
        st.write(f"- **{ticker_descriptions[k]}**")

st.divider()

st.subheader("☁️ Hébergement Gratuit Recommandé")
st.info("💡 **Le saviez-vous ?** Étant une application Streamlit, vous n'avez pas besoin de serveurs payants pour la tester en ligne.")

st.markdown("""
Pour héberger cette application :
1. **[Streamlit Community Cloud](https://share.streamlit.io/)** : 🏆 Le choix numéro 1 pour ce projet. Totalement gratuit. 
2. **[Hugging Face Spaces](https://huggingface.co/spaces)** : Excellent si vous voulez héberger vos modèles de RL.
3. **[Render](https://render.com/)** : Hébergement de service web classique avec formule endormie gratuite.
""")
