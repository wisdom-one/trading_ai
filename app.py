"""
Application Streamlit principale pour Super Trader AI.

Ce module contient la logique de présentation (UI), gère l'état de session,
les graphiques interactifs en temps réel et les contrôles utilisateur de la barre latérale.
Il délègue toute la logique métier à SystemWrapper (principe de Responsabilité Unique).
"""

import streamlit as st
import time
from datetime import datetime
from typing import Tuple

from config import SETTINGS, TICKER_CATEGORIES, ALL_TICKERS, CUSTOM_CSS, APP_CONFIG
from utils import SystemWrapper
from utils.trading_utils import check_risk_limits


# Initialiser l'état de session globale pour le système de trading
if 'system' not in st.session_state:
    st.session_state.system = SystemWrapper()


def render_custom_css() -> None:
    """Injecte les styles CSS personnalisés pour améliorer l'esthétique du tableau de bord."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_sidebar(system: SystemWrapper) -> Tuple[str, int]:
    """
    Rend la barre latérale contenant toutes les options de configuration de l'application.

    Args:
        system: Instance globale de SystemWrapper.

    Returns:
        Tuple[str, int]: (Mode de durée choisi, Valeur de durée choisie)
    """
    with st.sidebar:
        st.header("⚙️ Configuration Super Trader")

        # Section de gestion du capital
        st.subheader("💰 Gestion du Capital")
        system.trade_amount = float(st.number_input("Mise par trade ($)", 0.01, 1000.0, float(system.trade_amount)))
        system.stop_loss_limit = float(st.number_input("Stop Loss ($)", 0.5, 1000000.0, float(system.stop_loss_limit)))
        system.take_profit_limit = float(st.number_input("Take Profit ($)", 0.5, 1000000.0, float(system.take_profit_limit)))

        # Paramètres d'intelligence artificielle
        st.subheader("🧠 Intelligence Artificielle")
        system.auto_evolve = st.checkbox("Auto-Évolution (Apprentissage continu)", value=system.auto_evolve)

        # Durée de l'automatisme
        st.subheader("⏱️ Durée Automatisme")
        duration_mode = st.selectbox("Mode", ["Indéfini", "Minutes", "Heures", "Jours"])
        duration_val = int(st.number_input("Valeur", 1, 365, 1))

        # Connexion API Polygon.io
        st.markdown("---")
        st.subheader("🔌 Connexion API (Polygon)")

        default_api_key = SETTINGS["load_api_key"]()
        has_default_key = bool(default_api_key)

        if has_default_key and default_api_key != "YOUR_API_KEY_HERE":
            st.success("✅ Clé API chargée depuis .env_data")
            use_env_key = st.checkbox("Utiliser la clé .env_data", value=True)
            api_key_input = default_api_key if use_env_key else st.text_input(
                "Nouvelle clé API", value="", type="password", help="Entrez une nouvelle clé API."
            )
        else:
            api_key_input = st.text_input(
                "Polygon.io API Key", value="", type="password",
                help="Définissez dans .env_data ou collez ici."
            )

        # Sélection du Ticker
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
            ).upper()

            if ticker_input:
                suggestions = [t for t in ALL_TICKERS if ticker_input.upper() in t.upper()][:5]
                if suggestions and ticker_input.upper() not in [t.upper() for t in ALL_TICKERS]:
                    st.caption(f"💡 Suggestions: {', '.join(suggestions)}")
        else:
            ticker_input = st.selectbox("Ticker", options=TICKER_CATEGORIES[ticker_category], index=0)

        # Seuil de rechargement automatique
        system.auto_reload_threshold = int(st.number_input(
            "Seuil auto-reload (données)",
            min_value=5, max_value=100, value=system.auto_reload_threshold,
            help="Recharge automatiquement les données quand il reste moins de X bougies."
        ))

        # Bouton de chargement des données
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


def render_main_dashboard(system: SystemWrapper) -> None:
    """
    Rend le tableau de bord principal avec les indicateurs système et les indicateurs RL.

    Args:
        system: Instance globale de SystemWrapper.
    """
    st.title(f"🚀 {APP_CONFIG['page_title']}")

    # Affichage du statut d'évolution asynchrone s'il est en cours
    if system.agent.is_evolving:
        st.info("🧬 **Évolution de l'IA en cours en arrière-plan...** Le trading se poursuit normalement avec le modèle actuel pendant que le modèle PPO s'entraîne sur le thread secondaire.")

    # Rangée principale de métriques financières
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


def render_control_buttons(system: SystemWrapper) -> None:
    """
    Rend les boutons d'activation et de désactivation de l'agent.

    Args:
        system: Instance globale de SystemWrapper.
    """
    c1, c2 = st.columns(2)
    if c1.button("▶️ DEMARRER SUPER TRADER", type="primary"):
        system.is_running = True
        system.start_time = time.time()
    if c2.button("⏹️ ARRÊTER", type="secondary"):
        system.is_running = False


def render_logs(system: SystemWrapper) -> None:
    """
    Rend le composant de journal des transactions.

    Args:
        system: Instance globale de SystemWrapper.
    """
    with st.container():
        st.subheader("Journal des Opérations")
        for log_entry in system.logs:
            st.text(log_entry)


def main() -> None:
    """Point d'entrée principal de l'application Streamlit."""
    # Configurer la page globale
    st.set_page_config(**APP_CONFIG)

    # Appliquer les styles CSS personnalisés
    render_custom_css()

    # Récupérer l'instance globale du système
    system = st.session_state.system

    # Rendu des composants d'interface principaux
    render_main_dashboard(system)
    duration_mode, duration_val = render_sidebar(system)
    render_control_buttons(system)

    # Zones d'affichage dynamiques réactives
    timer_placeholder = st.empty()
    chart_placeholder = st.empty()
    metrics_placeholder = st.empty()
    analysis_placeholder = st.empty()

    # Rendu initial du graphique
    with chart_placeholder.container():
        if not system.market_history.empty:
            chart_data = system.market_history['close'].astype(float)
            st.line_chart(chart_data)
        else:
            st.info("En attente de données de marché pour générer le graphique...")

    # Boucle d'exécution principale de l'agent de trading
    if system.is_running:
        with st.container():
            st.info("🤖 L'agent scanne le marché en combinant modèles mathématiques et RL...")
            prog = st.progress(0)

            max_loops = 200
            for i in range(max_loops):
                if not system.is_running:
                    break

                # Gestion de la durée de vie programmée du trading
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

                # Gestion du risque (utilisation de trading_utils)
                stop_reached, reason = check_risk_limits(system)
                if stop_reached:
                    system.is_running = False
                    if "Stop Loss" in reason:
                        st.error(reason)
                    else:
                        st.success(reason)
                    break

                # Gestion du rechargement automatique des buffers de données
                if system.should_auto_reload():
                    system.auto_reload_data()

                # Exécution d'un cycle de tick de l'agent
                analysis = system.run_cycle()

                # Affichage de l'analyse technique périodiquement
                if i % 10 == 0 and analysis:
                    with analysis_placeholder:
                        with st.expander("📊 Analyse Technique en Temps Réel", expanded=True):
                            c_rsi, c_macd, c_regime = st.columns(3)
                            c_rsi.metric("RSI", f"{analysis['rsi']:.1f}")
                            c_macd.metric("MACD", f"{analysis['macd']:.4f}")
                            regime_str = "Haussier" if analysis['regime'] == 1 else "Baissier" if analysis['regime'] == -1 else "Neutre"
                            c_regime.metric("Régime", regime_str)

                # Mise à jour graphique à chaque cycle
                with chart_placeholder.container():
                    if not system.market_history.empty:
                        chart_data = system.market_history['close'].astype(float)
                        st.line_chart(chart_data)

                # Mise à jour des indicateurs de statut
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

                time.sleep(0.3)  # Intervalle de rafraîchissement de 300 ms
                prog.progress((i + 1) % 100)

            st.rerun()

    # Rendre les journaux système
    render_logs(system)


if __name__ == "__main__":
    main()

