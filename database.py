from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import bcrypt

# Crear la base de datos
Base = declarative_base()
engine = create_engine('sqlite:///barberia.db', echo=True)  # 'barberia.db' es el nombre de la base de datos SQLite
Session = sessionmaker(bind=engine)
session = Session()

def hashear_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def crear_usuario(nombre, email, password, rol='empleado'):
    session = Session()
    existing_user = session.query(Usuario).filter(Usuario.email == email).first()
    if existing_user:
        session.close()
        return False, "El correo electrónico ya está registrado."
    try:
        hashed_password = hashear_password(password)
        nuevo_usuario = Usuario(nombre=nombre, email=email, password=hashed_password, rol=rol)
        session.add(nuevo_usuario)
        session.commit()
        session.close()
        return True, "Usuario creado exitosamente."
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error al crear el usuario: {e}"
    
def verificar_usuario_con_rol(email, password):
    """Verifica el usuario y devuelve el rol si la autenticación es exitosa."""
    session = Session()
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    session.close()
    if usuario and bcrypt.checkpw(password.encode('utf-8'), usuario.password.encode('utf-8')):
        return True, usuario.rol
    return False, None
    
# Modelo de Cliente
class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    documento = Column(String, unique=True, nullable=False)

# Modelo de Servicio
class Servicio(Base):
    __tablename__ = 'servicios'
    __table_args__ = {'extend_existing': True}  # Evita el error si la tabla ya está definida
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)

# Modelo de Venta
class Venta(Base):
    __tablename__ = 'ventas'
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, nullable=False)
    servicio_id = Column(Integer, nullable=False)
    fecha_venta = Column(DateTime, default=datetime.utcnow)
    precio_servicio = Column(Float)  # Asegúrate de que este campo esté en la tabla

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)  # Cifrada
    rol = Column(String)  # 'admin' o 'empleado'
# Crear las tablas si no existen
Base.metadata.create_all(engine)
