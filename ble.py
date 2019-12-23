# -*- coding: utf-8 -*-
# 環境センサーをLimited Broadcasterモードにして
# 10秒アドバタイズ、290秒休み(開発中は50秒休み)に設定
# 常時スキャンし、データーを取得したらAmbientに送信する
# 1台(Single)のセンサー端末に対応

from bluepy.btle import Peripheral, DefaultDelegate, Scanner, BTLEException, UUID
import bluepy.btle
import sys
import struct
from datetime import datetime
import argparse
import ambient
import requests
import time
import csv

channelID = 100
writeKey = 'writeKey'
am = ambient.Ambient(channelID, writeKey)

devs = {
    'omron': {'companyID': 'd502'},
    'esp32': {'companyID': 'ffff'}
}
target = 'esp32'

Debugging = False

Verbose = True
def dataInput(*args):
    with open('data.csv', 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerow(data)

def send2ambient(dataRow):
    if companyID == 'ffff':
        (temp, humid, press) = struct.unpack('<hhh', bytes.fromhex(dataRow))
        dataInput(temp / 100, humid / 100, press / 10)
        sendWithRetry({'d1': temp / 100, 'd2': humid / 100, 'd3': press / 10})


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self.lastseq = None
        self.lasttime = datetime.fromtimestamp(0)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev or isNewData:
            for (adtype, desc, value) in dev.getScanData():
                # print(adtype, desc, value)
                if target in ('omron', 'esp32'):
                    if desc == 'Manufacturer' and value[0:4] == devs[target]['companyID']:
                        delta = datetime.now() - self.lasttime
                        if value[4:6] != self.lastseq and delta.total_seconds() > 11: # アドバタイズする10秒の間に測定が実行されseqが加算されたものは捨てる
                            self.lastseq = value[4:6]
                            self.lasttime = datetime.now()
                            send2ambient(value[6:])
def main():

    scanner = Scanner().withDelegate(ScanDelegate())
    scanner.scan(5.0) # スキャンする。デバイスを見つけた後の処理はScanDelegateに任せる
if __name__ == "__main__":
    main()