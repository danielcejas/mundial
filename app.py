import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go

st.set_page_config(
    page_title="Mundial 2026 · Predicciones",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Flag image helpers ───────────────────────────────────────────────────────
ISO = {
    "Spain": "es", "England": "gb-eng", "France": "fr", "Argentina": "ar",
    "Morocco": "ma", "Portugal": "pt", "Colombia": "co", "Japan": "jp",
    "Germany": "de", "Brazil": "br", "Iran": "ir", "Senegal": "sn",
    "Netherlands": "nl", "Norway": "no", "Croatia": "hr", "Turkey": "tr",
    "Switzerland": "ch", "Algeria": "dz", "Australia": "au", "Uzbekistan": "uz",
    "Uruguay": "uy", "Ivory Coast": "ci", "Egypt": "eg", "Canada": "ca",
    "Ecuador": "ec", "South Korea": "kr", "Panama": "pa", "Austria": "at",
    "Belgium": "be", "United States": "us", "Mexico": "mx", "Jordan": "jo",
    "New Zealand": "nz", "DR Congo": "cd", "Tunisia": "tn", "Iraq": "iq",
    "Sweden": "se", "Scotland": "gb-sct", "Ghana": "gh", "Paraguay": "py",
    "Cape Verde": "cv", "Saudi Arabia": "sa", "Haiti": "ht",
    "Czech Republic": "cz", "South Africa": "za", "Qatar": "qa",
    "Curaçao": "cw", "Bosnia and Herzegovina": "ba",
}

ROUNDS = {
    "round_32":       "Dieciseisavos",
    "round_16":       "Octavos de Final",
    "quarter_finals": "Cuartos de Final",
    "semi_finals":    "Semifinales",
    "final":          "Gran Final",
}


def flag_img(team: str, h: int = 20) -> str:
    code = ISO.get(team)
    if not code:
        return "⚽"
    return (
        f'<img src="https://flagcdn.com/w40/{code}.png" '
        f'style="height:{h}px; width:auto; vertical-align:middle; '
        f'border-radius:3px; box-shadow:0 1px 3px rgba(0,0,0,.4);" '
        f'onerror="this.style.display=\'none\'">'
    )


def winner_of(m: dict):
    if m["best_1X2"] == "home_win":
        return m["home"]
    if m["best_1X2"] == "away_win":
        return m["away"]
    return None


@st.cache_data
def load_data():
    mc = pd.read_csv("data/processed/mc_results.csv")
    surv = pd.read_csv("data/processed/survival_probabilities.csv")
    mc = mc.sort_values("probability", ascending=False).reset_index(drop=True)
    with open("data/processed/bracket_2026.json", "r", encoding="utf-8") as f:
        bracket = json.load(f)
    return mc, surv, bracket


mc, surv, bracket = load_data()

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Background — dark navy, not pure black */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #111827 !important;
}
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stSidebar"] { background: #1f2937 !important; }

/* Tabs */
[data-testid="stTabs"] button          { font-weight:600; color:#9ca3af !important; }
[data-testid="stTabs"] button[aria-selected="true"] {
    color:#f59e0b !important;
    border-bottom-color:#f59e0b !important;
}

/* Selectbox / radio labels */
label, .stRadio label { color:#d1d5db !important; }
            /* Encabezados legibles sobre fondo oscuro */
h1, h2, h3, h4, h5, h6 { color:#f1f5f9 !important; }

/* Opciones del radio horizontal (rondas en Tab 4) */
div[role="radiogroup"] label p {
    color:#e2e8f0 !important;
    font-weight:600 !important;
}

/* ▲▲▲ HASTA AQUÍ ▲▲▲ */

/* --- Reusable card --- */

/* --- Reusable card --- */
.card {
    background: #1f2937;
    border: 1px solid #374151;
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 0.7rem;
    transition: border-color .2s;
}
.card:hover { border-color: #6b7280; }

/* --- Podium card --- */
.podium-card {
    background: #1f2937;
    border-radius: 18px;
    padding: 1.7rem 1rem;
    text-align: center;
    height: 100%;
}

/* --- Knockout card --- */
.ko-card {
    background: #1f2937;
    border: 1px solid #374151;
    border-left: 4px solid #f59e0b;
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.55rem;
    transition: border-color .2s;
}
.ko-card:hover { border-color: #f59e0b88; }

/* --- Standings --- */
.standings-wrap {
    border: 1px solid #374151;
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 1rem;
}
.standings-head {
    background: #253044;
    display: grid;
    grid-template-columns: 2rem 1fr 3rem 3rem 3rem 3rem 3.5rem;
    padding: 0.65rem 1rem;
    gap: 0.3rem;
    color: #f59e0b;
    font-size: 0.73rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .07em;
}
.standings-row {
    background: #1f2937;
    display: grid;
    grid-template-columns: 2rem 1fr 3rem 3rem 3rem 3rem 3.5rem;
    align-items: center;
    padding: 0.7rem 1rem;
    gap: 0.3rem;
    border-top: 1px solid #374151;
    font-size: 0.9rem;
    color: #f1f5f9;
    transition: background .15s;
}
.standings-row:hover { background: #253044; }
.standings-foot {
    background: #172033;
    padding: .45rem 1rem;
    font-size: .72rem;
    color: #9ca3af;
    display: flex;
    gap: 1.2rem;
    border-top: 1px solid #374151;
}

/* --- Badges --- */
.score-badge {
    background: #f59e0b;
    color: #111827;
    font-weight: 800;
    padding: .22rem .9rem;
    border-radius: 20px;
    font-size: 1rem;
    white-space: nowrap;
}
.advances-badge {
    background: rgba(52,211,153,.12);
    color: #6ee7b7;
    border: 1px solid rgba(52,211,153,.3);
    padding: .15rem .55rem;
    border-radius: 12px;
    font-size: .78rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: .35rem;
}
</style>
""", unsafe_allow_html=True)

# ── Page header ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #172033 0%, #1e3a5f 50%, #172033 100%);
    border-bottom: 3px solid #f59e0b;
    padding: 2.4rem 1rem 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
    border-radius: 14px;
">
  <div style="font-size:3rem; line-height:1;">🏆</div>
  <h1 style="
      color:#f59e0b; font-size:2.4rem; font-weight:800;
      margin:.3rem 0 0; letter-spacing:-.5px; color:#f59e0b;
  ">Mundial 2026</h1>
  <p style="
      color:#94a3b8; font-size:.85rem; margin:.4rem 0 0;
      letter-spacing:.18em; text-transform:uppercase;
  ">Dashboard Predictivo · Simulación Monte Carlo</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(
    ["🏅  Favoritos", "⚽  Fase de Grupos", "📊  Clasificación", "🏆  Eliminatorias"]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 · Favoritos
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    SURV_ROUNDS = ["Dieciseisavos", "Octavos", "Cuartos", "Semis", "Final", "Campeón"]

    # ── PODIO: top 3 por probabilidad de campeón ──────────────────────────────
    top3 = surv.sort_values("Campeón", ascending=False).head(3)
    medals  = ["🥇", "🥈", "🥉"]
    borders = ["#f59e0b", "#cbd5e1", "#b45309"]

    col1, col2, col3 = st.columns(3)
    for col, (_, row), medal, border in zip([col1, col2, col3], top3.iterrows(), medals, borders):
        with col:
            st.markdown(f"""
            <div class="podium-card" style="border:2px solid {border};">
              <div style="font-size:1.8rem;">{medal}</div>
              <div style="margin:.6rem 0 .4rem;">{flag_img(row['Team'], h=52)}</div>
              <div style="color:#f1f5f9; font-weight:700; font-size:1.05rem;">{row['Team']}</div>
              <div style="color:{border}; font-size:2rem; font-weight:800; margin-top:.5rem;">
                {row['Campeón']*100:.1f}%
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h4 style="color:#f1f5f9; font-weight:700; margin:1rem 0 .6rem;">Recorrido de cada selección</h4>', unsafe_allow_html=True)
    # ── SELECTOR DE PAÍS ──────────────────────────────────────────────────────
    teams_sorted = surv.sort_values("Campeón", ascending=False)["Team"].tolist()
    sel_team = st.selectbox(
        "Selecciona una selección",
        teams_sorted,
        format_func=lambda t: f"{t}",
    )

    row = surv[surv["Team"] == sel_team].iloc[0]

    # ── Cabecera: bandera + nombre + posición en el ranking ───────────────────
    rank_pos = teams_sorted.index(sel_team) + 1
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:1rem; margin:1rem 0;
                background:linear-gradient(135deg,#1a2340,#0f1829);
                border:1px solid #2a3d6e; border-radius:14px; padding:1rem 1.4rem;">
        <div>{flag_img(sel_team, h=56)}</div>
        <div>
            <div style="color:#f1f5f9; font-size:1.6rem; font-weight:800;">{sel_team}</div>
            <div style="color:#9fb3d9; font-size:.9rem;">#{rank_pos} favorito al título</div>
        </div>
        <div style="margin-left:auto; text-align:right;">
            <div style="color:#f59e0b; font-size:2rem; font-weight:800;">{row['Campeón']*100:.1f}%</div>
            <div style="color:#9fb3d9; font-size:.8rem;">probabilidad de ganar</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Probabilidad de SUPERAR cada ronda (barras horizontales) ──────────────
    # ── Probabilidad de alcanzar cada ronda (directo del CSV) ─────────────────
    # ── Probabilidad de alcanzar cada ronda (directo del CSV) ─────────────────
    st.markdown('<h5 style="color:#e2e8f0; font-weight:700; margin:1rem 0 .6rem;">Probabilidad de alcanzar cada ronda</h5>', unsafe_allow_html=True)


    max_pct = row[SURV_ROUNDS[0]] * 100  # dieciseisavos marca la escala
    for rnd in SURV_ROUNDS:
        pct = row[rnd] * 100
        bar = int(pct / max_pct * 100)
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:14px; margin-bottom:12px;">
            <div style="width:130px; color:#cdd6f4; font-size:15px; font-weight:600;">{rnd}</div>
            <div style="flex:1; background:#1f2937; border-radius:10px; height:26px; position:relative;">
                <div style="background:linear-gradient(90deg,#059669,#34d399);
                            height:26px; width:{bar}%; border-radius:10px;
                            display:flex; align-items:center; justify-content:flex-end;
                            padding-right:10px; min-width:48px;
                            box-shadow:0 0 8px rgba(52,211,153,.25);">
                    <span style="color:#06281d; font-weight:800; font-size:14px;">{pct:.1f}%</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 · Partidos de Grupo
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    groups = list(bracket["group_stage"].keys())
    g = st.selectbox(
        "Selecciona grupo:",
        groups,
        format_func=lambda x: f"Grupo  {x}",
        key="g_matches",
    )
    matches = bracket["group_stage"][g]["matches"]
    st.markdown(f"#### Grupo {g} · {len(matches)} partidos")

    for m in matches:
        w = winner_of(m)
        ph  = m["probs_1X2"]["home_win"] * 100
        pd_ = m["probs_1X2"]["draw"]     * 100
        pa  = m["probs_1X2"]["away_win"] * 100

        home_s = "font-weight:800; color:#f1f5f9;" if w == m["home"] else "color:#9ca3af;"
        away_s = "font-weight:800; color:#f1f5f9;" if w == m["away"] else "color:#9ca3af;"

        winner_html = (
            f"<span style='color:#34d399; font-size:.8rem; display:flex; align-items:center; gap:.3rem;'>"
            f"✓ {flag_img(w, h=16)} {w}</span>"
            if w else
            "<span style='color:#9ca3af; font-size:.8rem;'>Empate</span>"
        )

        total = ph + pd_ + pa or 100
        ph_w = int(ph / total * 100)
        pd_w = int(pd_ / total * 100)
        pa_w = 100 - ph_w - pd_w

        st.markdown(f"""
        <div class="card">
          <div style="display:flex; align-items:center; gap:.75rem; flex-wrap:wrap;">
            <div style="flex:1; text-align:right; {home_s} font-size:.95rem;
                        display:flex; align-items:center; justify-content:flex-end; gap:.5rem;">
              {m['home']} {flag_img(m['home'], h=24)}
            </div>
            <span class="score-badge">{m['score']}</span>
            <div style="flex:1; text-align:left; {away_s} font-size:.95rem;
                        display:flex; align-items:center; gap:.5rem;">
              {flag_img(m['away'], h=24)} {m['away']}
            </div>
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center;
                      margin-top:.65rem; flex-wrap:wrap; gap:.5rem;">
            <div style="background:#374151; border-radius:6px; height:5px;
                        display:flex; overflow:hidden; flex:1; min-width:120px;">
              <div style="width:{ph_w}%; background:#34d399;"></div>
              <div style="width:{pd_w}%; background:#9ca3af;"></div>
              <div style="width:{pa_w}%; background:#f87171;"></div>
            </div>
            <span style="font-size:.75rem; color:#6b7280; white-space:nowrap;">
              {ph:.0f}% · {pd_:.0f}% · {pa:.0f}%
            </span>
            {winner_html}
          </div>
        </div>
        """, unsafe_allow_html=True)



# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 · Clasificación de Grupos
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    groups = list(bracket["group_stage"].keys())
    g = st.selectbox(
        "Selecciona grupo:",
        groups,
        format_func=lambda x: f"Grupo  {x}",
        key="g_table",
    )
    st.markdown(f"#### Grupo {g}")

    standings = bracket["group_stage"][g]["standings"]
    n = len(standings)

    COL = "2rem 1fr 3rem 3rem 3rem 3rem 3.5rem"
    CELL = f"display:grid; grid-template-columns:{COL}; align-items:center; gap:.3rem; padding:.7rem 1rem;"
    HEAD = f"display:grid; grid-template-columns:{COL}; gap:.3rem; padding:.65rem 1rem;"

    rows_html = ""
    for i, t in enumerate(standings):
        pos = i + 1
        lborder   = "#f59e0b" if pos == 1 else "#34d399" if pos == 2 else "#f87171" if pos == n else "transparent"
        pos_color = "#f59e0b" if pos == 1 else "#34d399" if pos == 2 else "#f87171" if pos == n else "#9ca3af"
        gd        = t["gd"]
        gd_color  = "#34d399" if gd > 0 else "#f87171" if gd < 0 else "#9ca3af"
        gd_str    = f"+{gd}" if gd > 0 else str(gd)
        rows_html += (
            f'<div style="{CELL} background:#1f2937; border-top:1px solid #374151;'
            f' border-left:4px solid {lborder}; font-size:.9rem; color:#f1f5f9;">'
            f'<span style="color:{pos_color}; font-weight:700;">{pos}</span>'
            f'<span style="display:flex; align-items:center; gap:.5rem; font-weight:500;">'
            f'{flag_img(t["team"], h=20)} {t["team"]}</span>'
            f'<span style="color:#f59e0b; font-weight:800; text-align:right;">{t["pts"]}</span>'
            f'<span style="color:#9ca3af; text-align:right;">3</span>'
            f'<span style="color:#6ee7b7; text-align:right;">{t["gf"]}</span>'
            f'<span style="color:#fca5a5; text-align:right;">{t["ga"]}</span>'
            f'<span style="color:{gd_color}; font-weight:600; text-align:right;">{gd_str}</span>'
            f'</div>'
        )

    full_html = (
        f'<div style="border:1px solid #374151; border-radius:14px; overflow:hidden; margin-bottom:1rem;">'
        f'<div style="{HEAD} background:#253044; color:#f59e0b; font-size:.73rem;'
        f' font-weight:700; text-transform:uppercase; letter-spacing:.07em;">'
        f'<span>#</span><span>Equipo</span>'
        f'<span style="text-align:right">Pts</span><span style="text-align:right">PJ</span>'
        f'<span style="text-align:right">GF</span><span style="text-align:right">GC</span>'
        f'<span style="text-align:right">DG</span></div>'
        f'{rows_html}'
        f'<div style="background:#172033; padding:.45rem 1rem; font-size:.72rem; color:#9ca3af;'
        f' display:flex; gap:1.2rem; border-top:1px solid #374151;">'
        f'<span><span style="color:#f59e0b;">&#9632;</span> 1.&ordm;</span>'
        f'<span><span style="color:#34d399;">&#9632;</span> Clasificado</span>'
        f'<span><span style="color:#f87171;">&#9632;</span> Eliminado</span>'
        f'</div></div>'
    )
    st.html(full_html)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 · Eliminatorias
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    ronda = st.radio(
        "Ronda:",
        list(ROUNDS.keys()),
        format_func=lambda x: ROUNDS[x],
        horizontal=True,
        key="ronda",
    )

    ko_matches = bracket["knockouts"][ronda]
    label = ROUNDS[ronda]
    n_m   = len(ko_matches)

    st.markdown(
        f'<h4 style="color:#f1f5f9; font-weight:700; margin:1rem 0 .6rem;">'
        f'{label} · {n_m} {"partido" if n_m == 1 else "partidos"}</h4>',
        unsafe_allow_html=True,
    )

    items    = list(ko_matches.items())
    use_cols = n_m > 2

    if use_cols:
        col_a, col_b = st.columns(2)
        pairs = [(col_a if i % 2 == 0 else col_b, info) for i, (_, info) in enumerate(items)]
    else:
        pairs = [(st, info) for _, info in items]

    for container, info in pairs:
        advances = info["advances"]
        prob     = info["advances_prob"] * 100
        ph  = info["probs_1X2"]["home_win"] * 100
        pd_ = info["probs_1X2"]["draw"]     * 100
        pa  = info["probs_1X2"]["away_win"] * 100

        home_s = "font-weight:800; color:#f1f5f9;" if advances == info["home"] else "color:#9ca3af;"
        away_s = "font-weight:800; color:#f1f5f9;" if advances == info["away"] else "color:#9ca3af;"

        html = f"""
        <div class="ko-card">
          <div style="display:flex; align-items:center; gap:.6rem; flex-wrap:wrap;">
            <span style="display:flex; align-items:center; gap:.4rem; flex:1; {home_s} font-size:.93rem;">
              {flag_img(info['home'], h=22)} {info['home']}
            </span>
            <span class="score-badge">{info['score']}</span>
            <span style="display:flex; align-items:center; justify-content:flex-end;
                         gap:.4rem; flex:1; {away_s} font-size:.93rem;">
              {info['away']} {flag_img(info['away'], h=22)}
            </span>
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center;
                      margin-top:.55rem; flex-wrap:wrap; gap:.4rem;">
            <span style="font-size:.75rem; color:#6b7280;">{ph:.0f}% · {pd_:.0f}% · {pa:.0f}%</span>
            <span class="advances-badge">
              {flag_img(advances, h=16)} {advances} · {prob:.1f}%
            </span>
          </div>
        </div>
        """
        container.markdown(html, unsafe_allow_html=True)
