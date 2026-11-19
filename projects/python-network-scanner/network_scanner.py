#!/usr/bin/env python3
"""Small TCP connect scanner for systems you own or are authorized to test."""
import argparse
import ipaddress
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

COMMON_PORTS = [20, 21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080]

def parse_ports(value: str) -> list[int]:
    ports = set()
    try:
        for part in value.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-', 1))
                if start > end:
                    raise ValueError
                ports.update(range(start, end + 1))
            else:
                ports.add(int(part))
    except ValueError as exc:
        raise argparse.ArgumentTypeError('Use ports like 22,80,443 or a range like 1-1024.') from exc
    if not ports or min(ports) < 1 or max(ports) > 65535 or len(ports) > 4096:
        raise argparse.ArgumentTypeError('Ports must be 1-65535 and at most 4096 ports per scan.')
    return sorted(ports)

def scan_port(host: str, port: int, timeout: float) -> tuple[int, bool, str]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host, port))
        return port, result == 0, ''
    except OSError as exc:
        return port, False, str(exc)
    finally:
        sock.close()

def main() -> int:
    parser = argparse.ArgumentParser(description='TCP connect scanner for authorized lab targets.')
    parser.add_argument('target', help='Single IPv4 address or hostname you own / are authorized to test')
    parser.add_argument('-p', '--ports', type=parse_ports, default=COMMON_PORTS,
                        help='Comma-separated ports or range (default: common ports)')
    parser.add_argument('--timeout', type=float, default=0.5, help='Connection timeout in seconds (default: 0.5)')
    parser.add_argument('--workers', type=int, default=32, help='Concurrent connections, 1-64 (default: 32)')
    args = parser.parse_args()
    if not 0.05 <= args.timeout <= 10:
        parser.error('--timeout must be between 0.05 and 10 seconds')
    if not 1 <= args.workers <= 64:
        parser.error('--workers must be between 1 and 64')
    try:
        target = socket.gethostbyname(args.target)
        ipaddress.IPv4Address(target)
    except (socket.gaierror, ValueError):
        print(f'Error: could not resolve {args.target!r} to an IPv4 address.', file=sys.stderr)
        return 2
    print(f'Target: {args.target} ({target})')
    print(f'Ports: {len(args.ports)} | Timeout: {args.timeout}s | Workers: {args.workers}')
    print('Only scan systems you own or have explicit permission to test.\n')
    opened = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(scan_port, target, port, args.timeout) for port in args.ports]
        for future in as_completed(futures):
            port, is_open, error = future.result()
            if is_open:
                opened.append(port)
    if opened:
        print('OPEN TCP PORTS')
        for port in sorted(opened):
            try:
                service = socket.getservbyport(port, 'tcp')
            except OSError:
                service = 'unknown'
            print(f'{port:5}/tcp  open  {service}')
    else:
        print('No open TCP ports found in the selected port list.')
    print(f'\nCompleted. {len(opened)} open port(s) found.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
