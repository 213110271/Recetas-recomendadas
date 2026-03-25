"""
Script para cargar variables de entorno desde .env
"""
import os
from pathlib import Path

def load_env():
    """Carga variables de entorno desde archivo .env"""
    env_file = Path(__file__).parent.parent / '.env'
    
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                # Ignorar comentarios y líneas vacías
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

# Cargar al importar
load_env()
