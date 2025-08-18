import asyncio
import ssl
from collections import deque
import threading
from typing import AsyncGenerator
import websockets

from voice.audio_stream import AudioChunk, AudioFormat, AudioStream
from voice.microphone import Microphone 

class WebMicrophone(Microphone):
    """Microfone via WebSocket"""
    def __init__(self, host="0.0.0.0", port=2567, certfile="html/cert.pem", keyfile="html/key.pem"):
        self.host = host
        self.port = port
        self.samples = deque()
        self.certfile = certfile
        self.keyfile = keyfile
        self.stream = AudioStream()

    async def __handler(self, websocket):
        print("Device connected")
        try:
            async for message in websocket:
                if isinstance(message, bytes):
                    self.stream.feed(AudioChunk(message, AudioFormat(16000, "int16")))
                    #print("Chunk Received")
                else:
                    print("ERR: WebSocket não recebeu áudio")
        except:
            print("WebMic Client disconnected.")

    async def __start_websocket_server(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
        async with websockets.serve(
            self.__handler,
            self.host,
            self.port,
            ssl=ssl_context
        ):
            print(f"WebMicrophone WSS rodando em wss://{self.host}:{self.port}")
            await asyncio.Future()

    def start(self) -> AudioStream:
        """
        Inicia servidor WebSocket seguro (WSS)
        """
        
        def run():
            asyncio.run(self.__start_websocket_server())

        threading.Thread(target=run, daemon=True).start()
            
        return self.stream
