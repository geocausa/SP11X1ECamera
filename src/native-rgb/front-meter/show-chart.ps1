# SPDX-License-Identifier: MIT
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
Add-Type -Name DpiFrontChart -Namespace SP11 -MemberDefinition '[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();'
[SP11.DpiFrontChart]::SetProcessDPIAware() | Out-Null
$root=$PSScriptRoot
$f=New-Object Windows.Forms.Form
$f.Text='SP11 front camera fixed chart';$f.FormBorderStyle='None';$f.StartPosition='Manual'
$f.TopMost=$true;$f.ShowInTaskbar=$false;$f.KeyPreview=$true
$s=[Windows.Forms.Screen]::PrimaryScreen.Bounds;$f.Bounds=$s;$f.BackColor=[Drawing.Color]::FromArgb(128,128,128)
$f.Add_Paint({param($sender,$ev)
 $g=$ev.Graphics;$w=$f.ClientSize.Width;$h=$f.ClientSize.Height
 $colors=@(@(0,0,0),@(32,32,32),@(64,64,64),@(128,128,128),@(192,192,192),@(255,255,255))
 for($i=0;$i -lt 6;$i++){
  $c=$colors[$i];$brush=New-Object Drawing.SolidBrush ([Drawing.Color]::FromArgb($c[0],$c[1],$c[2]))
  try{$g.FillRectangle($brush,[int]($w*(0.08+$i*0.14)),[int]($h*0.12),[int]($w*0.12),[int]($h*0.25))}finally{$brush.Dispose()}
 }
 $colors=@(@(255,0,0),@(0,255,0),@(0,0,255),@(255,255,0),@(0,255,255),@(255,0,255))
 for($i=0;$i -lt 6;$i++){
  $c=$colors[$i];$brush=New-Object Drawing.SolidBrush ([Drawing.Color]::FromArgb($c[0],$c[1],$c[2]))
  try{$g.FillRectangle($brush,[int]($w*(0.08+$i*0.14)),[int]($h*0.43),[int]($w*0.12),[int]($h*0.22))}finally{$brush.Dispose()}
 }
 $g.DrawRectangle([Drawing.Pens]::White,[int]($w*0.04),[int]($h*0.04),[int]($w*0.92),[int]($h*0.66))
 $g.DrawLine([Drawing.Pens]::Black,[int]($w*0.07),[int]($h*0.07),[int]($w*0.20),[int]($h*0.07))
})
$f.Add_KeyDown({param($sender,$ev) if($ev.KeyCode -eq 'Escape'){$f.Close()}})
$timer=New-Object Windows.Forms.Timer;$timer.Interval=1200000;$timer.Add_Tick({$f.Close()})
$f.Add_Shown({
 $f.Refresh();$timer.Start()
 [ordered]@{status='FIXED_CHART_SHOWN';utc=[DateTime]::UtcNow.ToString('o');width=$s.Width;height=$s.Height;user=[Environment]::UserName;unchanged_display_brightness=(Get-CimInstance -Namespace root\wmi -Class WmiMonitorBrightness | Select-Object -ExpandProperty CurrentBrightness)} | ConvertTo-Json | Set-Content (Join-Path $root 'SHOWN.json')
})
try{[Windows.Forms.Application]::Run($f)}finally{$timer.Dispose();$f.Dispose();[DateTime]::UtcNow.ToString('o') | Set-Content (Join-Path $root 'CLOSED.txt')}
