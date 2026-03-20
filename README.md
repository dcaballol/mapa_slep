# 🏫 Mapa Establecimientos SLEP Santa Corina

Aplicación interactiva para visualizar los 91 establecimientos educacionales del SLEP Santa Corina en las comunas de Estación Central, Cerrillos y Maipú.

## 🚀 Despliegue en Streamlit Cloud (gratis)

### Paso 1 — Subir a GitHub
1. Crea un repositorio en GitHub (puede ser privado)
2. Sube los dos archivos: `app.py` y `requirements.txt`

### Paso 2 — Conectar con Streamlit Cloud
1. Ve a [share.streamlit.io](https://share.streamlit.io) e inicia sesión con GitHub
2. Click en **"New app"**
3. Selecciona tu repositorio y rama (`main`)
4. En **Main file path** escribe: `app.py`
5. Click en **"Deploy!"** → listo en ~2 minutos ✅

## 🖥️ Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## ✨ Funcionalidades

- Mapa interactivo con marcadores por establecimiento
- Colores diferenciados por comuna (rojo / naranja / verde)
- Agrupación de marcadores (cluster) activable/desactivable
- Popup con nombre, dirección, RBD y coordenadas
- Filtro por comuna y búsqueda por nombre
- Métricas por comuna
- Tabla de datos desplegable
- Capas de mapa: claro, OpenStreetMap, modo oscuro
- Pantalla completa

## 📊 Datos

91 establecimientos:
- 🔴 Estación Central: 26
- 🟠 Cerrillos: 18  
- 🟢 Maipú: 47
