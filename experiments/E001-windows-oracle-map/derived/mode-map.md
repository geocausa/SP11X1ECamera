# E001 static oracle — Windows sensor transport modes

All normal listed streams are VC0 / CSI-2 data type `0x2b` / RAW10. Values below come from the selected local QTI sensor packages.

## IMX681 front RGB

| # | Crop start | Output | FPS | line length | frame length | output pixel clock |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 104,256 | 3840x2640 | 30 | 6752 | 3554 | 548.57 MHz |
| 1 | 104,496 | 3840x2160 | 60 | 5408 | 2218 | 548.57 MHz |
| 2 | 104,496 | 3840x2160 | 30 | 6752 | 3554 | 548.57 MHz |
| 3 | 264,256 | 3520x2640 | 30 | 6752 | 3554 | 548.57 MHz |
| 4 | 192,356 | 3660x2440 | 30 | 6752 | 3554 | 548.57 MHz |
| 5 | 8,64 | 504x378 | 3 | 3096 | 77518 | 655.71 MHz |

Mode 5 is clearly special-purpose; do not use it as the first Linux capture target.

## OV13858 rear RGB

All at 30 FPS, output pixel clock 474.24 MHz:
- mode 0: 4076x2806 from (0,0)
- mode 1: 4064x2286 from (6,260)
- mode 2: 3736x2802 from (170,2)

The package reports line-length value 1122 and frame length 3214. Since 1122 is smaller than output width, preserve this value as a sensor/QTI timing unit rather than assuming it is literal output pixels until correlated with sensor registers.

## VD55G0 IR
- 644x604 RAW10 VC0
- 60 FPS
- line length 1200
- frame length 1955
- min blanking 64/64
- output pixel clock 84 MHz
