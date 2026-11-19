#!/usr/bin/env bash
# Read-only baseline audit for a Linux host. Does not change system settings.
set -u
pass() { printf '[PASS] %s\\n' "$1"; }
warn() { printf '[WARN] %s\\n' "$1"; }
info() { printf '[INFO] %s\\n' "$1"; }

printf 'Linux Security Baseline Audit\\n==============================\\n'
printf 'Host: %s\\nDate: %s\\n\\n' "$(hostname 2>/dev/null || echo unknown)" "$(date -Is 2>/dev/null || date)"
if command -v uname >/dev/null 2>&1; then info "Kernel: $(uname -sr)"; fi
if [ "$(id -u)" -eq 0 ]; then info 'Running as root; report may include more detail.'; else info 'Running without root; some checks may be limited.'; fi

if command -v ufw >/dev/null 2>&1; then
  status=$(ufw status 2>/dev/null | head -n 1 || true)
  case "$status" in *active*) pass "UFW firewall is active ($status)" ;; *) warn "UFW is installed but not reported active ($status)" ;; esac
elif command -v firewall-cmd >/dev/null 2>&1; then
  status=$(firewall-cmd --state 2>/dev/null || true)
  [ "$status" = running ] && pass 'firewalld is running' || warn "firewalld state: ${status:-unknown}"
else
  warn 'Neither ufw nor firewall-cmd was found; verify the host firewall manually.'
fi

if [ -r /etc/ssh/sshd_config ]; then
  if grep -Eq '^[[:space:]]*PermitRootLogin[[:space:]]+no([[:space:]#]|$)' /etc/ssh/sshd_config; then pass 'sshd_config explicitly disables root login'; else warn 'Root login is not explicitly disabled in /etc/ssh/sshd_config (included config may override this).'; fi
  if grep -Eq '^[[:space:]]*PasswordAuthentication[[:space:]]+no([[:space:]#]|$)' /etc/ssh/sshd_config; then pass 'sshd_config explicitly disables password authentication'; else warn 'Password authentication is not explicitly disabled in /etc/ssh/sshd_config (included config may override this).'; fi
else
  info 'SSH server config not found/readable; SSH checks skipped.'
fi

if [ -r /etc/passwd ] && [ -r /etc/shadow ]; then pass 'Standard local account database files are present.'; else info 'Could not read both /etc/passwd and /etc/shadow; account database check limited.'; fi
if command -v systemctl >/dev/null 2>&1; then
  if systemctl is-active --quiet ssh 2>/dev/null || systemctl is-active --quiet sshd 2>/dev/null; then info 'SSH service appears active; ensure remote access is required and restricted.'; else pass 'SSH service does not appear active under common unit names.'; fi
else
  info 'systemctl unavailable; service checks skipped.'
fi
if [ -r /etc/os-release ]; then . /etc/os-release; info "Distribution: ${PRETTY_NAME:-unknown}"; fi
printf '\\nAudit finished. WARN means review manually, not necessarily a confirmed vulnerability.\\n'
