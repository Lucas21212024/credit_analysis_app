from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class HistoricoAnalise(Base):
    __tablename__ = 'historico_analises'

    id = Column(Integer, primary_key=True)
    data = Column(DateTime, default=datetime.utcnow)
    cliente = Column(String, nullable=False)
    cnpj = Column(String, nullable=False)
    pontuacao = Column(Integer, nullable=False)
    risco = Column(String, nullable=False)
    motivos_positivos = Column(Text, nullable=True)
    motivos_negativos = Column(Text, nullable=True)

# Configuração do banco de dados SQLite
engine = create_engine('sqlite:///data/analises.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
