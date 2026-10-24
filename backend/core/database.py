from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker


URL_BANCO_DADOS = "postgresql://admin:adminpassword@localhost:5432/grafos_musicais"

engine = create_engine(URL_BANCO_DADOS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Musica(Base):
    __tablename__ = "musicas"

    track_id = Column(String, primary_key=True, index=True)
    track_name = Column(String, index=True)
    artists = Column(String)
    track_genre = Column(String)
    
    tempo = Column(Float)
    valence = Column(Float)
    energy = Column(Float)
    danceability = Column(Float)
    loudness = Column(Float)
    speechiness = Column(Float)
    acousticness = Column(Float)
    instrumentalness = Column(Float)
    liveness = Column(Float)

Base.metadata.create_all(bind=engine)