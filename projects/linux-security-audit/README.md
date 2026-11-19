# Linux Security Audit Tool

A read-only Bash baseline audit that checks basic host details, common firewall availability, selected SSH settings, and whether common SSH service units appear active. It does not change settings or claim to be a complete vulnerability scanner.

## Requirements
- Bash
- Standard Linux utilities
- Optional: `ufw`, `firewall-cmd`, `systemctl`

## Run
```bash
chmod +x security_audit.sh
./security_audit.sh
```

## Validate
```bash
bash -n security_audit.sh
./security_audit.sh
```
Review each `[WARN]` item manually. Distribution defaults, SSH include files, and firewall implementations vary, so the output is a starting point rather than definitive security proof.

## Safety
The script is read-only. It does not alter firewall, SSH, user, or system settings. Review the source before running it on a production host.
