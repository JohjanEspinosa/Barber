import streamlit as st
from database import session, Cliente, Servicio, Venta
import pandas as pd
import pytz
from datetime import datetime
from io import BytesIO

# Estilos para un diseño minimalista

# Función para mostrar el resumen de ventas
def mostrar_resumen_ventas(fecha_inicio, fecha_fin):
    # Filtro las ventas por las fechas proporcionadas
    query = session.query(Venta)

    if fecha_inicio and fecha_fin:
        query = query.filter(Venta.fecha_venta >= datetime.combine(fecha_inicio, datetime.min.time()))
        query = query.filter(Venta.fecha_venta <= datetime.combine(fecha_fin, datetime.max.time()))

    ventas = query.all()

    if ventas:
        # Calculando los datos del resumen
        precios = [venta.precio_servicio if venta.precio_servicio else 0 for venta in ventas]
        total_ventas = sum(precios)
        servicio_mas_vendido = max(set([venta.servicio_id for venta in ventas]), key=[venta.servicio_id for venta in ventas].count)

        servicio_nombre = session.query(Servicio).filter_by(id=servicio_mas_vendido).first().nombre if servicio_mas_vendido else "N/A"
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Total Ventas", value=f"${total_ventas:,.2f}")
        with col2:
            st.metric(label="Servicio Más Vendido", value=servicio_nombre)
    else:
        st.write("No hay ventas registradas en el rango de fechas seleccionado.")

# Función para gestionar ventas
def gestionar_ventas():
    st.header("Gestión de Ventas")

    # Aplico el CSS personalizado


    # Filtros de ventas (fecha y cliente)
    st.markdown('<div class="filtros">', unsafe_allow_html=True)
    st.subheader("Filtrar Ventas")
    col1, col2 = st.columns([2, 1])

    with col1:
        fecha_inicio = st.date_input("Desde", datetime.today())
        fecha_fin = st.date_input("Hasta", datetime.today())

    with col2:
        busqueda_cliente = st.text_input("Buscar Cliente")

    st.markdown('</div>', unsafe_allow_html=True)

    # Mostrar el resumen de ventas para el rango de fechas seleccionado
    st.markdown('<div class="resumen">', unsafe_allow_html=True)
    mostrar_resumen_ventas(fecha_inicio, fecha_fin)
    st.markdown('</div>', unsafe_allow_html=True)

    # Formulario para registrar una nueva venta
    st.subheader("Registrar Venta")

    # Obtener clientes y servicios
    clientes = session.query(Cliente).all()
    servicios = session.query(Servicio).all()

    clientes_filtrados = [cliente for cliente in clientes if busqueda_cliente.lower() in cliente.nombre.lower() or busqueda_cliente in cliente.documento]

    if clientes_filtrados:
        cliente_id = st.selectbox("Selecciona Cliente", [cliente.nombre for cliente in clientes_filtrados])
    else:
        st.write("No se encontraron clientes.")
        cliente_id = None

    servicio_id = st.selectbox("Selecciona Servicio", [servicio.nombre for servicio in servicios])

    if st.button("Registrar Venta"):
        cliente = session.query(Cliente).filter_by(nombre=cliente_id).first()
        servicio = session.query(Servicio).filter_by(nombre=servicio_id).first()

        if cliente and servicio:
            # Registrar la venta
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
            
            # Recargar el total de ventas actualizado después de registrar la venta
            mostrar_resumen_ventas(fecha_inicio, fecha_fin)

            st.success("Venta registrada")
            st.balloons()

        else:
            st.error("Selecciona un cliente y un servicio válidos")

    # Mostrar ventas filtradas por fecha
    st.subheader("Ventas Realizadas")

    query = session.query(Venta)

    if fecha_inicio and fecha_fin:
        query = query.filter(Venta.fecha_venta >= datetime.combine(fecha_inicio, datetime.min.time()))
        query = query.filter(Venta.fecha_venta <= datetime.combine(fecha_fin, datetime.max.time()))

    ventas = query.all()

    if ventas:
        # Crear DataFrame para mostrar las ventas
        venta_data = {
            "ID": [venta.id for venta in ventas],
            "Cliente": [session.query(Cliente).filter_by(id=venta.cliente_id).first().nombre for venta in ventas],
            "Servicio": [session.query(Servicio).filter_by(id=venta.servicio_id).first().nombre for venta in ventas],
            "Fecha": [venta.fecha_venta.strftime("%Y-%m-%d %H:%M:%S") for venta in ventas],
            "Precio (COP)": [
                f"${venta.precio_servicio:,.2f}".rstrip('0').rstrip('.') if venta.precio_servicio is not None else "N/A"
                for venta in ventas
            ]
        }

        df_ventas = pd.DataFrame(venta_data)

        # Mostrar la tabla de ventas
        st.table(df_ventas.set_index('ID'))

        # Generar Excel
        excel_file = BytesIO()
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df_ventas.to_excel(writer, index=False, sheet_name="Ventas")
        excel_file.seek(0)

        # Botón para descarga
        st.download_button(
            label="Descargar Reporte en Excel",
            data=excel_file,
            file_name="ventas_reporte.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.write("No hay ventas en las fechas seleccionadas.")

# Ejecutar la función de gestionar ventas
if __name__ == "__main__":
    gestionar_ventas()
