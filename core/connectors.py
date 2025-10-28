from ctrader_open_api import Client, Protobuf, TcpProtocol, EndPoints
from ctrader_open_api.messages.OpenApiMessages_pb2 import (
    ProtoOAApplicationAuthReq,
    ProtoOAAccountAuthReq,
)
from twisted.internet import reactor


class PlatformConnector:
    def __init__(self, client_id: str, client_secret: str, access_token: str, ctid_account_id: int, host_type: str = "demo"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.ctid_account_id = ctid_account_id
        self.host = EndPoints.PROTOBUF_LIVE_HOST if host_type.lower() == "live" else EndPoints.PROTOBUF_DEMO_HOST
        self.client = Client(self.host, EndPoints.PROTOBUF_PORT, TcpProtocol)

    def connect(self):
        self.client.setConnectedCallback(self._on_connected)
        self.client.setDisconnectedCallback(self._on_disconnected)
        self.client.setMessageReceivedCallback(self._on_message_received)
        print("\n🚀 Iniciando cliente...")
        self.client.startService()
        reactor.run()

    def _on_connected(self, client):
        print("🔗 Conectado. Enviando autenticación de aplicación...")
        app_auth = ProtoOAApplicationAuthReq()
        app_auth.clientId = self.client_id
        app_auth.clientSecret = self.client_secret

        d = self.client.send(app_auth)
        d.addCallback(self._after_app_auth)
        d.addErrback(self._on_error)

    def _after_app_auth(self, message):
        print("✅ Aplicación autenticada. Enviando autenticación de cuenta...")
        account_auth = ProtoOAAccountAuthReq()
        account_auth.ctidTraderAccountId = self.ctid_account_id
        account_auth.accessToken = self.access_token

        d = self.client.send(account_auth)
        d.addCallback(self._after_account_auth)
        d.addErrback(self._on_error)

    def _after_account_auth(self, message):
        print("✅ Cuenta autenticada. Plataforma lista para enviar solicitudes.")
        # Aquí es donde en el futuro puedes encadenar solicitudes como obtener símbolos, trades, etc.

    def _on_message_received(self, client, message):
        print("📨 Mensaje recibido:\n")
        print(Protobuf.extract(message))

    def _on_disconnected(self, client, reason):
        print(f"❌ Desconectado: {reason}")

    def _on_error(self, failure):
        print(f"❌ Error en la operación: {failure}")