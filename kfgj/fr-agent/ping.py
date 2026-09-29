import urllib.request, json
import sys

# 默认端口，可通过命令行参数覆盖
DEFAULT_PORT = 18999

def ping(port=None):
    if port is None:
        port = DEFAULT_PORT
    try:
        r = json.loads(urllib.request.urlopen(f'http://localhost:{port}/ping', timeout=5).read())
        print(f'Agent (port {port}):', r)
    except Exception as e:
        print(f'Error (port {port}):', e)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else None
    ping(port)
