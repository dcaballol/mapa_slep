import streamlit as st
import folium
from folium.plugins import MarkerCluster, Fullscreen
from streamlit_folium import st_folium
import pandas as pd
import math
import re
import requests

# ── Configuración de página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mapa Establecimientos SLEP Santa Corina",
    page_icon="🏫",
    layout="wide",
)

# ── Estilos CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #f0f4f8; }

  .header-banner {
    background: linear-gradient(135deg, #1a3a5c 0%, #2563a8 100%);
    padding: 1.2rem 1.8rem; border-radius: 12px;
    color: white; margin-bottom: 1.2rem;
  }
  .header-banner h1 { margin: 0; font-size: 1.6rem; font-weight: 700; }
  .header-banner p  { margin: 0.3rem 0 0; font-size: 0.9rem; opacity: 0.85; }

  .metric-card {
    background: white; border-radius: 10px; padding: 1rem;
    text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }
  .metric-num   { font-size: 2rem; font-weight: 700; color: #2563a8; }
  .metric-label { font-size: 0.78rem; color: #64748b; text-transform: uppercase; letter-spacing: .05em; }
  .stSelectbox label { font-weight: 600; }

  /* ── Tabs estilo píldora limpio ── */
  .stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #dde3ed;
    padding: 5px 6px;
    border-radius: 10px;
    margin-bottom: 1rem;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 7px;
    padding: 8px 20px;
    font-size: 0.92rem;
    font-weight: 500;
    color: #4a5568;
    border: none;
  }
  .stTabs [data-baseweb="tab"]:hover {
    background: rgba(255,255,255,0.6);
    color: #1a202c;
  }
  .stTabs [aria-selected="true"] {
    background: white !important;
    color: #1a3a5c !important;
    font-weight: 700 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.13) !important;
  }
  .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
  .stTabs [data-baseweb="tab-border"]    { display: none !important; }

  /* Expander header */
  .streamlit-expanderHeader { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── Datos embebidos ────────────────────────────────────────────────────────────
RAW = [
    (8518,"LICEO ESTACIÓN CENTRAL","ESTACIÓN CENTRAL","Purísima #58",-33.456606,-70.698432),
    (8519,"ESCUELA BÁSICA PEDRO AGUIRRE CERDA","CERRILLOS","Avenida Buzeta #4479",-33.481839,-70.693164),
    (8521,"ESCUELA CARLOS CONDELL DE LA HAZA","ESTACIÓN CENTRAL","Transit #661",-33.461464,-70.700384),
    (8537,"ESCUELA ARNALDO FALABELLA","ESTACIÓN CENTRAL","Calle Coronel Godoy #555",-33.458589,-70.692224),
    (8544,"ESCUELA BÁSICA ARTURO ALESSANDRI PALMA","ESTACIÓN CENTRAL","Av Libertador Bernardo O'higgins #4558",-33.456016,-70.698750),
    (8556,"ESCUELA REPÚBLICA DE AUSTRIA","ESTACIÓN CENTRAL","Teniente Luis Cruz Martínez #4431",-33.475292,-70.694990),
    (8558,"ESCUELA BÁSICA VÍCTOR JARA","ESTACIÓN CENTRAL","Pinguinos #4250",-33.471515,-70.691880),
    (8579,"ESCUELA BÁSICA UNIÓN LATINOAMERICANA","ESTACIÓN CENTRAL","Santa Teresa #1071",-33.463481,-70.691737),
    (8587,"LICEO DE ADULTOS LUIS GÓMEZ CATALÁN","ESTACIÓN CENTRAL","Av Libertador Bernardo O'higgins #4552",-33.455536,-70.697520),
    (9861,"CENTRO EDUC.MUNIC. DR. AMADOR NEGHME RODRÍGUEZ","ESTACIÓN CENTRAL","Av 5 de Abril #4710",-33.472198,-70.720809),
    (9862,"LICEO BICENTENARIO POLIVALENTE A N°71 GUILLERMO FELIÚ CRUZ","ESTACIÓN CENTRAL","Av 5 de Abril #4800",-33.463820,-70.701440),
    (9863,"LICEO SANTIAGO BUERAS Y AVARIA","MAIPÚ","Capellan Benavides #2321",-33.505274,-70.751742),
    (9864,"LICEO JOSÉ IGNACIO ZENTENO","MAIPÚ","Av de la Victoria #2400",-33.503402,-70.769155),
    (9865,"LICEO POLIVALENTE DR. LUIS VARGAS SALCEDO","CERRILLOS","Vargas Salcedo #1720",-33.498959,-70.730978),
    (9867,"CENTRO DE EDUC. TECN.PROFESIONAL CODEDUC","MAIPÚ","Segunda Transversal #1900",-33.509559,-70.747255),
    (9869,"ESCUELA BÁSICA REPÚBLICA DE FRANCIA","ESTACIÓN CENTRAL","Laitec #5850",-33.476160,-70.710876),
    (9870,"ESCUELA BÁSICA CÓNDORES DE PLATA","CERRILLOS","Salomón Sack #925",-33.493812,-70.718154),
    (9872,"ESCUELA BASICA PROF.RAMÓN DEL RÍO","ESTACIÓN CENTRAL","Calle Chacao #1036",-33.466036,-70.702886),
    (9873,"ESCUELA BÁSICA PACTO ANDINO","ESTACIÓN CENTRAL","Las Lilas #5810",-33.463514,-70.709209),
    (9874,"ESCUELA LOTHAR KOMMER BRUGER","CERRILLOS","Avenida Las Torres #539",-33.506905,-70.734126),
    (9875,"ESCUELA CERRILLOS","CERRILLOS","Los Cerrillos #570",-33.493965,-70.710273),
    (9876,"ESCUELA GENERAL SAN MARTÍN","MAIPÚ","Av 5 de Abril #409",-33.510406,-70.762212),
    (9877,"ESCUELA GENERAL OHIGGINS","MAIPÚ","Emiliano Llona #1853",-33.509716,-70.763082),
    (9878,"ESCUELA PRESIDENTE RIESCO ERRÁZURIZ","MAIPÚ","Pasaje San Ramón #101",-33.526210,-70.759092),
    (9879,"ESCUELA BÁSICA CAROLINA VERGARA AYARES","ESTACIÓN CENTRAL","Coyhaique #6055",-33.473384,-70.705159),
    (9880,"ESCUELA BÁSICA ESTADO DE PALESTINA","ESTACIÓN CENTRAL","Coyhaique #6215",-33.473583,-70.701607),
    (9881,"ESCUELA VICENTE REYES PALAZUELOS","MAIPÚ","Elizabeth Heisse #500",-33.517077,-70.750836),
    (9882,"ESCUELA J.PRIETO VIAL","CERRILLOS","Golfo de México #361",-33.509246,-70.738273),
    (9883,"ESCUELA BÁSICA N 263 RAMON FREIRE","MAIPÚ","Blanco Encalada #1111",-33.498514,-70.771112),
    (9884,"ESCUELA LEÓN HUMBERTO VALENZUELA","MAIPÚ","Pasaje Andes #680",-33.497483,-70.765287),
    (9886,"ESCUELA ESTRELLA REINA DE CHILE","CERRILLOS","14 de octubre #1151",-33.499828,-70.725391),
    (9887,"LICEO EL LLANO DE MAIPÚ","MAIPÚ","Las Acacias #535",-33.516657,-70.750116),
    (9888,"ESCUELA SANTA ADELA","CERRILLOS","Paseo Los profesores #7400, Villa Santa Adela",-33.509348,-70.716482),
    (9889,"LICEO REINO DE DINAMARCA","MAIPÚ","Germán Greves #265",-33.508731,-70.827589),
    (9890,"ESCUELA TOMAS VARGAS","MAIPÚ","Asunción #1440",-33.499999,-70.776254),
    (9891,"REPUBLICA DE GUATEMALA","MAIPÚ","Presidente German Riesco #3315",-33.497502,-70.749556),
    (9892,"ESCUELA LAS AMÉRICAS","MAIPÚ","Marco Antonio #16916",-33.548310,-70.772968),
    (9893,"ESCUELA DIFERENCIAL ANDALUÉ","MAIPÚ","Calle San José #860",-33.515860,-70.767456),
    (9895,"ESCUELA BÁSICA REINA DE SUECIA","MAIPÚ","Av Arquitecto Hugo Bravo #1677",-33.473672,-70.756017),
    (9896,"LICEO MAIPÚ DE LAS ARTES Y LA TECNOLOGÍA","MAIPÚ","Camino a Melipilla #8720",-33.510754,-70.724213),
    (12255,"COLEGIO ALCÁZAR","MAIPÚ","Av Parque Central Poniente #500",-33.557051,-70.791340),
    (24883,"ESCUELA BÁSICA MUNICIPAL SAN LUIS","MAIPÚ","Avenida Las Naciones #2020",-33.512336,-70.785138),
    (25042,"ESCUELA BÁSICA LOS BOSQUINOS","MAIPÚ","Av El Olimpo #650",-33.529498,-70.773419),
    (25186,"COLEGIO MUNIC. SAN SEBASTIAN DE RINCONADA","MAIPÚ","La Galaxia #2370",-33.508713,-70.795438),
    (25314,"ESCUELA BÁSICA 1737 LOS ALERCES DE MAIPÚ","MAIPÚ","Glorias Navales #2040, Villa Arturo Prat",-33.539069,-70.777922),
    (25539,"EJERCITO LIBERTADOR DE CERRILLOS","CERRILLOS","Rosa Ester Rodríguez #6902",-33.488988,-70.723182),
    (25770,"LICEO NACIONAL DE MAIPÚ","MAIPÚ","Av Portales #2471",-33.519165,-70.792454),
    (31065,"LICEO TECNOLÓGICO BICENTENARIO ENRIQUE KIRBERG BALTIANSKY","MAIPÚ","Av El Conquistador #1561",-33.528244,-70.796830),
    (31074,"LICEO BICENTENARIO DE NIÑAS DE MAIPÚ","MAIPÚ","Av Ingeniero Eduardo Domínguez #1377",-33.491425,-70.784010),
    ("13102007","SALOMON SACK","CERRILLOS","Salomón Sack #925",-33.493678,-70.718424),
    ("13102008","CARDENAL RAÚL SILVA HENRÍQUEZ","CERRILLOS","Cardenal San Francisco Fresno #240",-33.480387,-70.719868),
    ("13102009","EL MIRADOR","CERRILLOS","Avda Las Torres #7590",-33.500989,-70.733227),
    ("13102010","ANGEL FANTUZI","CERRILLOS","Diputado Angel Fantuzzi #7621",-33.513932,-70.702073),
    ("13102011","RÍO MAGDALENA","CERRILLOS","Rio Magdalena #540",-33.505946,-70.733439),
    ("13102013","ORESTE PLATH","CERRILLOS","Cost Nte. del Ferrocarril #6893",-33.486068,-70.721424),
    ("13102014","VILLA MÉXICO","CERRILLOS","Golfo de México #361",-33.509257,-70.737535),
    ("13106017","AVELUZ","ESTACIÓN CENTRAL","Aeropuerto #1041",-33.474457,-70.712339),
    ("13106018","LOS ANGELITOS DE VILLA FRANCIA","ESTACIÓN CENTRAL","Las Estepas #845",-33.471882,-70.714581),
    ("13106019","LAS LUCIÉRNAGAS","ESTACIÓN CENTRAL","Padre Vicente Irarrázabal #1700",-33.470135,-70.692471),
    ("13106021","DUENDES Y ESTRELLITAS","ESTACIÓN CENTRAL","Curacaví 808",-33.472420,-70.721536),
    ("13106022","ARTEMISA","ESTACIÓN CENTRAL","Transit #485",-33.459969,-70.700744),
    ("13106023","KIMELÜ","ESTACIÓN CENTRAL","Pasaje Magallanes 6234",-33.470341,-70.701774),
    ("13106024","MIS PRIMERAS HUELLAS","ESTACIÓN CENTRAL","Pje. Coyhaique #6225",-33.473192,-70.701066),
    ("13106025","AYELÉN","ESTACIÓN CENTRAL","Huillinco #6062",-33.474208,-70.705462),
    ("13106026","ESTACIÓN ALEGRÍA","ESTACIÓN CENTRAL","Calle Diagonal #4687",-33.476557,-70.697601),
    ("13119003","PEQUEÑOS EXPLORADORES","MAIPÚ","Av. La Galaxia #1000",-33.520082,-70.794539),
    ("13119004","DIVINA PROVIDENCIA","MAIPÚ","San José #3041",-33.517338,-70.797493),
    ("13119010","EMANUEL","MAIPÚ","Av. Cuatro Poniente #1230",-33.518506,-70.791624),
    ("13119017","BLANCO ENCALADA","MAIPÚ","Etna #330",-33.497287,-70.767578),
    ("13119018","VICENTE REYES","MAIPÚ","Vicente Reyes #1081",-33.516245,-70.751034),
    ("13119019","PEHUÉN","MAIPÚ","Av. Sur #2860",-33.522270,-70.795153),
    ("13119020","PALLAMAR","MAIPÚ","Pozo Almonte #1484",-33.513492,-70.745950),
    ("13119021","SAN JUAN","MAIPÚ","Jorge Guerra #321",-33.540238,-70.770432),
    ("13119022","PINCELES Y COLORES","MAIPÚ","Av. Tres Poniente #2400",-33.506823,-70.779660),
    ("13119023","NUEVO MUNDO","MAIPÚ","Av. El Descanso #1540",-33.469690,-70.758128),
    ("13119024","ANKATU","MAIPÚ","Av. El Conquistador #1451",-33.518139,-70.796617),
    ("13119025","KIM RUKA","MAIPÚ","La Galaxia #255",-33.525379,-70.794038),
    ("13119026","LAS ABEJITAS","MAIPÚ","Octavio Paz #2811",-33.501160,-70.794976),
    ("13119027","CASCANUECES","MAIPÚ","Av. Marta Ossa Ruíz #1060",-33.465887,-70.752521),
    ("13119028","PEQUEÑAS MARAVILLAS","MAIPÚ","Collanco #1260",-33.491684,-70.768656),
    ("13119029","AITUÉ","MAIPÚ","Mujeres Chilenas #2746",-33.503804,-70.793309),
    ("13119030","SEMILLITAS","MAIPÚ","Canadá #3440",-33.497034,-70.738403),
    ("13119031","MOLINO DE COLORES","MAIPÚ","Gustavo Eiffel #5171",-33.473184,-70.750185),
    ("13119032","SINFONÍA MÁGICA","MAIPÚ","Av. La Sinfonía #1000",-33.489372,-70.763971),
    ("13119033","LOS SOLCITOS","MAIPÚ","Valle de los Reyes #127",-33.527056,-70.798231),
    ("13119034","ALTAWEÑI","MAIPÚ","La Farfana #2070",-33.487756,-70.778801),
    ("13119035","RAYEN MAPU","MAIPÚ","Santa Priscila #3101",-33.498916,-70.781897),
    ("13119036","ALON KURA","MAIPÚ","Lumen #3737",-33.493510,-70.735827),
    ("13119040","VALLE VERDE","MAIPÚ","Alaska #7780",-33.490327,-70.732810),
    ("13119042","ESDRAS","MAIPÚ","Esdras #60",-33.545296,-70.781532),
    ("13119043","EL TRANQUE","MAIPÚ","El Tranque #201",-33.549060,-70.794105),
]

df = pd.DataFrame(RAW, columns=["RBD","Establecimiento","Comuna","Dirección","LAT","LONG"])

COMUNA_CONFIG = {
    "ESTACIÓN CENTRAL": {"color": "#e74c3c", "folium_color": "red",    "emoji": "🔴"},
    "CERRILLOS":        {"color": "#f39c12", "folium_color": "orange",  "emoji": "🟠"},
    "MAIPÚ":            {"color": "#27ae60", "folium_color": "green",   "emoji": "🟢"},
}

# ── Funciones de optimización de ruta ─────────────────────────────────────────

try:
    import googlemaps as _gm
    _GMAPS_OK = True
except ImportError:
    _GMAPS_OK = False


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371
    r1, r2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(r1)*math.cos(r2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def _haversine_matrix(coords):
    n = len(coords)
    return [[_haversine(coords[i][0], coords[i][1], coords[j][0], coords[j][1])
             for j in range(n)] for i in range(n)]


def _osrm_time_matrix(coords):
    """Matriz de tiempos de conducción (minutos) vía OSRM Table API. Retorna None si falla."""
    coords_str = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in coords)
    url = f"https://router.project-osrm.org/table/v1/driving/{coords_str}?annotations=duration"
    try:
        resp = requests.get(url, timeout=15)
        data = resp.json()
        if data.get("code") == "Ok":
            return [[v / 60 for v in row] for row in data["durations"]]
    except Exception:
        pass
    return None


def _gmaps_matrix(coords, key, mode):
    client = _gm.Client(key=key)
    n = len(coords)
    mat = [[0.0]*n for _ in range(n)]
    dur = [[0.0]*n for _ in range(n)]
    strs = [f"{c[0]:.6f},{c[1]:.6f}" for c in coords]
    for i in range(0, n, 25):
        for j in range(0, n, 25):
            res = client.distance_matrix(strs[i:i+25], strs[j:j+25], mode=mode)
            for ri, row in enumerate(res['rows']):
                for rj, el in enumerate(row['elements']):
                    gi, gj = i + ri, j + rj
                    if el['status'] == 'OK':
                        mat[gi][gj] = el['distance']['value'] / 1000
                        dur[gi][gj] = el['duration']['value'] / 60
                    else:
                        mat[gi][gj] = _haversine(*coords[gi], *coords[gj])
                        dur[gi][gj] = mat[gi][gj] * 2
    return mat, dur


def _nn_route(mat):
    n = len(mat)
    vis = [False] * n
    route = [0]
    vis[0] = True
    for _ in range(n - 1):
        cur = route[-1]
        nxt = min((j for j in range(n) if not vis[j]), key=lambda j: mat[cur][j])
        route.append(nxt)
        vis[nxt] = True
    return route


def _two_opt(route, mat):
    best = list(route)
    n = len(best)
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                a, b = best[i - 1], best[i]
                c = best[j]
                d = best[j + 1] if j + 1 < n else None
                delta = (mat[a][c] + (mat[b][d] if d is not None else 0)
                         - mat[a][b] - (mat[c][d] if d is not None else 0))
                if delta < -1e-9:
                    best[i:j + 1] = best[i:j + 1][::-1]
                    improved = True
    return best


def _gmaps_urls(route_coords, gmode):
    """URL de Google Maps con todas las paradas en una sola URL cuando es posible.
    Usa formato ?api=1 (hasta 23 waypoints = 25 paradas totales por URL).
    Solo divide si hay más de 25 paradas totales.
    gmode: 'driving' | 'transit' | 'walking'
    """
    urls = []
    n = len(route_coords)
    chunk = 23  # 23 waypoints + origen + destino = 25 paradas totales por URL
    i = 0
    while i < n - 1:
        ei = min(i + chunk + 1, n - 1)
        origin = route_coords[i]
        dest   = route_coords[ei]
        wps    = route_coords[i + 1:ei]
        url = (f"https://www.google.com/maps/dir/?api=1"
               f"&origin={origin[0]:.6f},{origin[1]:.6f}"
               f"&destination={dest[0]:.6f},{dest[1]:.6f}"
               f"&travelmode={gmode}")
        if wps:
            url += "&waypoints=" + "|".join(f"{p[0]:.6f},{p[1]:.6f}" for p in wps)
        urls.append(url)
        i = ei
        if i >= n - 1:
            break
    return urls


def _road_route(route_coords):
    """Geometría real por calles via OSRM. Retorna (geom_coords, dist_km, dur_min).
    En caso de error retorna (route_coords, None, None)."""
    coords_str = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in route_coords)
    url = (f"https://router.project-osrm.org/route/v1/driving/{coords_str}"
           f"?overview=full&geometries=geojson")
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("code") == "Ok":
            route = data["routes"][0]
            geom = [(p[1], p[0]) for p in route["geometry"]["coordinates"]]
            dist_km = route["distance"] / 1000
            dur_min = route["duration"] / 60
            return geom, dist_km, dur_min
    except Exception:
        pass
    return route_coords, None, None


def _num_icon(n, color="#1a3a5c"):
    return folium.DivIcon(
        html=(f'<div style="background:{color};color:white;border-radius:50%;'
              f'width:28px;height:28px;line-height:28px;text-align:center;'
              f'font-weight:700;font-size:12px;border:2px solid white;'
              f'box-shadow:0 2px 6px rgba(0,0,0,.35);">{n}</div>'),
        icon_size=(28, 28),
        icon_anchor=(14, 14),
    )


# ── Session state ──────────────────────────────────────────────────────────────
if "favorites" not in st.session_state:
    st.session_state["favorites"] = set()
if "rbds_input" not in st.session_state:
    st.session_state["rbds_input"] = ""

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
  <h1>🏫 Mapa de Establecimientos — SLEP Santa Corina</h1>
  <p>Visualización georreferenciada · Comunas de Estación Central, Cerrillos y Maipú · Región Metropolitana</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Flag_of_Chile.svg/60px-Flag_of_Chile.svg.png", width=40)
    st.markdown("### 🔍 Filtros (Mapa)")
    comunas_disp = sorted(df["Comuna"].unique())
    comunas_sel = st.multiselect(
        "Comunas",
        options=comunas_disp,
        default=comunas_disp,
        format_func=lambda c: f"{COMUNA_CONFIG[c]['emoji']} {c.title()}"
    )
    busqueda = st.text_input("🔎 Buscar establecimiento", placeholder="Nombre o dirección...")
    cluster_on = st.toggle("Agrupar marcadores en zonas", value=False)
    st.markdown("---")
    st.markdown("#### 🎨 Leyenda")
    for c, cfg in COMUNA_CONFIG.items():
        st.markdown(f"{cfg['emoji']} **{c.title()}**")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_mapa, tab_ruta = st.tabs(["🗺️ Mapa de Establecimientos", "🛣️ Optimizar Ruta de Visitas"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Mapa
# ══════════════════════════════════════════════════════════════════════════════
with tab_mapa:
    dff = df[df["Comuna"].isin(comunas_sel)].copy()
    if busqueda:
        mask = (
            dff["Establecimiento"].str.contains(busqueda, case=False, na=False) |
            dff["Dirección"].str.contains(busqueda, case=False, na=False)
        )
        dff = dff[mask]

    col1, col2, col3, col4 = st.columns(4)
    totales = {c: len(df[df["Comuna"] == c]) for c in comunas_disp}
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-num">{len(dff)}</div><div class="metric-label">Establecimientos visibles</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#e74c3c">{totales["ESTACIÓN CENTRAL"]}</div><div class="metric-label">🔴 Estación Central</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#f39c12">{totales["CERRILLOS"]}</div><div class="metric-label">🟠 Cerrillos</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#27ae60">{totales["MAIPÚ"]}</div><div class="metric-label">🟢 Maipú</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    centro_lat = dff["LAT"].mean() if len(dff) > 0 else -33.50
    centro_lon = dff["LONG"].mean() if len(dff) > 0 else -70.75

    m = folium.Map(location=[centro_lat, centro_lon], zoom_start=12,
                   tiles="CartoDB positron", control_scale=True)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)
    folium.TileLayer("CartoDB dark_matter", name="Modo oscuro").add_to(m)
    folium.LayerControl(position="topright").add_to(m)
    Fullscreen(position="topleft").add_to(m)

    group = MarkerCluster(name="Agrupados", show=cluster_on).add_to(m) if cluster_on else m

    for _, row in dff.iterrows():
        cfg = COMUNA_CONFIG.get(row["Comuna"], {"folium_color": "blue", "emoji": "🔵", "color": "#3498db"})
        gmaps_url     = f"https://www.google.com/maps/dir/?api=1&destination={row['LAT']},{row['LONG']}&travelmode=driving"
        gmaps_walk    = f"https://www.google.com/maps/dir/?api=1&destination={row['LAT']},{row['LONG']}&travelmode=walking"
        gmaps_transit = f"https://www.google.com/maps/dir/?api=1&destination={row['LAT']},{row['LONG']}&travelmode=transit"
        popup_html = f"""
        <div style="font-family:Arial,sans-serif;min-width:250px;max-width:300px;">
          <div style="background:{cfg['color']};color:white;padding:8px 12px;border-radius:6px 6px 0 0;font-weight:700;font-size:13px;">
            {cfg['emoji']} {row['Establecimiento']}
          </div>
          <div style="padding:10px 12px;background:#fff;border-radius:0 0 6px 6px;border:1px solid #e2e8f0;">
            <p style="margin:4px 0;font-size:12px;"><b>📍 Dirección:</b> {row['Dirección']}</p>
            <p style="margin:4px 0;font-size:12px;"><b>🏘️ Comuna:</b> {row['Comuna'].title()}</p>
            <p style="margin:4px 0;font-size:12px;"><b>🔑 RBD/Cód.:</b> {row['RBD']}</p>
            <p style="margin:4px 0;font-size:11px;color:#64748b;">📌 {row['LAT']:.6f}, {row['LONG']:.6f}</p>
            <hr style="margin:8px 0;border:none;border-top:1px solid #e2e8f0;">
            <p style="margin:4px 0 6px;font-size:11px;font-weight:700;color:#475569;">🗺️ CÓMO LLEGAR</p>
            <div style="display:flex;gap:5px;flex-wrap:wrap;">
              <a href="{gmaps_url}" target="_blank" style="background:#1a73e8;color:white;padding:5px 9px;border-radius:5px;text-decoration:none;font-size:11px;font-weight:600;">🚗 En auto</a>
              <a href="{gmaps_transit}" target="_blank" style="background:#0f9d58;color:white;padding:5px 9px;border-radius:5px;text-decoration:none;font-size:11px;font-weight:600;">🚌 Transporte</a>
              <a href="{gmaps_walk}" target="_blank" style="background:#f57c00;color:white;padding:5px 9px;border-radius:5px;text-decoration:none;font-size:11px;font-weight:600;">🚶 A pie</a>
            </div>
          </div>
        </div>"""
        folium.Marker(
            location=[row["LAT"], row["LONG"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{cfg['emoji']} {row['Establecimiento']}",
            icon=folium.Icon(color=cfg["folium_color"], icon="graduation-cap", prefix="fa"),
        ).add_to(group if cluster_on else m)

    map_data = st_folium(m, width="100%", height=580, returned_objects=["last_object_clicked"])

    if map_data and map_data.get("last_object_clicked"):
        clicked = map_data["last_object_clicked"]
        lat_c, lon_c = clicked.get("lat"), clicked.get("lng")
        if lat_c and lon_c:
            match = dff[(abs(dff["LAT"] - lat_c) < 0.0005) & (abs(dff["LONG"] - lon_c) < 0.0005)]
            if not match.empty:
                r = match.iloc[0]
                cfg = COMUNA_CONFIG.get(r["Comuna"], {"color": "#3498db", "emoji": "🔵"})
                gm_auto     = f"https://www.google.com/maps/dir/?api=1&destination={r['LAT']},{r['LONG']}&travelmode=driving"
                gm_transito = f"https://www.google.com/maps/dir/?api=1&destination={r['LAT']},{r['LONG']}&travelmode=transit"
                gm_pie      = f"https://www.google.com/maps/dir/?api=1&destination={r['LAT']},{r['LONG']}&travelmode=walking"
                st.markdown(f"""
                <div style="background:white;border-left:5px solid {cfg['color']};padding:1rem 1.4rem;border-radius:8px;margin-top:.5rem;box-shadow:0 2px 8px rgba(0,0,0,.08);">
                  <h4 style="margin:0 0 .4rem;color:{cfg['color']};">{cfg['emoji']} {r['Establecimiento']}</h4>
                  <p style="margin:.2rem 0;font-size:.9rem;">📍 {r['Dirección']}</p>
                  <p style="margin:.2rem 0 .7rem;font-size:.9rem;">🏘️ {r['Comuna'].title()} &nbsp;|&nbsp; 🔑 RBD: {r['RBD']}</p>
                  <p style="margin:0 0 .4rem;font-size:.8rem;font-weight:700;color:#475569;">🗺️ CÓMO LLEGAR</p>
                  <a href="{gm_auto}" target="_blank" style="background:#1a73e8;color:white;padding:6px 12px;border-radius:6px;text-decoration:none;font-size:.82rem;font-weight:600;margin-right:6px;">🚗 En auto</a>
                  <a href="{gm_transito}" target="_blank" style="background:#0f9d58;color:white;padding:6px 12px;border-radius:6px;text-decoration:none;font-size:.82rem;font-weight:600;margin-right:6px;">🚌 Transporte público</a>
                  <a href="{gm_pie}" target="_blank" style="background:#f57c00;color:white;padding:6px 12px;border-radius:6px;text-decoration:none;font-size:.82rem;font-weight:600;">🚶 A pie</a>
                </div>""", unsafe_allow_html=True)

    with st.expander("📋 Tabla de datos — listado completo de establecimientos", expanded=False):
        st.dataframe(
            dff[["RBD", "Establecimiento", "Comuna", "Dirección"]].rename(columns={"RBD": "RBD / Cód. JUNJI", "Establecimiento": "Nombre"}),
            use_container_width=True, hide_index=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Optimizar Ruta
# ══════════════════════════════════════════════════════════════════════════════
with tab_ruta:
    st.markdown("### 🛣️ Optimizador de Ruta de Visitas")
    st.caption("Ingresa los RBD de los establecimientos que necesitas visitar. La app calcula el orden óptimo de visitas usando Vecino Más Cercano + mejora 2-opt.")

    col_ctrl, col_res = st.columns([1, 2], gap="medium")

    with col_ctrl:
        # ── Favoritos ──────────────────────────────────────────────────────
        with st.expander("⭐ Favoritos", expanded=False):
            st.caption("Marca los establecimientos que visitas frecuentemente para cargarlos rápido.")
            all_rbd_opts = df["RBD"].tolist()
            fav_stored = [r for r in st.session_state["favorites"] if r in all_rbd_opts]
            fav_sel = st.multiselect(
                "Establecimientos favoritos",
                options=all_rbd_opts,
                default=fav_stored,
                format_func=lambda r: f"{r} · {df[df['RBD']==r]['Establecimiento'].values[0]}",
                label_visibility="collapsed",
            )
            cf1, cf2 = st.columns(2)
            with cf1:
                if st.button("💾 Guardar", use_container_width=True):
                    st.session_state["favorites"] = set(fav_sel)
                    st.success(f"✅ {len(fav_sel)} favoritos guardados")
            with cf2:
                if st.button("📥 Cargar en ruta", use_container_width=True,
                             disabled=not st.session_state["favorites"]):
                    st.session_state["rbds_input"] = "\n".join(
                        str(r) for r in sorted(str(r) for r in st.session_state["favorites"])
                    )
                    st.rerun()

        rbds_raw = st.text_area(
            "📋 RBDs a visitar",
            key="rbds_input",
            height=190,
            placeholder="Pega los RBDs aquí, uno por línea.\nAcepta formato 'RBD - Nombre' o solo el número:\n\n9863 - Liceo Santiago Bueras\n9864\n9865\n...",
            help="Acepta 'RBD', 'RBD - Nombre', separados por línea, coma o punto y coma.",
        )

        st.markdown("**📍 Punto de inicio**")
        orig_tipo = st.radio(
            "Origen",
            ["Desde una dirección / coordenadas", "Desde un establecimiento de la lista", "Centroide del grupo (automático)"],
            label_visibility="collapsed",
        )

        # Defaults: SLEP Santa Corina (Estación Central, zona central de colegios)
        orig_lat_val, orig_lon_val = -33.4650, -70.7020

        if orig_tipo == "Desde una dirección / coordenadas":
            st.caption("Ingresa las coordenadas de tu punto de partida (puedes obtenerlas haciendo clic derecho en Google Maps).")
            c1, c2 = st.columns(2)
            with c1:
                orig_lat_val = st.number_input("Latitud", value=-33.4650, format="%.4f", step=0.0001)
            with c2:
                orig_lon_val = st.number_input("Longitud", value=-70.7020, format="%.4f", step=0.0001)

        elif orig_tipo == "Desde un establecimiento de la lista":
            all_rbds = df["RBD"].tolist()
            orig_sel = st.selectbox(
                "Establecimiento de inicio",
                options=all_rbds,
                format_func=lambda r: f"{r} · {df[df['RBD'] == r]['Establecimiento'].values[0]}",
            )
            sel_r = df[df["RBD"] == orig_sel].iloc[0]
            orig_lat_val, orig_lon_val = sel_r["LAT"], sel_r["LONG"]
            st.caption(f"📍 {sel_r['Dirección']}")

        st.markdown("**🏁 Punto de término**")
        end_tipo = st.radio(
            "Término",
            ["🏠 Volver al inicio (ruta circular)",
             "🏁 Terminar en el último establecimiento",
             "📌 Terminar en coordenadas específicas"],
            label_visibility="collapsed",
        )
        round_trip  = end_tipo.startswith("🏠")
        custom_end  = end_tipo.startswith("📌")
        end_lat_val = end_lon_val = None
        if custom_end:
            st.caption("Coordenadas del punto final (clic derecho en Google Maps).")
            ce1, ce2 = st.columns(2)
            with ce1:
                end_lat_val = st.number_input("Latitud fin", value=-33.4650, format="%.4f", step=0.0001)
            with ce2:
                end_lon_val = st.number_input("Longitud fin", value=-70.7020, format="%.4f", step=0.0001)

        modo_opts = {"🚗 Auto": "driving", "🚌 Transporte público": "transit", "🚶 A pie": "walking"}
        modo_label = st.radio("Modo de viaje", list(modo_opts.keys()))
        gmode = modo_opts[modo_label]

        with st.expander("⚙️ Configuración avanzada"):
            api_key_in = st.text_input(
                "API Key Google Maps (opcional)",
                type="password",
                help="Con una API Key se calculan distancias reales de ruta (Distance Matrix API). Sin ella se usa distancia en línea recta (Haversine).",
            )
            if api_key_in and not _GMAPS_OK:
                st.warning("Para usar la API instala: `pip install googlemaps`")
            use_2opt = st.checkbox(
                "Mejorar con 2-opt",
                value=True,
                help="Aplica mejora local sobre la ruta inicial. Para más de 25 paradas se omite automáticamente.",
            )

        calcular = st.button("🔄 Calcular Ruta Óptima", type="primary", use_container_width=True)

    with col_res:
        if not calcular:
            st.info("👈 Ingresa los RBDs a la izquierda y presiona **Calcular Ruta Óptima**.")
            m_prev = folium.Map(location=[-33.49, -70.74], zoom_start=12, tiles="CartoDB positron")
            for _, row in df.iterrows():
                cfg = COMUNA_CONFIG.get(row["Comuna"], {"color": "#3498db"})
                folium.CircleMarker(
                    [row["LAT"], row["LONG"]], radius=5,
                    color=cfg["color"], fill=True, fill_opacity=0.4,
                    tooltip=f"{row['RBD']} · {row['Establecimiento']}",
                ).add_to(m_prev)
            st_folium(m_prev, width="100%", height=500, returned_objects=[])

        else:
            # ── Parsear RBDs ─────────────────────────────────────────────────
            # Soporta: "9863", "9863 - Santiago Bueras", "9863,9864", etc.
            tokens = []
            for line in rbds_raw.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                # Extrae números de 4+ dígitos al inicio de la línea (antes del guión o nombre)
                m = re.match(r'^(\d{4,})', line)
                if m:
                    tokens.append(m.group(1))
                else:
                    # Fallback: busca números de 4+ dígitos en toda la línea
                    nums = re.findall(r'\b(\d{4,})\b', line)
                    tokens.extend(nums)

            found, not_found, seen = [], [], set()
            for tok in tokens:
                match = df[df["RBD"].astype(str) == tok]
                if match.empty:
                    try:
                        match = df[df["RBD"] == int(tok)]
                    except (ValueError, TypeError):
                        pass
                if not match.empty:
                    key = str(match.iloc[0]["RBD"])
                    if key not in seen:
                        found.append(match.iloc[0])
                        seen.add(key)
                else:
                    not_found.append(tok)

            if not_found:
                st.warning(f"⚠️ RBDs no encontrados en la base de datos: {', '.join(not_found)}")

            if len(found) < 2:
                st.error("Se necesitan al menos 2 establecimientos para optimizar una ruta.")
            else:
                school_df = pd.DataFrame(found).reset_index(drop=True)
                n_schools = len(school_df)

                if orig_tipo == "Centroide del grupo":
                    orig_lat = float(school_df["LAT"].mean())
                    orig_lon = float(school_df["LONG"].mean())
                else:
                    orig_lat, orig_lon = orig_lat_val, orig_lon_val

                # coords: index 0 = origen, 1..n = colegios
                coords = [(orig_lat, orig_lon)] + list(zip(school_df["LAT"], school_df["LONG"]))

                use_api = bool(api_key_in and _GMAPS_OK)

                with st.spinner("Calculando tiempos de viaje..."):
                    if use_api:
                        try:
                            _dist_mat, opt_mat = _gmaps_matrix(coords, api_key_in, gmode)
                            st.success("✅ Optimizando por tiempo real (Google Maps Distance Matrix API)")
                        except Exception as exc:
                            st.warning(f"Error con la API: {exc}. Se usará OSRM.")
                            opt_mat = _osrm_time_matrix(coords) or _haversine_matrix(coords)
                    else:
                        osrm_mat = _osrm_time_matrix(coords)
                        if osrm_mat is not None:
                            opt_mat = osrm_mat
                            st.caption("⏱️ Optimizando por tiempo real de conducción (OSRM)")
                        else:
                            opt_mat = _haversine_matrix(coords)
                            st.caption("📐 Optimizando por distancia en línea recta (sin conexión a OSRM)")

                with st.spinner("Optimizando ruta..."):
                    route = _nn_route(opt_mat)
                    if use_2opt:
                        if n_schools <= 25:
                            route = _two_opt(route, opt_mat)
                        else:
                            st.caption("ℹ️ 2-opt omitido (más de 25 paradas). Se usa el resultado del Vecino Más Cercano.")

                # Índices de colegios en school_df
                school_indices = [r - 1 for r in route[1:]]
                ordered = school_df.iloc[school_indices].reset_index(drop=True)

                route_coords = [(orig_lat, orig_lon)] + list(zip(ordered["LAT"], ordered["LONG"]))
                if round_trip:
                    route_coords.append((orig_lat, orig_lon))
                elif custom_end and end_lat_val is not None:
                    route_coords.append((end_lat_val, end_lon_val))

                total_km = sum(
                    _haversine(route_coords[i][0], route_coords[i][1],
                               route_coords[i + 1][0], route_coords[i + 1][1])
                    for i in range(len(route_coords) - 1)
                )

                # ── Mapa de ruta ─────────────────────────────────────────────
                mc = folium.Map(
                    location=[(orig_lat + float(ordered["LAT"].mean())) / 2,
                               (orig_lon + float(ordered["LONG"].mean())) / 2],
                    zoom_start=12, tiles="CartoDB positron", control_scale=True,
                )
                Fullscreen(position="topleft").add_to(mc)

                # Obtener ruta real por calles (OSRM, sin API key)
                with st.spinner("Trazando ruta por calles reales (OSRM)..."):
                    road_geom, osrm_km, osrm_min = _road_route(route_coords)
                    used_osrm = osrm_km is not None

                if used_osrm:
                    folium.PolyLine(
                        road_geom, color="#1a73e8", weight=4, opacity=0.78,
                    ).add_to(mc)
                else:
                    folium.PolyLine(
                        route_coords, color="#1a73e8", weight=2,
                        opacity=0.5, dash_array="6 5",
                    ).add_to(mc)
                    st.warning("No se pudo conectar a OSRM. Las líneas son de referencia (línea recta).")

                inicio_label = "🏠 Inicio / Fin" if round_trip else "🏠 Inicio"
                folium.Marker(
                    [orig_lat, orig_lon],
                    popup=inicio_label,
                    tooltip=inicio_label,
                    icon=folium.Icon(color="blue", icon="home", prefix="fa"),
                ).add_to(mc)

                total_stops = len(ordered)
                for i, (_, row) in enumerate(ordered.iterrows()):
                    cfg = COMUNA_CONFIG.get(row["Comuna"], {"color": "#3498db"})
                    is_last = (i == total_stops - 1)
                    stop_label = f"Parada #{i + 1}" + (" · ÚLTIMO" if is_last and not round_trip else "")
                    popup_html = (
                        f"<b>{stop_label}</b><br>"
                        f"<b>{row['Establecimiento']}</b><br>"
                        f"<small>📍 {row['Dirección']}<br>🔑 RBD: {row['RBD']}</small>"
                    )
                    marker_color = "#c0392b" if (is_last and not round_trip and not custom_end) else cfg["color"]
                    folium.Marker(
                        [row["LAT"], row["LONG"]],
                        popup=folium.Popup(popup_html, max_width=240),
                        tooltip=f"#{i + 1} · {row['Establecimiento']}",
                        icon=_num_icon(i + 1, marker_color),
                    ).add_to(mc)

                if custom_end and end_lat_val is not None:
                    folium.Marker(
                        [end_lat_val, end_lon_val],
                        popup="🏁 Punto de término",
                        tooltip="🏁 Fin",
                        icon=folium.Icon(color="red", icon="flag", prefix="fa"),
                    ).add_to(mc)

                st_folium(mc, width="100%", height=440, returned_objects=[])
                if used_osrm:
                    st.caption("✅ Ruta trazada por calles reales (OSRM). Google Maps usará sus propias calles al navegar.")
                else:
                    st.caption("ℹ️ Sin conexión a OSRM — líneas de referencia. Google Maps navegará por calles reales.")

                # ── Métricas ─────────────────────────────────────────────────
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Paradas", n_schools)
                with m2:
                    km_label = f"{osrm_km:.1f} km" if used_osrm else f"~{total_km:.1f} km"
                    st.metric("Distancia por calles", km_label)
                with m3:
                    if used_osrm:
                        h, m = divmod(int(osrm_min), 60)
                        dur_str = f"{h}h {m}min" if h else f"{m} min"
                    else:
                        dur_str = "—"
                    st.metric("Tiempo estimado", dur_str)
                with m4:
                    st.metric("Fuente distancias", "OSRM (calles)" if used_osrm else "Haversine (recta)")

                # ── Google Maps URLs ──────────────────────────────────────────
                gmaps_urls = _gmaps_urls(route_coords, gmode)
                st.markdown("**🗺️ Abrir en Google Maps**")
                if len(gmaps_urls) == 1:
                    st.link_button(
                        f"🗺️ Navegar ruta completa ({n_schools} paradas)",
                        gmaps_urls[0],
                        use_container_width=True,
                    )
                else:
                    chunk_size = 23
                    st.caption(
                        f"Ruta dividida en {len(gmaps_urls)} tramos "
                        f"(más de 25 paradas — límite de Google Maps). "
                        f"Abre cada tramo en orden."
                    )
                    cols_url = st.columns(len(gmaps_urls))
                    for idx, url in enumerate(gmaps_urls):
                        inicio = idx * chunk_size + 1
                        fin = min(inicio + chunk_size - 1, n_schools)
                        with cols_url[idx]:
                            st.link_button(
                                f"Tramo {idx + 1}  (paradas {inicio}–{fin})",
                                url, use_container_width=True,
                            )

                # ── Tabla de orden ────────────────────────────────────────────
                with st.expander("📋 Ver orden completo de visitas", expanded=True):
                    disp = ordered[["RBD", "Establecimiento", "Comuna", "Dirección"]].copy()
                    disp.insert(0, "#", range(1, len(disp) + 1))
                    st.dataframe(disp, use_container_width=True, hide_index=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center;color:#94a3b8;font-size:.78rem;margin-top:1rem;'>"
    "SLEP Santa Corina · Departamento de Monitoreo y Seguimiento (JISC) · 2025</div>",
    unsafe_allow_html=True,
)
