import streamlit as st
import folium
from folium.plugins import MarkerCluster, Fullscreen
from streamlit_folium import st_folium
import pandas as pd

# ── Configuración de página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mapa Establecimientos SLEP Santa Corina",
    page_icon="🏫",
    layout="wide",
)

# ── Estilos CSS personalizados ─────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #f5f7fa; }
  .header-banner {
    background: linear-gradient(135deg, #1a3a5c 0%, #2563a8 100%);
    padding: 1.2rem 1.8rem;
    border-radius: 12px;
    color: white;
    margin-bottom: 1.2rem;
  }
  .header-banner h1 { margin: 0; font-size: 1.6rem; font-weight: 700; }
  .header-banner p  { margin: 0.3rem 0 0; font-size: 0.9rem; opacity: 0.85; }
  .metric-card {
    background: white;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }
  .metric-num  { font-size: 2rem; font-weight: 700; color: #2563a8; }
  .metric-label{ font-size: 0.78rem; color: #64748b; text-transform: uppercase; letter-spacing: .05em; }
  .stSelectbox label { font-weight: 600; }
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

# ── Colores y emojis por comuna ────────────────────────────────────────────────
COMUNA_CONFIG = {
    "ESTACIÓN CENTRAL": {"color": "#e74c3c", "folium_color": "red",    "emoji": "🔴"},
    "CERRILLOS":        {"color": "#f39c12", "folium_color": "orange",  "emoji": "🟠"},
    "MAIPÚ":            {"color": "#27ae60", "folium_color": "green",   "emoji": "🟢"},
}

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
  <h1>🏫 Mapa de Establecimientos — SLEP Santa Corina</h1>
  <p>Visualización georreferenciada · Comunas de Estación Central, Cerrillos y Maipú · Región Metropolitana</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar: filtros ───────────────────────────────────────────────────────────
with st.sidebar:
    #st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Flag_of_Chile.svg/60px-Flag_of_Chile.svg.png", width=40)
    st.markdown("### 🔍 Filtros")
    comunas_disp = sorted(df["Comuna"].unique())
    comunas_sel = st.multiselect(
        "Comunas",
        options=comunas_disp,
        default=comunas_disp,
        format_func=lambda c: f"{COMUNA_CONFIG[c]['emoji']} {c.title()}"
    )
    busqueda = st.text_input("🔎 Buscar establecimiento", placeholder="Nombre o dirección...")
    cluster_on = st.toggle("Agrupar marcadores (Cluster)", value=True)
    st.markdown("---")
    st.markdown("#### 🎨 Leyenda")
    for c, cfg in COMUNA_CONFIG.items():
        st.markdown(f"{cfg['emoji']} **{c.title()}**")

# ── Filtrado ───────────────────────────────────────────────────────────────────
dff = df[df["Comuna"].isin(comunas_sel)].copy()
if busqueda:
    mask = (
        dff["Establecimiento"].str.contains(busqueda, case=False, na=False) |
        dff["Dirección"].str.contains(busqueda, case=False, na=False)
    )
    dff = dff[mask]

# ── Métricas ───────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
totales = {c: len(df[df["Comuna"]==c]) for c in comunas_disp}
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-num">{len(dff)}</div><div class="metric-label">Establecimientos visibles</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#e74c3c">{totales["ESTACIÓN CENTRAL"]}</div><div class="metric-label">🔴 Estación Central</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#f39c12">{totales["CERRILLOS"]}</div><div class="metric-label">🟠 Cerrillos</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#27ae60">{totales["MAIPÚ"]}</div><div class="metric-label">🟢 Maipú</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Mapa Folium ────────────────────────────────────────────────────────────────
centro_lat = dff["LAT"].mean() if len(dff) > 0 else -33.50
centro_lon = dff["LONG"].mean() if len(dff) > 0 else -70.75

m = folium.Map(
    location=[centro_lat, centro_lon],
    zoom_start=12,
    tiles="CartoDB positron",
    control_scale=True,
)

# Capas de tiles adicionales
folium.TileLayer("OpenStreetMap",    name="OpenStreetMap").add_to(m)
folium.TileLayer("CartoDB dark_matter", name="Modo oscuro").add_to(m)
folium.LayerControl(position="topright").add_to(m)
Fullscreen(position="topleft").add_to(m)

# Capas por comuna
layers = {}
for c in comunas_disp:
    fg = folium.FeatureGroup(name=f"{COMUNA_CONFIG[c]['emoji']} {c.title()}", show=(c in comunas_sel))
    layers[c] = fg

# Marcadores
group = MarkerCluster(name="Agrupados", show=cluster_on).add_to(m) if cluster_on else m

for _, row in dff.iterrows():
    cfg = COMUNA_CONFIG.get(row["Comuna"], {"folium_color":"blue","emoji":"🔵","color":"#3498db"})
    popup_html = f"""
    <div style="font-family:Arial,sans-serif;min-width:230px;max-width:280px;">
      <div style="background:{cfg['color']};color:white;padding:8px 12px;border-radius:6px 6px 0 0;font-weight:700;font-size:13px;">
        {cfg['emoji']} {row['Establecimiento']}
      </div>
      <div style="padding:10px 12px;background:#fff;border-radius:0 0 6px 6px;border:1px solid #e2e8f0;">
        <p style="margin:4px 0;font-size:12px;"><b>📍 Dirección:</b> {row['Dirección']}</p>
        <p style="margin:4px 0;font-size:12px;"><b>🏘️ Comuna:</b> {row['Comuna'].title()}</p>
        <p style="margin:4px 0;font-size:12px;"><b>🔑 RBD/Cód.:</b> {row['RBD']}</p>
        <p style="margin:4px 0;font-size:11px;color:#64748b;">
          📌 {row['LAT']:.6f}, {row['LONG']:.6f}
        </p>
      </div>
    </div>
    """
    tooltip = f"{cfg['emoji']} {row['Establecimiento']}"
    marker = folium.Marker(
        location=[row["LAT"], row["LONG"]],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=tooltip,
        icon=folium.Icon(color=cfg["folium_color"], icon="graduation-cap", prefix="fa"),
    )
    marker.add_to(group if cluster_on else m)

# Renderizar mapa
map_data = st_folium(m, width="100%", height=580, returned_objects=["last_object_clicked"])

# ── Detalle del marcador clickeado ─────────────────────────────────────────────
if map_data and map_data.get("last_object_clicked"):
    clicked = map_data["last_object_clicked"]
    lat_c, lon_c = clicked.get("lat"), clicked.get("lng")
    if lat_c and lon_c:
        match = dff[(abs(dff["LAT"]-lat_c)<0.0005) & (abs(dff["LONG"]-lon_c)<0.0005)]
        if not match.empty:
            r = match.iloc[0]
            cfg = COMUNA_CONFIG.get(r["Comuna"], {"color":"#3498db","emoji":"🔵"})
            st.markdown(f"""
            <div style="background:white;border-left:5px solid {cfg['color']};
                        padding:1rem 1.4rem;border-radius:8px;margin-top:.5rem;
                        box-shadow:0 2px 8px rgba(0,0,0,.08);">
              <h4 style="margin:0 0 .4rem;color:{cfg['color']};">{cfg['emoji']} {r['Establecimiento']}</h4>
              <p style="margin:.2rem 0;font-size:.9rem;">📍 {r['Dirección']}</p>
              <p style="margin:.2rem 0;font-size:.9rem;">🏘️ {r['Comuna'].title()} &nbsp;|&nbsp; 🔑 RBD: {r['RBD']}</p>
            </div>
            """, unsafe_allow_html=True)

# ── Tabla de datos ─────────────────────────────────────────────────────────────
with st.expander("📋 Ver listado completo de establecimientos", expanded=False):
    st.dataframe(
        dff[["RBD","Establecimiento","Comuna","Dirección"]].rename(columns={
            "RBD":"RBD / Cód. JUNJI",
            "Establecimiento":"Nombre",
            "Dirección":"Dirección",
        }),
        use_container_width=True,
        hide_index=True,
    )

st.markdown(
    "<div style='text-align:center;color:#94a3b8;font-size:.78rem;margin-top:1rem;'>"
    "SLEP Santa Corina · Departamento de Monitoreo y Seguimiento · 2026</div>",
    unsafe_allow_html=True
)
