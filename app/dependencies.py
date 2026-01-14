# app/dependencies.py
from typing import Generator
from app.db.session import SessionLocal
from passlib.context import CryptContext
import hashlib
from geoalchemy2.elements import WKBElement
from shapely import wkb

# DB
def get_db() -> Generator:
    """
    Dependency untuk mendapatkan database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Enkriptor
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

class Hasher():
    @staticmethod
    def verify_password(plain_password, hashed_password):
        # Hash dengan SHA256 dulu sebelum verify dengan bcrypt
        sha_password = hashlib.sha256(plain_password.encode()).hexdigest()
        return pwd_context.verify(sha_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password):
        sha_password = hashlib.sha256(password.encode()).hexdigest()
        return pwd_context.hash(sha_password)

# Fitur Geo
def extract_lat_lon(geom: WKBElement) -> dict:
    """
    Extract latitude dan longitude dari PostGIS geometry
    
    Returns:
        dict dengan keys 'latitude' dan 'longitude'
    """
    if geom is None:
        return None
    
    point = wkb.loads(bytes(geom.data))
    return {
        'longitude': point.x,
        'latitude': point.y
    }