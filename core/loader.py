# loader.py
import pandas as pd
from ctrader_open_api.messages.OpenApiMessages_pb2 import (
    ProtoOASymbolsListReq,
    ProtoOAGetTickDataReq,
    ProtoOASymbolByIdReq
)
from ctrader_open_api.protobuf import Protobuf
from typing import Optional
from twisted.internet import defer


class Loader:
    def __init__(self, symbol: str, timeframe: str, client, account_id: int):
        self.symbol = symbol.upper()
        self.timeframe = timeframe
        self.client = client 
        self.account_id = account_id 
        self.symbol_id = None  # Lo asignaremos luego

    def load_symbol_catalog(self) -> Optional[defer.Deferred]:
        """Carga el símbolo completo a partir del nombre."""
        req = ProtoOASymbolsListReq(ctidTraderAccountId=self.account_id)
        deferred = self.client.send(req)

        deferred.addCallback(self._fetch_symbol_detail)   # ✅ Método propio
        deferred.addCallback(self._process_symbol_detail) # ✅ Método propio
        deferred.addErrback(self._on_error)
        return deferred

    def _fetch_symbol_detail(self, message):
        decoded = Protobuf.extract(message)
        matches = [s for s in decoded.symbol if s.symbolName == self.symbol]

        if not matches:
            raise ValueError(f"❌ Símbolo {self.symbol} no encontrado en catálogo.")

        symbol_row = matches[0]
        self.symbol_id = symbol_row.symbolId

        # Solicita los detalles completos del símbolo
        symbol_req = ProtoOASymbolByIdReq(
            ctidTraderAccountId=self.account_id,
            symbolId=[self.symbol_id]  # ✅ Debe ser una lista
        )

        return self.client.send(symbol_req)

    def _process_symbol_detail(self, message):
        decoded = Protobuf.extract(message)

        # ✅ decoded.symbol es una lista, tomamos el primer elemento
        s = decoded.symbol[0]

        data = {
                "symbolId": s.symbolId,
                "symbolName": getattr(s, "symbolName", ""),
                "description": getattr(s, "description", ""),
                "pipPosition": getattr(s, "pipPosition", 0),
                "minTradeVolume": getattr(s, "minTradeVolume", 0),
                "maxLeverage": getattr(s, "maxLeverage", 0),
                "commission": getattr(s, "commission", 0),
                "spread": getattr(s, "spread", 0),
                "swapLong": getattr(s, "swapLong", 0),
                "swapShort": getattr(s, "swapShort", 0),
                "lotSize": getattr(s, "lotSize", 0),
            }

        print("✅ Datos procesados correctamente ✅")
        return pd.DataFrame([data])

    def load_symbol_transactions(self) -> Optional[pd.DataFrame]:
        """Simula carga de datos transaccionales (ficticios por ahora)."""
        data = {
            "timestamp": pd.date_range("2025-01-01", periods=10, freq="min"),
            "price_bid": [1.1 + i * 0.0001 for i in range(10)],
            "price_ask": [1.1002 + i * 0.0001 for i in range(10)],
        }
        return pd.DataFrame(data)

    def _on_error(self, failure):
        print(f"❌ Error al cargar catálogo: {failure}")