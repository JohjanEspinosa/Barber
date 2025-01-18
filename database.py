from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Crear la base de datos
Base = declarative_base()
engine = create_engine('sqlite:///barberia.db', echo=True)  # 'barberia.db' es el nombre de la base de datos SQLite
Session = sessionmaker(bind=engine)
session = Session()

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
