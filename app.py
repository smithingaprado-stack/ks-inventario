import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN DE SEGURIDAD ---
PASSWORD_CORRECTA = "KS2026"

st.set_page_config(page_title="KS Management Pro", layout="wide")

def verificar_password():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
    
    if not st.session_state["autenticado"]:
        st.title("🔒 Acceso Restringido - KS")
        password = st.text_input("Introduce la contraseña para ingresar:", type="password")
        if st.button("Ingresar"):
            if password == PASSWORD_CORRECTA:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta.")
        return False
    return True

if verificar_password():
    st.title("👕 KS Streetwear - Gestión Total")
    archivo = "Inventario_Tienda.xlsx"

    # Cargar base de datos
    if os.path.exists(archivo):
        df = pd.read_excel(archivo)
    else:
        df = pd.DataFrame(columns=['CODIGO', 'PRODUCTO', 'STOCK', 'PRECIO_S/', 'FOTO'])

    # --- MENÚ LATERAL ---
    st.sidebar.header("Menú Principal")
    opcion = st.sidebar.selectbox("Ir a:", ["🖼️ Vitrina y Ventas", "📊 Inventario y Reportes", "➕ Añadir Nueva Prenda"])

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()

    # --- 1. VITRINA Y VENTAS (CON EDICIÓN RÁPIDA) ---
    if opcion == "🖼️ Vitrina y Ventas":
        st.subheader("Buscador de Prendas")
        busqueda = st.text_input("🔍 Escribe el nombre o código").lower()
        df_filtrado = df[df['PRODUCTO'].str.lower().str.contains(busqueda) | df['CODIGO'].astype(str).str.contains(busqueda)]
        
        cols = st.columns(3)
        for index, row in df_filtrado.iterrows():
            with cols[index % 3]:
                st.markdown(f"### {row['PRODUCTO']}")
                r_foto = f"fotos/{row['FOTO']}"
                if os.path.exists(r_foto):
                    st.image(r_foto, use_container_width=True)
                else:
                    st.info("Sin imagen")
                
                st.write(f"**Código:** {row['CODIGO']}")
                st.write(f"**Precio:** S/. {row['PRECIO_S/']}")
                
                # Indicador de Stock
                stock_actual = int(row['STOCK'])
                if stock_actual <= 3:
                    st.error(f"⚠️ STOCK BAJO: {stock_actual}")
                else:
                    st.success(f"Stock disponible: {stock_actual}")

                # BOTÓN VENDER
                if st.button(f"🛒 Vender (-1)", key=f"v_{row['CODIGO']}"):
                    if stock_actual > 0:
                        df.at[index, 'STOCK'] = stock_actual - 1
                        df.to_excel(archivo, index=False)
                        st.rerun()

                # SECCIÓN EDITAR (Expander para no ocupar espacio)
                with st.expander("📝 Editar Producto"):
                    nuevo_nom = st.text_input("Nuevo Nombre", value=row['PRODUCTO'], key=f"n_{row['CODIGO']}")
                    nuevo_stk = st.number_input("Modificar Stock", value=stock_actual, key=f"s_{row['CODIGO']}")
                    if st.button("Guardar Cambios", key=f"g_{row['CODIGO']}"):
                        df.at[index, 'PRODUCTO'] = nuevo_nom
                        df.at[index, 'STOCK'] = nuevo_stk
                        df.to_excel(archivo, index=False)
                        st.success("¡Actualizado!")
                        st.rerun()
                st.divider()

    # --- 2. REPORTES ---
    elif opcion == "📊 Inventario y Reportes":
        st.header("Reporte Administrativo")
        st.dataframe(df, use_container_width=True)
        st.metric("Total Prendas en Almacén", int(df['STOCK'].sum()))

    # --- 3. AÑADIR NUEVO ---
    else:
        st.header("Añadir Nueva Prenda al Sistema")
        with st.form("reg_form", clear_on_submit=True):
            f_cod = st.text_input("Código Único")
            f_nom = st.text_input("Nombre del Producto")
            f_stk = st.number_input("Stock Inicial", min_value=0)
            f_pre = st.number_input("Precio de Venta S/.", min_value=0.0)
            f_foto = st.file_uploader("Subir Imagen", type=['jpg', 'png', 'jpeg'])
            
            if st.form_submit_button("Guardar en Inventario"):
                nombre_f = f"{f_cod}.jpg" if f_foto else "no_foto.jpg"
                if f_foto:
                    if not os.path.exists("fotos"):
                        os.makedirs("fotos")
                    with open(f"fotos/{nombre_f}", "wb") as f:
                        f.write(f_foto.getbuffer())
                
                nueva_prenda = pd.DataFrame({
                    'CODIGO': [f_cod], 'PRODUCTO': [f_nom], 
                    'STOCK': [f_stk], 'PRECIO_S/': [f_pre], 'FOTO': [nombre_f]
                })
                df = pd.concat([df, nueva_prenda], ignore_index=True).drop_duplicates('CODIGO', keep='last')
                df.to_excel(archivo, index=False)
                st.success("¡Producto registrado con éxito!")
