param([string]$Log='C:\ProgramData\SP11CamCal\chart-log.txt')
# Static ISP test chart (own design): slanted edges, star, gratings, colour patches, grey wedge.
# Shown full screen until C:\ProgramData\SP11CamCal\STOP exists.
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
Add-Type -Name Dpi -Namespace W -MemberDefinition '[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();'
[W.Dpi]::SetProcessDPIAware() | Out-Null
$stop='C:\ProgramData\SP11CamCal\STOP'
Remove-Item $stop -ErrorAction SilentlyContinue
$s=[Windows.Forms.Screen]::PrimaryScreen.Bounds
$W=$s.Width;$H=$s.Height
$bmp=New-Object Drawing.Bitmap $W,$H
$g=[Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode='AntiAlias'
function B($r,$gg,$b){New-Object Drawing.SolidBrush ([Drawing.Color]::FromArgb($r,$gg,$b))}
$g.FillRectangle((B 118 118 118),0,0,$W,$H)
# Layout fits the top ~60% of the screen (the part the SP11 front camera sees).
# row A: slanted-edge squares | Siemens star | vertical + horizontal gratings
$g.FillRectangle((B 235 235 235),[int](0.03*$W),[int](0.03*$H),[int](0.30*$W),[int](0.27*$H))
foreach($c in @(@(0.105,0.165),@(0.255,0.165))){
  $st=$g.Save()
  $g.TranslateTransform([single]($c[0]*$W),[single]($c[1]*$H));$g.RotateTransform(5)
  $q=[single](0.17*$H);$g.FillRectangle((B 20 20 20),-$q/2,-$q/2,$q,$q)
  $g.Restore($st)}
$cx=0.47*$W;$cy=0.165*$H;$R=0.135*$H
$g.FillEllipse((B 235 235 235),[single]($cx-$R),[single]($cy-$R),[single](2*$R),[single](2*$R))
for($k=0;$k -lt 36;$k++){
  $a0=$k*10*[Math]::PI/180;$a1=($k*10+5)*[Math]::PI/180
  $pts=[Drawing.PointF[]]@((New-Object Drawing.PointF ([single]$cx),([single]$cy)),
    (New-Object Drawing.PointF ([single]($cx+$R*[Math]::Cos($a0))),([single]($cy+$R*[Math]::Sin($a0)))),
    (New-Object Drawing.PointF ([single]($cx+$R*[Math]::Cos($a1))),([single]($cy+$R*[Math]::Sin($a1)))))
  $g.FillPolygon((B 20 20 20),$pts)}
$g.SmoothingMode='None'
$periods=@(8,12,16,24,32);$gx0=[int](0.62*$W);$gw=[int](0.35*$W/5)
for($i=0;$i -lt 5;$i++){
  $p=$periods[$i];$x0=$gx0+$i*$gw
  $y0=[int](0.03*$H);$y1=[int](0.155*$H)
  $g.FillRectangle((B 235 235 235),$x0,$y0,$gw-8,$y1-$y0)
  for($x=$x0;$x -lt $x0+$gw-8;$x+=$p){$g.FillRectangle((B 20 20 20),$x,$y0,[int]($p/2),$y1-$y0)}
  $y0=[int](0.175*$H);$y1=[int](0.30*$H)
  $g.FillRectangle((B 235 235 235),$x0,$y0,$gw-8,$y1-$y0)
  for($y=$y0;$y -lt $y1;$y+=$p){$g.FillRectangle((B 20 20 20),$x0,$y,$gw-8,[int]($p/2))}}
# row B: colour patches
$cols=@(@(200,30,30),@(30,170,40),@(30,50,200),@(30,180,200),@(190,40,180),@(220,210,30),
        @(225,170,140),@(150,100,75),@(95,125,180),@(85,110,50),@(230,130,30),@(100,60,150))
$pw=0.94*$W/12
for($i=0;$i -lt 12;$i++){$c=$cols[$i]
  $g.FillRectangle((B $c[0] $c[1] $c[2]),[int](0.03*$W+$i*$pw+6),[int](0.32*$H),[int]($pw-12),[int](0.12*$H))}
# row C: grey wedge, 12 steps
$sw=0.94*$W/12
for($i=0;$i -lt 12;$i++){$v=[int][Math]::Round(255*[Math]::Pow($i/11,2.2))
  $g.FillRectangle((B $v $v $v),[int](0.03*$W+$i*$sw),[int](0.46*$H),[int]([Math]::Ceiling($sw)),[int](0.13*$H))}
$g.Dispose()
$f=New-Object Windows.Forms.Form
$f.FormBorderStyle='None';$f.StartPosition='Manual';$f.TopMost=$true;$f.ShowInTaskbar=$false
$f.Bounds=$s;$f.BackgroundImage=$bmp;$f.BackgroundImageLayout='None'
$t=New-Object Windows.Forms.Timer;$t.Interval=1000
$t.Add_Tick({if(Test-Path $stop){$f.Close()}})
$f.Add_Shown({[Windows.Forms.Cursor]::Hide();$t.Start();('shown,{0},{1}x{2}' -f [DateTime]::UtcNow.ToString('o'),$W,$H) | Set-Content $Log})
[Windows.Forms.Application]::Run($f)
('closed,{0}' -f [DateTime]::UtcNow.ToString('o')) | Add-Content $Log
