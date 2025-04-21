import streamlit as st
from database import session, Cliente, Servicio, Venta
import pandas as pd
import pytz
from datetime import datetime, time
from io import BytesIO

def mostrar_resumen_ventas(fecha_inicio, fecha_fin):
    # Filtro las ventas por las fechas proporcionadas
    query = session.query(Venta)

    if fecha_inicio and fecha_fin:
        query = query.filter(Venta.fecha_venta >= datetime.combine(fecha_inicio, time.min))
        query = query.filter(Venta.fecha_venta <= datetime.combine(fecha_fin, time.max))

    ventas = query.all()

    if ventas:
        # Calculando los datos del resumen
        precios = [venta.precio_servicio if venta.precio_servicio else 0 for venta in ventas]
        total_ventas = sum(precios)
        servicio_ids = [venta.servicio_id for venta in ventas]
        servicio_mas_vendido_id = max(set(servicio_ids), key=servicio_ids.count) if servicio_ids else None
        servicio_nombre = session.query(Servicio).filter_by(id=servicio_mas_vendido_id).first().nombre if servicio_mas_vendido_id else "N/A"

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Total Ventas", value=f"${total_ventas:,.2f}")
        with col2:
            st.metric(label="Servicio Más Vendido", value=servicio_nombre)
    else:
        st.write("No hay ventas registradas en el rango de fechas seleccionado.")

def gestionar_ventas():
    st.markdown(
        """
        <style>
        .st-header {
            padding-bottom: 1rem;
            border-bottom: 1px solid #eee;
            margin-bottom: 1.5rem;
        }
        .st-subheader {
            color: #555;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid #eee;
            padding-bottom: 0.5rem;
        }
        .st-selectbox label,
        .st-number-input label,
        .st-text-input label,
        .st-date-input label {
            color: #333;
        }
        .stButton>button {
            background-color: #007bff !important;
            color: white !important;
            border: none !important;
            border-radius: 5px !important;
            padding: 0.5rem 1rem !important;
            font-size: 1rem !important;
            cursor: pointer !important;
        }
        .stButton>button:hover {
            background-color: #0056b3 !important;
        }
        .stSuccess {
            color: green;
            margin-top: 1rem;
        }
        .stError {
            color: red;
            margin-top: 1rem;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #777;
        }
        .metric-value {
            font-size: 1.2rem;
            font-weight: bold;
        }
        .stTable {
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
            margin-top: 1rem;
        }
        .stTable table {
            width: 100%;
            border-collapse: collapse;
        }
        .stTable th, .stTable td {
            border: 1px solid #ddd;
            padding: 0.5rem;
            text-align: left;
        }
        .stDownloadButton>button {
            background-color: #28a745 !important;
        }
        .stDownloadButton>button:hover {
            background-color: #1e7e34 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.header("Gestión de Ventas")

    # --- Búsqueda de Clientes Mejorada ---
    st.subheader("Registrar Venta")
    clientes = session.query(Cliente).all()
    nombres_documentos_clientes = [f"{cliente.nombre} (Doc: {cliente.documento})" for cliente in clientes]
    cliente_seleccionado = st.selectbox("Selecciona Cliente", [""] + nombres_documentos_clientes) # Añade una opción vacía inicial

    servicio_id = st.selectbox("Selecciona Servicio", [servicio.nombre for servicio in session.query(Servicio).all()])

    if st.button("Registrar Venta"):
        if not cliente_seleccionado:
            st.error("Por favor, selecciona un cliente.")
        elif not servicio_id:
            st.error("Por favor, selecciona un servicio.")
        else:
            cliente_nombre = cliente_seleccionado.split(" (Doc:")[0]
            cliente = session.query(Cliente).filter_by(nombre=cliente_nombre).first()
            servicio = session.query(Servicio).filter_by(nombre=servicio_id).first()

            if cliente and servicio:
                zona_horaria_colombia = pytz.timezone('America/Bogota')
                fecha_actual_colombia = datetime.now(zona_horaria_colombia)
                nueva_venta = Venta(
                    cliente_id=cliente.id,
                    servicio_id=servicio.id,
                    fecha_venta=fecha_actual_colombia,
                    precio_servicio=servicio.precio
                )
                session.add(nueva_venta)
                session.commit()
                st.success(f"Venta registrada para {cliente.nombre} ({servicio.nombre})")
                st.balloons()
            else:
                st.error("Error al encontrar cliente o servicio.")

    # --- Filtros de Ventas ---
    st.subheader("Filtrar Ventas")
    col1, col2 = st.columns([2, 1])
    with col1:
        fecha_inicio = st.date_input("Desde", datetime.today())
        fecha_fin = st.date_input("Hasta", datetime.today())

    # Ya no necesitamos el filtro de búsqueda de cliente aquí, la selección se hizo al registrar la venta

# --- Ventas Realizadas ---
    st.subheader("Ventas Realizadas")
    query_ventas = session.query(Venta)
    if fecha_inicio and fecha_fin:
        query_ventas = query_ventas.filter(Venta.fecha_venta >= datetime.combine(fecha_inicio, time.min))
        query_ventas = query_ventas.filter(Venta.fecha_venta <= datetime.combine(fecha_fin, time.max))
    ventas_totales = query_ventas.count()

    items_por_pagina = 10
    num_paginas = (ventas_totales + items_por_pagina - 1) // items_por_pagina

    if "pagina_actual_ventas" not in st.session_state:
        st.session_state["pagina_actual_ventas"] = 1

    def siguiente_pagina():
        if st.session_state["pagina_actual_ventas"] < num_paginas:
            st.session_state["pagina_actual_ventas"] += 1
            st.rerun() # Importante para actualizar la vista

    def pagina_anterior():
        if st.session_state["pagina_actual_ventas"] > 1:
            st.session_state["pagina_actual_ventas"] -= 1
            st.rerun() # Importante para actualizar la vista

    start_index = (st.session_state["pagina_actual_ventas"] - 1) * items_por_pagina
    end_index = start_index + items_por_pagina
    ventas_pagina = query_ventas.offset(start_index).limit(items_por_pagina).all() # Obtener solo la página actual desde la DB

    if ventas_pagina:
        venta_data = {
            "ID": [venta.id for venta in ventas_pagina],
            "Cliente": [session.query(Cliente).filter_by(id=venta.cliente_id).first().nombre for venta in ventas_pagina],
            "Servicio": [session.query(Servicio).filter_by(id=venta.servicio_id).first().nombre for venta in ventas_pagina],
            "Fecha": [venta.fecha_venta.strftime("%Y-%m-%d %H:%M:%S") for venta in ventas_pagina],
            "Precio (COP)": [
                f"${venta.precio_servicio:,.2f}".rstrip('0').rstrip('.') if venta.precio_servicio is not None else "N/A"
                for venta in ventas_pagina
            ]
        }
        df_ventas = pd.DataFrame(venta_data)
        st.table(df_ventas.set_index('ID'))

        col_paginacion = st.columns([1, 3, 1])
        with col_paginacion[0]:
            st.button("Anterior", on_click=pagina_anterior, disabled=st.session_state["pagina_actual_ventas"] == 1)
        with col_paginacion[1]:
            st.write(f"Página {st.session_state['pagina_actual_ventas']} de {num_paginas}")
        with col_paginacion[2]:
            st.button("Siguiente", on_click=siguiente_pagina, disabled=st.session_state["pagina_actual_ventas"] == num_paginas)

        # Generar Excel (basado en todas las ventas filtradas)
        ventas_excel = query_ventas.all()
        venta_data_excel = {
            "ID": [venta.id for venta in ventas_excel],
            "Cliente": [session.query(Cliente).filter_by(id=venta.cliente_id).first().nombre for venta in ventas_excel],
            "Servicio": [session.query(Servicio).filter_by(id=venta.servicio_id).first().nombre for venta in ventas_excel],
            "Fecha": [venta.fecha_venta.strftime("%Y-%m-%d %H:%M:%S") for venta in ventas_excel],
            "Precio (COP)": [
                f"${venta.precio_servicio:,.2f}".rstrip('0').rstrip('.') if venta.precio_servicio is not None else "N/A"
                for venta in ventas_excel
            ]
        }
        df_ventas_excel = pd.DataFrame(venta_data_excel)
        excel_file = BytesIO()
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df_ventas_excel.to_excel(writer, index=False, sheet_name="Ventas")
        excel_file.seek(0)

        st.download_button(
            label="Descargar Reporte en Excel",
            data=excel_file,
            file_name="ventas_reporte.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.write("No hay ventas en las fechas seleccionadas.")