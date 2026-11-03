# Laptop helper: normalise a script to LF, then run it on Spartan via OpenSSH "bash -s".
param([string]$f)
$t = [IO.File]::ReadAllText($f) -replace "`r`n", "`n"
[IO.File]::WriteAllText($f, $t)
cmd /c "C:\Windows\System32\OpenSSH\ssh.exe spartan bash -s < $($f -replace '/', '\')"
