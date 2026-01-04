import sys
import threading
import ssl
from websocket import create_connection

# Konfigurasi Akun
# Mencoba kembali ke root path tapi dengan slash eksplisit
WS_URL = "wss://nl.wstunnel.xyz/" 
HOST = "nl.wstunnel.xyz"

def pipe_stdin_to_ws(ws):
    try:
        while True:
            data = sys.stdin.buffer.read(4096)
            if not data: break
            ws.send_binary(data)
    except Exception:
        pass
    finally:
        try:
            ws.close()
        except:
            pass

def pipe_ws_to_stdout(ws):
    try:
        while True:
            data = ws.recv()
            if not data: break
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
    except Exception:
        pass

if __name__ == "__main__":
    try:
        # Connect to WebSocket
        # Kita hapus custom header Host manual, biarkan library yang atur otomatis
        # kadang double header bikin error 400
        ws = create_connection(
            WS_URL, 
            sslopt={"cert_reqs": ssl.CERT_NONE}
        )
        
        # Start Threads
        t = threading.Thread(target=pipe_ws_to_stdout, args=(ws,))
        t.daemon = True
        t.start()
        
        pipe_stdin_to_ws(ws)
    except Exception as e:
        sys.stderr.write(f"Connection Error: {str(e)}\n")
