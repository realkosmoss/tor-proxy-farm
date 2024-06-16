import random
from mitmproxy import http, proxy, options
from mitmproxy.tools.dump import DumpMaster

# Function to load proxies from proxies.txt file
def load_proxies(filename):
    with open(filename) as f:
        proxies = [line.strip() for line in f if line.strip()]
    return proxies

# Example list of proxy servers
proxies = load_proxies('proxies.txt')

class ProxyPool:
    def __init__(self, proxies):
        self.proxies = proxies
        self.current_index = 0

    def get_next_proxy(self):
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy

    def request(self, flow: http.HTTPFlow) -> None:
        proxy = self.get_next_proxy()
        flow.request.headers["X-Forwarded-For"] = proxy
        print(f"Forwarding request to proxy {proxy}")

def start_proxy_server():
    proxy_pool = ProxyPool(proxies)

    opts = options.Options(listen_host='0.0.0.0', listen_port=1080)
    pconf = proxy.config.ProxyConfig(opts)
    m = DumpMaster(opts)

    m.server = proxy.server.ProxyServer(pconf)
    m.addons.add(proxy_pool)

    try:
        print("Starting proxy pool server on 0.0.0.0:1080...")
        m.run()
    except KeyboardInterrupt:
        print("Shutting down proxy pool server...")
        m.shutdown()

if __name__ == "__main__":
    start_proxy_server()
