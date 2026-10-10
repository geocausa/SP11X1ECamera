# SPDX-License-Identifier: MIT
param([switch]$SelfTest,[int]$FixtureWidth=2736,[int]$FixtureHeight=1824)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
Add-Type -Name DpiFrontChart -Namespace SP11 -MemberDefinition '[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();'
[SP11.DpiFrontChart]::SetProcessDPIAware() | Out-Null
$root=$PSScriptRoot
$f=New-Object Windows.Forms.Form
$f.Text='SP11 front camera coded chart';$f.FormBorderStyle='None';$f.StartPosition='Manual'
$f.TopMost=$true;$f.ShowInTaskbar=$false;$f.KeyPreview=$true
$s=[Windows.Forms.Screen]::PrimaryScreen.Bounds;$f.Bounds=$s;$f.BackColor=[Drawing.Color]::FromArgb(128,128,128)
$paint={param($sender,$ev)
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
 # Four public ArUco DICT_4X4_1000 IDs, quiet zones and healthy-upper layout.
 $patterns=@('000000001100001100000000000000000000','000000011100010010001010011010000000','000000001000001000001010011110000000','000000000100001010011100001110000000')
 $xs=@(0.008,0.932,0.932,0.008);$ys=@(0.04,0.04,0.58,0.58)
 $size=[int]($w*0.06);$quiet=[int]($size/6)
 for($tag=0;$tag -lt 4;$tag++){
  $tx=[int]($w*$xs[$tag]);$ty=[int]($h*$ys[$tag])
  $g.FillRectangle([Drawing.Brushes]::White,$tx-$quiet,$ty-$quiet,$size+2*$quiet,$size+2*$quiet)
  for($row=0;$row -lt 6;$row++){for($col=0;$col -lt 6;$col++){
   $brush=if($patterns[$tag][$row*6+$col] -eq '1'){[Drawing.Brushes]::White}else{[Drawing.Brushes]::Black}
   $x0=[int][Math]::Ceiling($col*$size/6);$x1=[int][Math]::Ceiling(($col+1)*$size/6)
   $y0=[int][Math]::Ceiling($row*$size/6);$y1=[int][Math]::Ceiling(($row+1)*$size/6)
   $g.FillRectangle($brush,$tx+$x0,$ty+$y0,$x1-$x0,$y1-$y0)
  }}
 }
}
$f.Add_Paint($paint)

if($SelfTest){
 if($FixtureWidth -le 0 -or $FixtureHeight -le 0){throw 'Positive fixture dimensions required'}
 $s=New-Object Drawing.Rectangle (0,0,$FixtureWidth,$FixtureHeight)
 $f.ClientSize=New-Object Drawing.Size ($FixtureWidth,$FixtureHeight)
 $bitmap=New-Object Drawing.Bitmap ($s.Width,$s.Height)
 $graphics=[Drawing.Graphics]::FromImage($bitmap);$graphics.Clear([Drawing.Color]::FromArgb(128,128,128))
 try{
  $event=New-Object Windows.Forms.PaintEventArgs ($graphics,(New-Object Drawing.Rectangle (0,0,$s.Width,$s.Height)))
  & $paint $f $event
  $patterns=@('000000001100001100000000000000000000','000000011100010010001010011010000000','000000001000001000001010011110000000','000000000100001010011100001110000000')
  $xs=@(0.008,0.932,0.932,0.008);$ys=@(0.04,0.04,0.58,0.58);$size=[int]($s.Width*.06);$count=0
  for($tag=0;$tag -lt 4;$tag++){for($row=0;$row -lt 6;$row++){for($col=0;$col -lt 6;$col++){
   $x=[int]($s.Width*$xs[$tag])+[int](($col+.5)*$size/6)
   $y=[int]($s.Height*$ys[$tag])+[int](($row+.5)*$size/6)
   $expected=if($patterns[$tag][$row*6+$col] -eq '1'){255}else{0}
   if($bitmap.GetPixel($x,$y).R -ne $expected){throw 'Coded chart GDI cell mismatch'};$count++
  }}}
  [ordered]@{status='PASS_CODED_CHART_GDI_SELFTEST';assertions=$count;display_opened=$false;camera_access=$false;width=$s.Width;height=$s.Height}|ConvertTo-Json -Compress
 }finally{$graphics.Dispose();$bitmap.Dispose();$f.Dispose()}
 return
}
$f.Add_KeyDown({param($sender,$ev) if($ev.KeyCode -eq 'Escape'){$f.Close()}})
$timer=New-Object Windows.Forms.Timer;$timer.Interval=1200000;$timer.Add_Tick({$f.Close()})
$f.Add_Shown({
 $f.Refresh();$timer.Start()
 [ordered]@{status='FIXED_CHART_SHOWN';utc=[DateTime]::UtcNow.ToString('o');width=$s.Width;height=$s.Height;user=[Environment]::UserName;unchanged_display_brightness=(Get-CimInstance -Namespace root\wmi -Class WmiMonitorBrightness | Select-Object -ExpandProperty CurrentBrightness)} | ConvertTo-Json | Set-Content (Join-Path $root 'SHOWN.json')
})
try{[Windows.Forms.Application]::Run($f)}finally{$timer.Dispose();$f.Dispose();[DateTime]::UtcNow.ToString('o') | Set-Content (Join-Path $root 'CLOSED.txt')}
