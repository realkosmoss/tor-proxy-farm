import os
import tempfile
import subprocess
import psutil

class ServiceInstaller:
    # Path to the local Tor executable
    service_executable = "tor.exe"

    def __init__(self, total_ips):
        self.temp_dir = os.path.join(tempfile.gettempdir(), "xoloservice")
        self.total_ips = total_ips
        self.stop_tor_service()

    def _create_temp_directory(self):
        os.makedirs(self.temp_dir, exist_ok=True)

    def _generate_ips_file(self, file_path):
        ips = ["HTTPTunnelPort 9080"]
        ips += [f"HTTPTunnelPort {9081 + i}" for i in range(self.total_ips - 1)]
        with open(file_path, 'w') as f:
            f.write("\n".join(ips))

    def install_service(self):
        self._create_temp_directory()
        config_path = os.path.join(self.temp_dir, "config")
        self._generate_ips_file(config_path)

        process = subprocess.Popen([self.service_executable, "-f", config_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            line = process.stdout.readline().decode().strip()
            print(line)
            if "Bootstrapped 100% (done): Done" in line:
                break

    def stop_tor_service(self):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == "tor.exe":
                proc.terminate()
                proc.wait()  # Ensure the process has terminated

def make(total_ips):
    installer = ServiceInstaller(total_ips)
    installer.install_service()
    proxies = [f"127.0.0.1:{9080 + i}" for i in range(total_ips)]
    
    # Save the proxies to proxies.txt in the format ip:port
    with open('proxies.txt', 'w') as f:
        f.write("\n".join(proxies))
    
    return proxies

ips = make(500)
input(f"\nPROXIES GENERATED:\n{ips}\n\nPress enter to terminate the proxies...")
