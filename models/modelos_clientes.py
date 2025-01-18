import streamlit as st
from database import session, Cliente  # Importar desde database.py
import pandas as pd  # Importar pandas para crear una tabla más estilizada

# Pantalla de Gestión de Clientes
# En tu archivo gestionar_clientes.py (pantalla de clientes)
def gestionar_clientes():
    st.header("Gestión de Clientes")

    # Mostrar formulario para agregar un nuevo cliente
    st.subheader("Agregar Nuevo Cliente")

    # Inicializar los campos si no existen en session_state
    if "nombre" not in st.session_state:
        st.session_state["nombre"] = ""
    if "telefono" not in st.session_state:
        st.session_state["telefono"] = ""
    if "documento" not in st.session_state:
        st.session_state["documento"] = ""

    # Mostrar el formulario
    nombre = st.text_input("Nombre del Cliente", value=st.session_state["nombre"])
    telefono = st.text_input("Teléfono del Cliente", value=st.session_state["telefono"])
    documento = st.text_input("Documento del Cliente", value=st.session_state["documento"])

    # Verificar si el documento ya existe en la base de datos
    if st.button("Agregar Cliente"):
        if nombre and telefono and documento:
            # Verificar si el documento ya existe en la base de datos
            cliente_existente = session.query(Cliente).filter_by(documento=documento).first()
            
            if cliente_existente:
                st.error("Ya existe un cliente con este documento.")
            else:
                nuevo_cliente = Cliente(nombre=nombre, telefono=telefono, documento=documento)
                session.add(nuevo_cliente)
                session.commit()

                # Limpiar los campos del formulario
                st.session_state["nombre"] = ""
                st.session_state["telefono"] = ""
                st.session_state["documento"] = ""

                st.success("Cliente agregado exitosamente")
        else:
            st.error("Por favor, ingresa el nombre, teléfono y documento del cliente")

    # Mostrar lista de clientes en una tabla
    st.subheader("Clientes Registrados")
    clientes = session.query(Cliente).all()

    # Si hay clientes, mostrar en una tabla con nombres de columnas
    if clientes:
        cliente_data = {
            "ID": [cliente.id for cliente in clientes],
            "Nombre": [cliente.nombre for cliente in clientes],
            "Teléfono": [cliente.telefono for cliente in clientes],
            "Documento": [cliente.documento for cliente in clientes]  # Mostrar también el documento
        }
        df_clientes = pd.DataFrame(cliente_data)
        st.table(df_clientes.set_index('ID'))  # Establecer el 'ID' como índice para que no aparezca un índice extra

        # Estilo con Markdown (opcional)
        st.markdown("""
            <style>
            .stButton>button {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                border-radius: 5px;
                padding: 10px;
            }
            .stTable {
                border: 1px solid #ddd;
                border-radius: 5px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }
            </style>
            """, unsafe_allow_html=True)
    else:
        st.write("No hay clientes registrados.")
