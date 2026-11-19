import socket
import subprocess
import sys
import threading
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('network_scanner.py')

class ScannerTests(unittest.TestCase):
    def test_help(self):
        run = subprocess.run([sys.executable, str(SCRIPT), '--help'], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0)
        self.assertIn('authorized lab targets', run.stdout)

    def test_detects_local_listener(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 0))
        server.listen(1)
        port = server.getsockname()[1]
        server.settimeout(0.5)
        def accept_once():
            try:
                conn, _ = server.accept()
                conn.close()
            except socket.timeout:
                pass
        thread = threading.Thread(target=accept_once, daemon=True)
        thread.start()
        run = subprocess.run([sys.executable, str(SCRIPT), '127.0.0.1', '--ports', str(port)], capture_output=True, text=True, timeout=5)
        server.close()
        thread.join(timeout=1)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn(f'{port}/tcp  open', run.stdout)

if __name__ == '__main__':
    unittest.main()
