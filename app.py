import streamlit as st
from models.modelos_clientes import gestionar_clientes
from models.modelos_servicios import gestionar_servicios
from models.modelos_ventas import gestionar_ventas

# Ventana Principal de Navegación
def main():
    st.title("Sistema de Barbaros Shop")
    st.sidebar.title("Menú")
    opciones = ["Inicio", "Clientes", "Servicios", "Ventas"]
    seleccion = st.sidebar.radio("Selecciona una opción:", opciones)

    if seleccion == "Inicio":
        st.write("Bienvenido al Sistema de Gestión de la Barbería.")
        st.write("Aquí podrás gestionar tus clientes, servicios y ventas.")
    elif seleccion == "Clientes":
        gestionar_clientes()
    elif seleccion == "Servicios":
        gestionar_servicios()
    elif seleccion == "Ventas":
        gestionar_ventas()

if __name__ == "__main__":
    main()
