#!/usr/bin/env bash
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe -T -o BatchMode=yes"
$SSH spartan 'sinfo -p sapphire -N -o "%N %C %m %T" | head -n 30'
