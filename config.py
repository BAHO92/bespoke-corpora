import os
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get('BESPOKE_DATA_DIR', APP_ROOT / 'data'))

CORPUS_DIR = DATA_DIR / 'corpus'
DB_ROOT = DATA_DIR / 'db'

HOST = os.environ.get('BESPOKE_HOST', '127.0.0.1')
VAULT_PORT = int(os.environ.get('BESPOKE_PORT', '5222'))
