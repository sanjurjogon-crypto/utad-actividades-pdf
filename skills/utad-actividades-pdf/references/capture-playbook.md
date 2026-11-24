# Capture playbook (Windows + VirtualBox)

The evidence is the part that cannot be faked. Everything here is about getting a frame that
shows **the command and its output, legible**, on the machine the statement asks for.

## The one rule

A capture is valid when a reader who does not know the activity can read the command, read the
output, and see that the output belongs to that command. If any of the three fails, recapture.

## Order of preference (Windows host)

1. **`VBoxManage.exe` directly**:
   - Locate it via `PATH` or `"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"`.
   - `VBoxManage controlvm "<VM>" screenshotpng <out.png>` captures the VM framebuffer directly
     for both Linux and Windows guests (no guest credentials required).
   - `VBoxManage guestcontrol "<VM>" run` / `start` / `copyto` runs commands or opens scripted
     terminal windows inside guests that have VirtualBox Guest Additions installed.
   - `VBoxManage snapshot "<VM>" take "<name>"` creates snapshots.
2. **SSH into the VM** (when VirtualBox uses Bridged, Host-Only, or NAT port forwarding and
   `guestcontrol` credentials are unavailable or Guest Additions are not installed).
3. **A real terminal on the Windows host / WSL**, if the statement targets Windows or allows it.
4. **The user's own screenshots**, if there is no VM or access at all. Then the document ships
   with `[[CAPTURA: …]]` placeholders on purpose.

## Checking VirtualBox VMs on Windows

```powershell
$VBOX = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
& $VBOX list vms
& $VBOX list runningvms
& $VBOX showvminfo "U-UD2-Sanjurjo" --machinereadable | Select-String "VMState|ostype|GuestAdditions"
```

- Start a powered-off VM in GUI mode if you need interactive display output:
  `& $VBOX startvm "<VM>" --type gui`
- Wait until Guest Additions desktop integration is up (`GuestAdditionsRunLevel=3` or `5`)
  before running GUI commands via `guestcontrol`.

## Linux guest: the scripted-window trick

Typing into a guest terminal through `keyboardputscancode` is slow and fragile (layout, focus,
Wayland). Instead write a small script inside the guest and open a terminal window that runs it,
then capture with `vm_capture.py`.

Important: `VBoxManage guestcontrol ... start` returns immediately without waiting for `sleep`,
whereas `guestcontrol ... run` waits for the command to finish (use `run` for file creation and
checks, `start` for launching `gnome-terminal`). GUI terminals also need `DISPLAY`,
`XDG_RUNTIME_DIR`, and `WAYLAND_DISPLAY` passed via `--putenv`:

```powershell
$VBOX = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
$VM = "U-UD2-Sanjurjo"
$USER = "sanjurjo"   # guest username
$PASS = "..."        # guest password (or use --passwordfile)

# 1. Create the script inside the guest (one command per line; stop xtrace before sleep)
$script = @'
export PS4="$ "
set -x
ip -4 a
ip route
ping -c 2 10.0.2.2
{ set +x; } 2>/dev/null
touch ~/.cap_done
sleep 900
'@ -replace "`r`n", "`n"
$script | Set-Content -NoNewline -Encoding Ascii s1.sh

& $VBOX guestcontrol "$VM" copyto --username $USER --password $PASS `
  "$PWD\s1.sh" "/home/$USER/s1.sh"

# 2. Open a compact terminal window on the active desktop session
& $VBOX guestcontrol "$VM" start --exe "/usr/bin/gnome-terminal" `
  --username $USER --password $PASS `
  --putenv "DISPLAY=:0" `
  --putenv "XDG_RUNTIME_DIR=/run/user/1000" `
  --putenv "WAYLAND_DISPLAY=wayland-0" `
  -- gnome-terminal --geometry=100x26 -- bash "/home/$USER/s1.sh"

# 3. Capture and crop with automatic black-frame / missing-window retry
Start-Sleep -Seconds 4
python scripts/vm_capture.py "$VM" fig/raw_fig1.png fig/fig1.png
```

Why `PS4='$ '` + `set -x`: the trace prints each command as `$ ip route` immediately before
its output, so the frame looks like a normal session and is honest — it *is* the real output.
Put one command per line rather than `cmd1 && cmd2` so each command gets its own `$ ` line.
For piped commands (e.g. `top -b -n 2 -d 1 | awk ... | head -n 14`), `set -x` only prints the
last stage (`$ head -n 14`), so print the pipeline manually before running it:
`{ set +x; } 2>/dev/null; echo '$ top -b -n 2 -d 1 | awk ... | head -n 14'; top ... | head -n 14`
(`{ set +x; } 2>/dev/null` stops tracing cleanly before `sleep 900`.)

Notes:

- **Avoid full `apt-get upgrade` inside an active GUI session unless required:** upgrading
  `systemd`, `dbus`, or `gnome-terminal` mid-session can break `gnome-terminal` window launches
  until reboot (use `sudo apt-get update && sudo apt-get install -y <pkg>` instead). Note also
  that Ubuntu's `7zip` package provides `7z` (not `7zz`).
- **Bound network timeouts and wait on a sentinel file for slow/failing commands:** an
  un-timeouted `ping` on broken DNS waits ~12 s before printing the error. Use `ping -c 1 -W 2`,
  `dig +time=2 +tries=1`, and `curl --max-time 3`, `touch ~/.cap_done` right before `sleep 900`,
  and poll `guestcontrol ... run --exe "/bin/test" -- -f /home/$USER/.cap_done` before running
  `vm_capture.py`.
- **Use `sudo` cleanly for root-only commands (`cat /etc/netplan/*.yaml`, `resolvectl`):**
  running them unprivileged inside `gnome-terminal` can pop up a GNOME Polkit password modal
  that blocks screenshots. Verify passwordless sudo or run root commands via `guestcontrol` with
  `--username root` / `echo $PASS | sudo -S ...` in advance, or write output / inspect cleanly.
- **Ubuntu 22.10+ SSH and Netplan hygiene:** `openssh-server` may use systemd socket activation
  (`systemctl disable --now ssh.socket ssh.service`). Inspect `/etc/netplan/` because Netplan
  merges every `.yaml` file; check interface names in VirtualBox (`enp0s3`, `enp0s8`, etc.).
- **Background stress/daemon processes inside Linux VMs:** `guestcontrol run` may terminate
  children when it exits. Use `systemd-run --unit=cpu-hog bash -c 'exec yes >/dev/null 2>&1'`
  and stop later with `systemctl stop cpu-hog`.
- Never put the script in `/tmp` if a reboot happens in between (reboots wipe `/tmp`).
- `--geometry=100x26` gives a compact window whose text is big relative to the image. A
  maximised window produces tiny text that becomes illegible once placed in the PDF. **Prefer a
  smaller window over a bigger capture.**
- Reuse one window per figure: close the previous script (`pkill -f '/s[0-9]+.sh'`) before
  opening the next, or the capture shows the wrong window in front. Do not kill
  `gnome-terminal-server`.
- Disable idle blanking + enable centered windows once per session inside the guest:
  `gsettings set org.gnome.desktop.session idle-delay 0`,
  `gsettings set org.gnome.desktop.screensaver lock-enabled false`, and
  `gsettings set org.gnome.mutter center-new-windows true`.

## Windows guest (VirtualBox)

- `VBoxManage controlvm "<VM>" screenshotpng` works directly on Windows VMs too and captures
  exactly what is on the VM display without needing guest credentials.
- To launch a clean PowerShell window on the Windows guest desktop via `guestcontrol`:

```powershell
$VBOX = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
$VM = "W-UD2-Sanjurjo"
$USER = "sanjurjo"
$PASS = "..."

$psBody = @'
Clear-Host
Write-Output "PS C:\> hostname"
hostname
Write-Output "PS C:\> whoami"
whoami
'@
$wCmd = '[IO.File]::WriteAllText((Join-Path $env:USERPROFILE "s2.ps1"), @"' + "`n$psBody`n" + '"@)'
$wEnc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($wCmd))

& $VBOX guestcontrol "$VM" run `
  --exe "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" `
  --username $USER --password $PASS -- `
  -NoProfile -WindowStyle Hidden -EncodedCommand $wEnc

$lCmd = 'Start-Process powershell -ArgumentList "-NoLogo","-NoExit","-ExecutionPolicy","Bypass","-File",(Join-Path $env:USERPROFILE "s2.ps1")'
$lEnc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($lCmd))

& $VBOX guestcontrol "$VM" start `
  --exe "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" `
  --username $USER --password $PASS -- `
  -NoProfile -WindowStyle Hidden -EncodedCommand $lEnc

Start-Sleep -Seconds 3
python scripts/vm_capture.py "$VM" fig/raw_fig2.png fig/fig2.png
```

Notes:

- **Keep Windows capture output ordered and clean:** avoid piping native executables (`ping`,
  `nslookup`) into `Select-String` when display order matters; use `ping -n 1 -w 1500` directly
  and pass `-ErrorAction SilentlyContinue` to `Get-DnsClientCache` (which errors after
  `ipconfig /flushdns` when empty).
- **Clean up old PowerShell windows** before capturing the next figure:
  `taskkill /IM powershell.exe /F` inside the guest (only kill child windows, never the host's
  own PowerShell!).
- **Elevation (hosts, static IPs, firewall)**: writing to `C:\Windows\System32\drivers\etc\hosts`,
  changing IPs or firewall rules needs elevation. Use an elevated PowerShell / scheduled task
  with `/RL HIGHEST` inside the guest, and avoid leaving a UAC secure-desktop dialog on screen
  when taking the screenshot (UAC secure-desktop shows black/blank in captures).
- If `guestcontrol` returns `VERR_TIMEOUT` or `VERR_UNRESOLVED_ERROR` (e.g. Guest Additions
  not running or credentials mismatch), run the commands directly inside the VM console or via
  SSH and capture with `VBoxManage controlvm "<VM>" screenshotpng` via `scripts/vm_capture.py`.

## Fallback when `guestcontrol` has no credentials (keyboard scancodes)

If the VM already has an active logged-in desktop session and neither `guestcontrol` credentials
nor SSH keys are available, you can open a terminal and type short commands via `controlvm`:

- **Open terminal**:
  - Windows (`Win+R` → `cmd`):
    `keyboardputscancode e0 5b 13 93 e0 db` → wait 1 s → `keyboardputstring "cmd"` → `keyboardputscancode 1c 9c`
  - Ubuntu (`Ctrl+Alt+T`):
    `keyboardputscancode 1d 38 14 94 b8 9d`
- **Spanish (`es`) keyboard layout caveat**: `keyboardputstring` maps US ASCII punctuation, so
  `-` on a Spanish guest layout becomes `'`. Send hyphens explicitly via scancode `35 b5`
  (e.g. `keyboardputstring "free "` + `keyboardputscancode 35 b5` + `keyboardputstring "h"`),
  and clear old output with `reset` (Ubuntu) or `cls` (Windows) before taking the screenshot.

## Reading a capture before you write about it

Open the cropped PNG (or zoom in with `read_file` / Pillow crop) and read the values one by one.
Do not reconstruct them from what a command is supposed to do. The failure this prevents is real:
a sentence claiming a column stayed at 45.872 «en las tres medidas» when the capture showed 45.772
in the middle.

## Cropping

- Crop to the terminal window, not to the desktop, and trim empty rows below the last output
  line. Use `--window` so `crop_capture.py` finds the foreground terminal window automatically
  (works on both dark and light terminals) in one command without writing ad-hoc box scripts:
  ```powershell
  python scripts/crop_capture.py fig/raw_fig1.png fig/fig1.png --window --pad 18
  ```
- Keep the window title bar only if it shows something useful (the VM name or the user). If the
  desktop wallpaper or the taskbar/dock is in frame, it is not cropped enough.
- Do not upscale. If text is small, recapture with a smaller window or larger terminal font.
- Save as PNG in a `fig\` folder next to the build script, named `fig1.png`, `fig2.png`, … and
  keep the raw capture too (`raw_fig1.png`), because recrops are common.

## Verification before you trust a capture

After doing an action, verify the state with an independent command before capturing:

- changed `/etc/hosts` → `getent hosts google.com` and `cat /etc/hosts`
- static IP → `ip -4 -o a` and `ip route`
- removed a user → `id usuario` must say *no such user*
- killed a process → `pgrep` returns nothing

If the verification and the capture disagree, the capture is of an older state. Redo.

## No tools at all (web chat)

Do not fake screenshots and do not describe them in past tense. Produce the document with
placeholders and give the reader a numbered list:

```
[[CAPTURA 1 — terminal 1, ventana compacta]]
Comandos: ip -4 a ; ip route ; ping -c 2 <puerta>
Qué tiene que verse: la IP con su máscara, la línea "default via" y "0 % packet loss".
```

Plus a two-line instruction in the chat: “ejecuta esto en la VM, haz una captura donde se vea
el comando y la salida, y pégala donde dice CAPTURA 1”. That is the graceful degradation, and
it is honest.

## Snapshots

When the statement asks for one (`Haz una instantánea UD2_RED_OK`), create it **after** the
verification passes and mention the name in the last paragraph:

```powershell
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" snapshot "<VM>" take "UD2_RED_OK"
```

Use VirtualBox's `VBoxManage snapshot` command; never a filesystem copy.
