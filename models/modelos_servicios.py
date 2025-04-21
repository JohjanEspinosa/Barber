import streamlit as st
from database import session, Servicio  # Importar desde database.py
import pandas as pd  # Importar pandas para crear una tabla más estilizada

# Pantalla de Gestión de Servicios
def gestionar_servicios():
    st.header("Gestión de Servicios")

    # Mostrar formulario para agregar un nuevo servicio
    st.subheader("Agregar Nuevo Servicio")

    # Inicializar los campos si no existen en session_state
    if "nombre_servicio" not in st.session_state:
        st.session_state["nombre_servicio"] = ""
    if "precio_servicio" not in st.session_state:
        st.session_state["precio_servicio"] = 1000  # Asegurarse de que el valor predeterminado sea >= 1000

    # Mostrar el formulario
    nombre = st.text_input("Nombre del Servicio", value=st.session_state["nombre_servicio"])
    precio = st.number_input("Precio del Servicio", min_value=1000, step=1000, value=st.session_state["precio_servicio"])
    
    if st.button("Agregar Servicio"):
        if nombre and precio > 0:
            nuevo_servicio = Servicio(nombre=nombre, precio=precio)
            session.add(nuevo_servicio)
            session.commit()

            # Limpiar los campos del formulario
            st.session_state["nombre_servicio"] = ""
            st.session_state["precio_servicio"] = 1000  # Restablecer a 1000

            st.success("Servicio agregado exitosamente")
            st.balloons()  # Mostrar un efecto de confeti para mayor interacción
        else:
            st.error("Por favor, ingresa el nombre y el precio del servicio")

    # Mostrar lista de servicios en una tabla
    st.subheader("Servicios Registrados")
    servicios = session.query(Servicio).all()

    # Si hay servicios, mostrar en una tabla con nombres de columnas
    if servicios:
        # Crear un DataFrame de pandas para estructurar los datos
        servicio_data = {
            "ID": [servicio.id for servicio in servicios],  # Solo usamos el ID real de la base de datos
            "Nombre": [servicio.nombre for servicio in servicios],
            "Precio (COP)": [f"${servicio.precio:,.0f}" for servicio in servicios]
        }
        df_servicios = pd.DataFrame(servicio_data)

        # Mostrar la tabla sin el índice de Pandas
        st.table(df_servicios.set_index('ID'))  # Establecer el 'ID' como índice para que no aparezca un índice extra
        
        # Agregar un poco de color y estilo usando st.markdown
        st.markdown("""
            <style>
            .streamlit-expanderHeader {
                background-color: #f2f2f2;
            }
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
        st.write("No hay servicios registrados.")