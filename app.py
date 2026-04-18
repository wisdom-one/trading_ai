"""
Super Trader AI - Streamlit Application
SOLID Principles Applied:
- Single Responsibility: UI logic separated from business logic
- Dependency Inversion: SystemWrapper receives dependencies, not hardcoded
Security:
- API key loaded from .env_data with proper parsing
- No secrets logged to console
"""

import streamlit as st
import time
from datetime import datetime

from config import SETTINGS, TICKER_CATEGORIES, ALL_TICKERS, CUSTOM_CSS, APP_CONFIG
from utils import SystemWrapper

# Initialize session state
if 'system' not in st.session_state:
    st.session_state.system = SystemWrapper()

# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_custom_css():
    """Render custom CSS styles"""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_sidebar(system):
    """Render the sidebar with configuration options"""
    with st.sidebar:
        st.header("⚙️ Super Trader Config")

        # Capital management
        st.subheader("💰 Gestion du Capital")
        system.trade_amount = st.number_input("Mise par trade ($)", 0.01, 1000.0, 1.0)
        system.stop_loss_limit = st.number_input("Stop Loss ($)", 0.5, 1000000.0, 50.0)
        system.take_profit_limit = st.number_input("Take Profit ($)", 0.5, 1000000.0, 100.0)

        # AI Settings
        st.subheader("🧠 Intelligence Artificielle")
        system.auto_evolve = st.checkbox("Auto-Évolution (Apprentissage continu)", value=True)

        # Duration settings
        st.subheader("⏱️ Durée Automatisme")
        duration_mode = st.selectbox("Mode", ["Indéfini", "Minutes", "Heures", "Jours"])
        duration_val = st.number_input("Valeur", 1, 365, 1)

        # API Configuration
        st.markdown("---")
        st.subheader("🔌 Connexion API (Polygon)")

        import os
        default_api_key = SETTINGS["load_api_key"]()
        has_default_key = bool(default_api_key)
        is_system_env = bool(os.getenv("POLYGON_API_KEY"))

        if has_default_key and default_api_key != "YOUR_API_KEY_HERE":
            source_msg = "Environnement Système" if is_system_env else ".env_data"
            st.success(f"✅ Clé API chargée depuis {source_msg}")
            use_env_key = st.checkbox(f"Utiliser la clé {source_msg}", value=True)
            api_key_input = default_api_key if use_env_key else st.text_input(
                "Nouvelle clé API", value="", type="password", help="Entrez une nouvelle clé API."
            )
        else:
            st.info("💡 Conseil: Définissez 'POLYGON_API_KEY' dans vos variables d'environnement pour un déploiement sécurisé.")
            api_key_input = st.text_input(
                "Polygon.io API Key", value="", type="password",
                help="Définissez POLYGON_API_KEY ou collez ici."
            )

        # Ticker selection
        st.markdown("---")
        st.subheader("📊 Sélection du Ticker")

        ticker_category = st.selectbox(
            "Catégorie",
            options=["Stocks", "Forex", "Crypto", "Manuel"],
            index=0
        )

        if ticker_category == "Manuel":
            ticker_input = st.text_input(
                "Ticker (ex: AAPL, X:BTCUSD, C:EURUSD)",
                value="AAPL",
                help="Entrez un ticker manuellement. Préfixes: X: pour crypto, C: pour forex."
            )

            if ticker_input:
                suggestions = [t for t in ALL_TICKERS if ticker_input.upper() in t.upper()][:5]
                if suggestions and ticker_input.upper() not in [t.upper() for t in ALL_TICKERS]:
                    st.caption(f"💡 Suggestions: {', '.join(suggestions)}")
        else:
            ticker_input = st.selectbox("Ticker", options=TICKER_CATEGORIES[ticker_category], index=0)

        # Auto-reload threshold
        system.auto_reload_threshold = st.number_input(
            "Seuil auto-reload (données)",
            min_value=5, max_value=100, value=10,
            help="Recharge automatiquement les données quand il reste moins de X bougies."
        )

        # Load data button
        if st.button("Charger Données"):
            if api_key_input and api_key_input != "YOUR_API_KEY_HERE":
                success, msg = system.load_api_data(api_key_input, ticker_input)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("Clé API manquante. Mode Simulation actif.")

        return duration_mode, duration_val


def render_main_dashboard(system):
    """Render the main dashboard with metrics and charts"""
    st.title(f"🚀 {APP_CONFIG['page_title']}")

    # Metrics row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("PnL Session", f"{system.daily_pnl:.2f} $")
    m2.metric("Gain Max Cumulé", f"{system.max_pnl:.2f} $")
    m3.metric("Bas Cumulé", f"{system.min_pnl:.2f} $")
    m4.metric("État Agent", "Actif" if system.is_running else "Prêt")

    c_s1, c_s2, c_s3 = st.columns(3)
    c_s1.metric("Source", "HISTORIQUE" if system.data_mode == 'HISTORICAL' else "SIMULATION")
    c_s2.metric("Données Analysées", f"{len(system.market_history)} bougies")

    if system.data_mode == 'HISTORICAL':
        stats = system.data_buffer_manager.get_buffer_stats()
        buffer_display = stats['current_buffer_name'] if stats['current_buffer_name'] else "Aucun"
        c_s3.metric("Buffer Actuel", buffer_display)
    else:
        c_s3.metric("Buffers Totaux", "0")


def render_control_buttons(system):
    """Render start/stop control buttons"""
    c1, c2 = st.columns(2)
    if c1.button("▶️ START SUPER TRADER", type="primary"):
        system.is_running = True
        system.start_time = time.time()
    if c2.button("⏹️ STOP", type="secondary"):
        system.is_running = False


def render_logs(system):
    """Render the logs section"""
    with st.container():
        st.subheader("Journal des Opérations")
        for log_entry in system.logs:
            st.text(log_entry)


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application entry point"""
    # Set page configuration
    st.set_page_config(**APP_CONFIG)

    # Apply custom CSS
    render_custom_css()

    # Get system from session state
    system = st.session_state.system

    # Render UI components
    render_main_dashboard(system)
    duration_mode, duration_val = render_sidebar(system)
    render_control_buttons(system)

    # Create placeholders for dynamic content
    timer_placeholder = st.empty()
    chart_placeholder = st.empty()
    metrics_placeholder = st.empty()
    analysis_placeholder = st.empty()

    # Initialize chart
    with chart_placeholder.container():
        if not system.market_history.empty:
            chart_data = system.market_history['close'].astype(float)
            st.line_chart(chart_data)
        else:
            st.info("Attente de données pour afficher le graphique...")

    # Main execution loop
    if system.is_running:
        with st.container():
            st.info("🤖 L'agent scanne le marché avec ses modèles mathématiques et RL...")
            prog = st.progress(0)

            max_loops = 200
            for i in range(max_loops):
                if not system.is_running:
                    break

                # Duration management
                elapsed = time.time() - system.start_time
                limit = 0
                if duration_mode == "Minutes":
                    limit = duration_val * 60
                elif duration_mode == "Heures":
                    limit = duration_val * 3600
                elif duration_mode == "Jours":
                    limit = duration_val * 86400

                if duration_mode != "Indéfini":
                    if elapsed > limit:
                        system.is_running = False
                        st.warning("⏱️ Fin de la durée programmée.")
                        break
                    remaining = limit - elapsed
                    m, s = divmod(remaining, 60)
                    h, m = divmod(m, 60)
                    timer_placeholder.info(f"⏳ Temps restant: {int(h):02d}:{int(m):02d}:{int(s):02d}")
                else:
                    timer_placeholder.info("🚀 L'agent est actif (Durée indéfinie)...")

                # Risk management
                if system.daily_pnl <= -system.stop_loss_limit:
                    system.is_running = False
                    st.error("🛑 Stop Loss touché.")
                    break
                if system.daily_pnl >= system.take_profit_limit:
                    system.is_running = False
                    st.success("🥂 Take Profit touché.")
                    break

                # Gestion Auto-reload des buffers
                if system.should_auto_reload():
                    system.auto_reload_data()

                # Run trading cycle
                analysis = system.run_cycle()

                # Display technical analysis periodically
                if i % 10 == 0 and analysis:
                    with analysis_placeholder:
                        with st.expander("📊 Analyse Technique en Temps Réel", expanded=True):
                            c_rsi, c_macd, c_regime = st.columns(3)
                            c_rsi.metric("RSI", f"{analysis['rsi']:.1f}")
                            c_macd.metric("MACD", f"{analysis['macd']:.4f}")
                            regime_str = "Haussier" if analysis['regime'] == 1 else "Baissier" if analysis['regime'] == -1 else "Neutre"
                            c_regime.metric("Régime", regime_str)

                # Update chart every cycle
                with chart_placeholder.container():
                    if not system.market_history.empty:
                        chart_data = system.market_history['close'].astype(float)
                        st.line_chart(chart_data)

                # Update metrics
                with metrics_placeholder.container():
                    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
                    mc1.metric("PnL Session", f"{system.daily_pnl:.2f} $")
                    mc2.metric("Gain Max Cumulé", f"{system.max_pnl:.2f} $")
                    mc3.metric("Bas Cumulé", f"{system.min_pnl:.2f} $")

                    remaining = system.get_remaining_data_count()
                    mc4.metric("Restantes", f"{remaining} bougies")

                    if system.data_mode == 'HISTORICAL':
                        stats = system.data_buffer_manager.get_buffer_stats()
                        buffer_info = f"{stats['current_buffer_index']+1}/{stats['total_buffers']}"
                        mc5.metric("Buffer", buffer_info)
                    else:
                        mc5.metric("Source", "SIMULATION")

                time.sleep(0.3)  # 300ms update interval
                prog.progress((i + 1) % 100)

            st.rerun()

    # Render logs
    render_logs(system)


if __name__ == "__main__":
    main()
