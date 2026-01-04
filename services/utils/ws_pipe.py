import sys
import threading
import ssl
from websocket import create_connection

# Konfigurasi Akun
# Try using the /ssh path which is common for these tunnels, or root if that fails.
# Based on the error, root returned 400 HTML, so it might be a wrong path.
WS_URL = "wss://nl.wstunnel.xyz/ssh" 
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
        ws = create_connection(
            WS_URL, 
            sslopt={"cert_reqs": ssl.CERT_NONE}, 
            header={
                "Host": HOST,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        
        # Start Threads
        t = threading.Thread(target=pipe_ws_to_stdout, args=(ws,))
        t.daemon = True
        t.start()
        
        pipe_stdin_to_ws(ws)
    except Exception as e:
        sys.stderr.write(f"Connection Error: {str(e)}\n")
