# Python Network Scanner

A small Python 3 TCP connect scanner for a single IPv4 host or hostname. It checks only selected ports and does not expand or scan entire subnets.

## Requirements
- Python 3.10+
- No third-party packages

## Usage
```bash
python3 network_scanner.py 127.0.0.1
python3 network_scanner.py 127.0.0.1 --ports 22,80,443
python3 network_scanner.py localhost --ports 1-1024 --timeout 0.3 --workers 32
```

## Options
- `--ports`: comma-separated ports or a range; maximum 4096 ports per scan
- `--timeout`: connection timeout from 0.05 to 10 seconds
- `--workers`: concurrency from 1 to 64

## Tests
```bash
python3 -m unittest -v
python3 network_scanner.py 127.0.0.1 --ports 1,22,80,443
```

For a positive test, start a temporary local HTTP server in another terminal:
```bash
python3 -m http.server 8000 --bind 127.0.0.1
```
Then run `python3 network_scanner.py 127.0.0.1 --ports 8000`.

## Safety
Use only on systems you own or have explicit permission to test. Educational lab use only; this tool does not exploit services.
