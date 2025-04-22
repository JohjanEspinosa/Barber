import streamlit as st
from models.modelos_clientes import gestionar_clientes
from models.modelos_servicios import gestionar_servicios
from models.modelos_ventas import gestionar_ventas
from database import crear_usuario
import bcrypt
from database import Session, Usuario, crear_usuario, verificar_usuario_con_rol

def registrar_usuario():
    nombre_registro = st.session_state.get("nombre_registro", "")
    email_registro = st.session_state.get("email_registro", "")
    password_registro = st.session_state.get("password_registro", "")
    confirm_password_registro = st.session_state.get("confirm_password_registro", "")

    if password_registro == confirm_password_registro:
        success, message = crear_usuario(nombre_registro, email_registro, password_registro)
        if success:
            st.success(message)
            # Limpiar los campos directamente en st.session_state
            st.session_state["nombre_registro"] = ""
            st.session_state["email_registro"] = ""
            st.session_state["password_registro"] = ""
            st.session_state["confirm_password_registro"] = ""
        else:
            st.error(message)
    else:
        st.error("Las contraseñas no coinciden.")

def main():
    st.markdown(
        """
        <style>

        .login-title {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .stTextInput label {
            color: #555;
        }
        .stButton>button {
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            cursor: pointer;
            width: 100%;
            margin-top: 10px;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
        .error-message {
            color: #dc3545;
            margin-top: 10px;
            text-align: center;
        }
        .success-message {
            color: #28a745;
            margin-top: 10px;
            text-align: center;
        }
        .register-link {
            text-align: center;
            margin-top: 20px;
            font-size: 0.9em;
            color: #777;
        }
        .register-link a {
            color: #007bff;
            text-decoration: none;
        }
        .register-link a:hover {
            text-decoration: underline;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["usuario"] = None
        st.session_state["rol"] = None
        st.session_state["show_register"] = False # Estado para mostrar/ocultar registro

    if not st.session_state["logged_in"]:
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.markdown('<h2 class="login-title">Iniciar Sesión</h2>', unsafe_allow_html=True)

            email_login = st.text_input("Correo Electrónico", key="email_login")
            password_login = st.text_input("Contraseña", type="password", key="password_login")

            if st.button("Iniciar Sesión", key="login_button"):
                success, rol = verificar_usuario_con_rol(email_login, password_login)
                if success:
                    st.markdown(f'<p class="success-message">¡Bienvenido, {email_login}!</p>', unsafe_allow_html=True)
                    st.session_state["logged_in"] = True
                    st.session_state["usuario"] = email_login
                    st.session_state["rol"] = rol
                    st.rerun()
                else:
                    st.markdown('<p class="error-message">Correo electrónico o contraseña incorrectos.</p>', unsafe_allow_html=True)

            st.markdown('<p class="register-link">¿No tienes cuenta? <a href="#" onclick="document.querySelector(\'[data-testid="stCheckbox"] input\').click()">Regístrate</a></p>', unsafe_allow_html=True)
            register_option = st.checkbox("Mostrar Registro", key="show_register_checkbox", label_visibility="collapsed")

            if register_option or st.session_state.get("show_register", False):
                st.markdown('<h2 class="login-title">Registrarse</h2>', unsafe_allow_html=True)
                nombre_registro = st.text_input("Nombre", key="nombre_registro")
                email_registro = st.text_input("Correo Electrónico", key="email_registro")
                password_registro = st.text_input("Nueva Contraseña", type="password", key="password_registro")
                confirm_password_registro = st.text_input("Confirmar Contraseña", type="password", key="confirm_password_registro")

                if st.button("Registrar", key="registro_button", on_click=registrar_usuario):
                    st.session_state["show_register"] = True # Mantener visible después del intento de registro

            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.write(f"¡Hola, {st.session_state['usuario']}!")
        st.write(f"Rol: {st.session_state['rol']}")
        if st.session_state["rol"] == "admin":
            st.subheader("Panel de Administrador")
            st.sidebar.title("Menú")
            opciones = ["Inicio", "Clientes", "Servicios", "Ventas", "Reportes", "Cerrar Sesión"]
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
            elif seleccion == "Cerrar Sesión":
                st.session_state["logged_in"] = False
                st.session_state["usuario"] = None
                st.session_state["rol"] = None
                st.session_state["show_register"] = False
                st.rerun()

        elif st.session_state["rol"] == "empleado":
            st.subheader("Panel de Barbero")
            st.sidebar.title("Menú")
            opciones = ["Inicio", "Clientes", "Ventas", "Cerrar Sesión"]
            seleccion = st.sidebar.radio("Selecciona una opción:", opciones)
            if seleccion == "Inicio":
                st.write("Bienvenido al Sistema de Gestión de la Barbería.")
                st.write("Aquí podrás gestionar tus clientes y ventas.")
            elif seleccion == "Clientes":
                    gestionar_clientes()
            elif seleccion == "Ventas":
                    gestionar_ventas()
            elif seleccion == "Cerrar Sesión":
                st.session_state["logged_in"] = False
                st.session_state["usuario"] = None
                st.session_state["rol"] = None
                st.session_state["show_register"] = False
                st.rerun()


if __name__ == "__main__":
    main()