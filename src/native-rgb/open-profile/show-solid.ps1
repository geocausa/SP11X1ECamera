# SPDX-License-Identifier: MIT
# Full-screen solid colour for SP11 flat-field / dark-frame captures.
# The colour is read from C:\ProgramData\SP11CamCal\solid.txt (r,g,b) every 200 ms,
# so a capture script can switch white/black without restarting the window.
# Shown until C:\ProgramData\SP11CamCal\STOP exists.
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
Add-Type -Name Dpi -Namespace W -MemberDefinition '[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();'
[W.Dpi]::SetProcessDPIAware() | Out-Null
$dir='C:\ProgramData\SP11CamCal'
$stop=Join-Path $dir 'STOP'
$cfg=Join-Path $dir 'solid.txt'
Remove-Item $stop -ErrorAction SilentlyContinue
if(-not (Test-Path $cfg)){Set-Content -Path $cfg -Value '255,255,255'}
$f=New-Object Windows.Forms.Form
$f.FormBorderStyle='None';$f.WindowState='Maximized';$f.TopMost=$true;$f.Cursor=[Windows.Forms.Cursors]::No
$f.BackColor=[Drawing.Color]::White
$script:last='';$t=New-Object Windows.Forms.Timer;$t.Interval=200
$t.Add_Tick({
  if(Test-Path $stop){$t.Stop();$f.Close();return}
  try{$raw=(Get-Content $cfg -Raw).Trim()
      if($raw -ne $script:last){$c=$raw.Split(',')|ForEach-Object{[int]$_}
        $f.BackColor=[Drawing.Color]::FromArgb($c[0],$c[1],$c[2]);$script:last=$raw
        Add-Content -Path (Join-Path $dir 'solid-log.txt') -Value ("{0:o} {1}" -f [DateTimeOffset]::UtcNow,$raw)}}catch{}
})
$t.Start()
[Windows.Forms.Cursor]::Hide()
[Windows.Forms.Application]::Run($f)
