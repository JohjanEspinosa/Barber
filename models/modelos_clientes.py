import streamlit as st
from database import session, Cliente  # Importar desde database.py
import pandas as pd  # Importar pandas para crear una tabla más estilizada

def gestionar_clientes():
    st.header("Gestión de Clientes")
    st.write("Aquí puedes administrar la información de tus clientes.")

    # --- Ver Clientes ---
    with st.expander("Ver Clientes"):
        clientes = session.query(Cliente).all()
        if clientes:
            cliente_data = {
                "ID": [cliente.id for cliente in clientes],
                "Nombre": [cliente.nombre for cliente in clientes],
                "Teléfono": [cliente.telefono for cliente in clientes],
                "Documento": [cliente.documento for cliente in clientes]
            }
            df_clientes = pd.DataFrame(cliente_data)
            st.table(df_clientes.set_index('ID'))
        else:
            st.info("No hay clientes registrados.")

    # --- Crear Nuevo Cliente ---
    with st.expander("Crear Nuevo Cliente"):
        nombre = st.text_input("Nombre del Cliente:")
        telefono = st.text_input("Teléfono del Cliente:")
        documento = st.text_input("Documento del Cliente:")
        if st.button("Guardar Nuevo Cliente"):
            if nombre and telefono and documento:
                # Verificar si el documento ya existe
                cliente_existente = session.query(Cliente).filter_by(documento=documento).first()
                if cliente_existente:
                    st.error("Ya existe un cliente con este documento.")
                else:
                    nuevo_cliente = Cliente(nombre=nombre, telefono=telefono, documento=documento)
                    session.add(nuevo_cliente)
                    session.commit()
                    st.success(f"Cliente '{nombre}' creado exitosamente.")
                    # Opcional: Limpiar los campos después de la creación
                    st.empty() # Esto puede limpiar el expander o puedes usar st.session_state
            else:
                st.error("Por favor, completa todos los campos.")
        # Aquí puedes agregar el código para crear un nuevo cliente
        pass

    # --- Editar Cliente ---
    with st.expander("Editar Cliente"):
        clientes_editar = session.query(Cliente).all()
        if not clientes_editar:
            st.info("No hay clientes para editar.")
        else:
            nombre_cliente_editar = st.selectbox(
                "Selecciona el cliente a editar:",
                [cliente.nombre for cliente in clientes_editar]
            )
            cliente_a_editar = next(
                (cliente for cliente in clientes_editar if cliente.nombre == nombre_cliente_editar),
                None,
            )

            if cliente_a_editar:
                with st.form(key=f"editar_cliente_{cliente_a_editar.id}"):
                    nuevo_nombre = st.text_input("Nuevo Nombre:", value=cliente_a_editar.nombre)
                    nuevo_telefono = st.text_input("Nuevo Teléfono:", value=cliente_a_editar.telefono)
                    nuevo_documento = st.text_input("Nuevo Documento:", value=cliente_a_editar.documento)
                    guardar_cambios = st.form_submit_button("Guardar Cambios")

                    if guardar_cambios:
                        cliente_existente_doc = session.query(Cliente).filter(
                            Cliente.documento == nuevo_documento, Cliente.id != cliente_a_editar.id
                        ).first()
                        if cliente_existente_doc:
                            st.error("Ya existe un cliente con este documento.")
                        else:
                            cliente_a_editar.nombre = nuevo_nombre
                            cliente_a_editar.telefono = nuevo_telefono
                            cliente_a_editar.documento = nuevo_documento
                            session.commit()
                            st.success(f"Cliente '{nuevo_nombre}' actualizado.")

    # --- Eliminar Cliente ---
    if st.session_state["rol"] == "admin":  # Solo admin puede eliminar
        with st.expander("Eliminar Cliente"):
            clientes_eliminar = session.query(Cliente).all()
        if not clientes_eliminar:
            st.info("No hay clientes para eliminar.")
        else:
            nombre_cliente_eliminar = st.selectbox(
                "Selecciona el cliente a eliminar:",
                [cliente.nombre for cliente in clientes_eliminar]
            )
            cliente_a_eliminar = next(
                (cliente for cliente in clientes_eliminar if cliente.nombre == nombre_cliente_eliminar),
                None,
            )

            if cliente_a_eliminar:
                if st.button("Eliminar Cliente"):
                    session.delete(cliente_a_eliminar)
                    session.commit()
                    st.success(f"Cliente '{nombre_cliente_eliminar}' eliminado.")
                    # Opcional: Recargar la lista de clientes o mostrar un mensaje
                    st.rerun() # Para actualizar la lista de clientes