
## Custom parameters below
udn = '/dev/ttyUSB-MBUS'                        #UsbDeviceName where M-BUS adapter is attached
dd = "/home/pi/domoticz/scripts/data/"          #Data Directory where static outputdatafiles is saved
ddr = "/home/pi/domoticz/scripts/data/ramdisk/"  #Data Directory where temporary outputdatafiles is saved
whlhf = dd + 'whlasthour.txt'                   #WattHourLastHourFile
whf = dd + 'whnow.txt'                          #WattHourFile
enf = ddr + 'elunow.txt'                         #ElusageNowFile
al1f = ddr + 'al1now.txt'                        #AmpereL1phaseFile
al2f = ddr + 'al2now.txt'                        #AmpereL2phaseFile
al3f = ddr + 'al3now.txt'                        #AmpereL3phaseFile
vl1f = ddr + 'vl1now.txt'                        #VoltsL1phaseFile
vl2f = ddr + 'vl2now.txt'                        #VoltsL2phaseFile
vl3f = ddr + 'vl3now.txt'                        #VoltsL3phaseFile

epnf = dd + 'elpnow.txt'                          #ElPriceNowFile   ---------- ved fastpris, bytt til fastpris.txt
enfw ='/var/www/html/ramdisk/elunow.txt'            #ElusageNowFileforWWWserver
ecfw ='/var/www/html/ramdisk/elcnow.txt'            #ElCostNowFileforWWWserver
lf = dd + 'errorlog.txt'                            #LogFile

nl = 18.50 #Nettleie pr. kwh i øre uten moms
fa = 17.69 #Forbruks- og enova-avgift pr. kwh i øre uten moms
sps = 0 #Spotpris påslag pr. kwh i øre uten moms     -------------- fastpris fra 6.12.2021
mva = 1.25 #Momsfaktor på totalprisen

## Custom parameters above



# Explanation of short variables used
# fl=FrameLength  hs=HexString hsa=HexStringAll h1=Hexvalue1instring h2=Hexvalue2 h3=Hexvalue3 hxval=HeXVALue dval=DecimalVALue

import serial
import binascii
import time

ser = serial.Serial(udn, baudrate=2400, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=None, xonxoff=False, rtscts=False, dsrdtr=False)

while True:
#    time.sleep(0.01)
    h1 = binascii.hexlify(ser.read()).decode('utf-8')
    h2 = binascii.hexlify(ser.read()).decode('utf-8')
    if h1 == "7e" and h2 == "a0":
        h3 = binascii.hexlify(ser.read()).decode('utf-8')
        if h3 == "27":   #A Hexvalue3 of 27 indicates a data frame of 39 hexcharacters containing only poweusage sendt every 2 seconds.  
            fl = int(h3, 16)-1
            hsa = h1 + h2 + h3
            loop = 0
            while loop < fl:
                hs = binascii.hexlify(ser.read()).decode('utf-8')
                hsa = hsa + hs
                loop = loop + 1
            if hs == "7e":
                print(hsa)
                hxval = hsa[68:76]
                dval = int(hxval, 16)
                print(dval)
                with open(enf, 'w') as f:
                    f.write(str(dval))
                with open(enfw, 'w') as f:
                    f.write(str(dval/1000))
                with open(epnf) as f: 
                    price = float(f.readline())
                with open(ecfw, 'w') as f:
                    f.write(str(dval*0.024*(nl+fa+sps+price)*mva/100))
            else: 
                with open(lf, 'a') as f:
                    print('Frame error. Frame with lenght ' + str(fl) + ' ended with ' + hs +'. Expecting 7e.')
                    f.write('Frame error. Frame with lenght ' + str(fl) + ' ended with ' + hs +'. Expecting 7e.'+'\n')
                    
        if h3 == "79":   #Indicates a data frame of 121 caracters containing poweusage, amperes and voltages sendt every 10 seconds.
            fl = int(h3, 16)-1
            hsa = h1 + h2 + h3
            loop = 0
            while loop < fl:
                hs = binascii.hexlify(ser.read()).decode('utf-8')
                hsa = hsa + hs
                loop = loop + 1
            if hs == "7e":
                print(hsa)
                hxval = hsa[142:150]
                dval = int(hxval, 16)
                print(dval)
                with open(enf, 'w') as f:
                    f.write(str(dval))
                with open(enfw, 'w') as f:
                    f.write(str(dval/1000))
                with open(epnf) as f: 
                    price = float(f.readline())
                with open(ecfw, 'w') as f:
                    f.write(str(dval*0.024*(nl+fa+sps+price)*mva/100))
                hxval = hsa[182:190]
                dval = int(hxval, 16)/1000
                print(dval)
                with open(al1f, 'w') as f:
                    f.write(str(dval))
                hxval = hsa[192:200]
                dval = int(hxval, 16)/1000
                print(dval)
                with open(al2f, 'w') as f:
                    f.write(str(dval))
                hxval = hsa[202:210]
                dval = int(hxval, 16)/1000
                print(dval)
                with open(al3f, 'w') as f:
                    f.write(str(dval))
                hxval = hsa[212:220]
                dval = int(hxval, 16)/10
                print(dval)
                with open(vl1f, 'w') as f:
                    f.write(str(dval))
                hxval = hsa[222:230]
                dval = int(hxval, 16)/10
                print(dval)
                with open(vl2f, 'w') as f:
                    f.write(str(dval))
                hxval = hsa[232:240]
                dval = int(hxval, 16)/10
                print(dval)
                with open(vl3f, 'w') as f:
                    f.write(str(dval))
            else: 
                with open(lf, 'a') as f:
                    print('Frame error. Frame with lenght ' + str(fl) + ' ended with ' + hs +'. Expecting 7e.')
                    f.write('Frame error. Frame with lenght ' + str(fl) + ' ended with ' + hs +'. Expecting 7e.'+'\n')

        if h3 == "9b":   #Indicates a data frame of 155 caracters containing poweusage, amperes, voltages and watthours send every hour.
            fl = int(h3, 16)-1
            hsa = h1 + h2 + h3
            loop = 0
            while loop < fl:
                hs = binascii.hexlify(ser.read()).decode('utf-8')
                hsa = hsa + hs
                loop = loop + 1
            if hs == "7e":
                print(hsa)
                hxval = hsa[142:150]
                dval = int(hxval, 16)
                print(dval)
                with open(enf, 'w') as f:
                    f.write(str(dval))
                with open(enfw, 'w') as f:
                    f.write(str(dval/1000))
                with open(epnf) as f: 
                    price = float(f.readline())
                with open(ecfw, 'w') as f:
                    f.write(str(dval*0.024*(nl+fa+sps+price)*mva/100))
                hxval = hsa[182:190]
                dval = int(hxval, 16)/1000
                print(dval)
                with open(al1f, 'w') as f:
                    f.write(str(dval))
                hxval = hsa[192:200]
                dval = int(hxval, 16)/1000
                print(dval)
                with open(al2f, 'w') as f:
                    f.write(str(dval))
                hxval = hsa[202:210]
                dval = int(hxval, 16)/1000
                print(dval)
                with open(al3f, 'w') as f:
                    f.write(str(dval))
                hxval = hsa[212:220]
                dval = int(hxval, 16)/10
                print(dval)
                with open(vl1f, 'w') as f:
                    f.write(str(dval))
                hxval = hsa[222:230]
                dval = int(hxval, 16)/10
                print(dval)
                with open(vl2f, 'w') as f:
                    f.write(str(dval))
                hxval = hsa[232:240]
                dval = int(hxval, 16)/10
                print(dval)
                with open(vl3f, 'w') as f:
                    f.write(str(dval))
                hxval = hsa[270:278]
                dval = int(hxval, 16)
                print(dval)
                from shutil import copyfile
                copyfile(whf, whlhf)
                with open(whf, 'w') as f:
                    f.write(str(dval))                   
            else: 
                with open(lf, 'a') as f:
                    print('Frame error. Frame with lenght ' + str(fl) + ' ended with ' + hs +'. Expecting 7e.')
                    f.write('Frame error. Frame with lenght ' + str(fl) + ' ended with ' + hs +'. Expecting 7e.'+'\n')

