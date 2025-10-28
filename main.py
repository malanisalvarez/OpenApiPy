# main.py
from core.connectors import PlatformConnector
from core.loader import Loader

ACCESS_TOKEN = "pKO6sd7AHGaCo86njOJrMsSrudmCbvwV9FVXKxUxN94"
CTID_ACCOUNT_ID = 44241979  # Reemplaza por tu ID numérico
CLIENT_ID = "18191_sbs6cQ0toYX0bgNVLdB0LlKJbdy4IAb6D238gXbwz2kIu2opNj"
CLIENT_SECRET = "7JLdsiIjOa32QVMOzgT2K9HftI9YF9A19m2U8zK83dZg1qOgPZ"
HOST_TYPE = 'demo'

# 📦 Clase extendida para soportar callback después de autenticación
class CustomConnector(PlatformConnector):
    def __init__(self, *args, on_ready=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_ready = on_ready

    def _after_account_auth(self, message):
        print("✅ Cuenta autenticada. Plataforma lista para enviar solicitudes.")
        if self.on_ready:
            self.on_ready(self.client, self.ctid_account_id)

# 🧠 Lógica una vez autenticado
def on_ready(client, account_id):
    loader = Loader(symbol="EURUSD", timeframe="M1", client=client, account_id=account_id)
    deferred = loader.load_symbol_catalog()

    def mostrar_catalogo(df_catalogo):
        print("✅ Catálogo de símbolo:")
        print(df_catalogo.head())

        # Cargar y mostrar transacciones
        df_transactions = loader.load_symbol_transactions()
        print("📊 Transacciones simuladas:")
        print(df_transactions.head())

    deferred.addCallback(mostrar_catalogo)

# 🚀 Ejecutar todo
connector = CustomConnector(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    access_token=ACCESS_TOKEN,
    ctid_account_id=CTID_ACCOUNT_ID,
    host_type=HOST_TYPE,
    on_ready=on_ready
)
connector.connect()




