#!/usr/bin/python
# coding: UTF-8
###########################################################################
#  (C) Mono Wireless Inc. - all rights reserved.
# 利用条件:
#   - 本ソースコードは、別途ソースコードライセンス記述が無い限りモノワイヤレス株式会社が
#     著作権を保有しています。
#   - 本ソースコードは、無保証・無サポートです。本ソースコードや生成物を用いたいかなる損害
#     についてもモノワイヤレス株式会社は保証致しません。不具合等の報告は歓迎いたします。
#   - 本ソースコードは、モノワイヤレス株式会社が販売する TWE シリーズと共に実行する前提で公開
#     しています。
###########################################################################
### TWELITE 標準アプリケーションを読み・書きするスクリプト
# [読み]
#   シリアルポートから出力される :??81???? データを読みだし、内容を解釈します。
# [書き]
#   標準入力に対し１行入力します。
#   q[Enter] --> 終了
#   :??????[Enter] --> : コマンドの出力
from serial import *
from sys import stdout, stdin, stderr, exit
import threading
# global 変数の定義
ser = None # シリアルポート
t1 = None  # 読み出しスレッド
bTerm = False # 終了フラグ
# その他のメッセージの表示 (ペイロードをそのまま出力)
def printPayload(l):
    if len(l) < 3: return False # データサイズのチェック
    
    print (" command = 0x%02x (other)" % l[1])
    print ("  src     = 0x%02x" % l[0])
    
    # ペイロードをそのまま出力する
    print ("  payload =",)
    for c in l[2:]:
        print ("%02x" % c,)
    print ("(hex)")
    return True
        
# 0x81 メッセージの解釈と表示
def printPayload_0x81(l):
    if len(l) != 23: return False # データサイズのチェック
    
    ladr = l[5] << 24 | l[6] << 16 | l[7] << 8 | l[8]
    print ("  command   = 0x%02x (data arrival)" % l[1])
    print ("  src       = 0x%02x" % l[0])
    print ("  src long  = 0x%08x" % ladr)
    print ("  dst       = 0x%02x" % l[9])
    print ("  pktid     = 0x%02x" % l[2])
    print ("  prtcl ver = 0x%02x" % l[3])
    print ("  LQI       = %d / %.2f [dbm]" % (l[4], (7*l[4]-1970)/20.))
    ts = l[10] << 8 | l[11]
    print ("  time stmp = %.3f [s]" % (ts / 64.0))
    print ("  relay flg = %d" % l[12])
    vlt = l[13] << 8 | l[14]
    print ("  volt      = %04d [mV]" % vlt)
    
    # DI1..4 のデータ
    dibm = l[16]
    dibm_chg = l[17]
    di = {} # 現在の状態
    di_chg = {} # 一度でもLo(1)になったら1
    for i in range(1,5):
        di[i] = 0 if (dibm & 0x1) == 0 else 1
        di_chg[i] = 0 if (dibm_chg & 0x1) == 0 else 1
        dibm >>= 1
        dibm_chg >>= 1
    
    print ("  DI1=%d/%d  DI2=%d/%d  DI3=%d/%d  DI4=%d/%d" % (di[1], di_chg[1], di[2], di_chg[2], di[3], di_chg[3], di[4], di_chg[4]))
    
    # AD1..4 のデータ
    ad = {}
    er = l[22]
    for i in range(1,5):
        av = l[i + 18 - 1]
        if av == 0xFF:
            # ADポートが未使用扱い(おおむね2V以)なら -1
            ad[i] = -1
        else:
            # 補正ビットを含めた計算
            ad[i] = ((av * 4) + (er & 0x3)) * 4
        er >>= 2
    print ("  AD1=%04d AD2=%04d AD3=%04d AD4=%04d [mV]" % (ad[1], ad[2], ad[3], ad[4]))
    
    return True
# シリアルポートからのデータを１行ずつ解釈するスレッド
def readThread():
    global ser, bTerm
    while True:
        if bTerm: return # 終了処理
        line = ser.readline().rstrip() # １ライン単位で読み出し、末尾の改行コードを削除（ブロッキング読み出し）
        
        bCommand = False
        bStr = False
        
        if len(line) > 0:
            c = line[0]
            if isinstance(c, str):
                if c == ':': bCommand = True
                bStr = True
            else:
                # python3 では bytes 型になる
                if c == 58: bCommand = True
                
            print ("\n%s" % line)
        
        if not bCommand: continue
    
        try:
            lst = {}
            if bStr:
                # for Python2.7
                lst = map(ord, line[1:].decode('hex')) # HEX文字列を文字列にデコード後、各々 ord() したリスト(list)に変換
            else:
                # for Python3
                import codecs
                s = line[1:].decode("ascii") # bytes -> str 変換
                lst = codecs.decode(s, "hex_codec") # hex_codec でバイト列に変換 (bytes)
                
            csum = sum(lst) & 0xff # チェックサムは 8bit 計算で全部足して　0 なら OK
            lst = lst[0:len(lst)-1] # チェックサムをリストから削除 (python3ではpopが使えない)
            if csum == 0:
                if lst[1] == 0x81:
                    printPayload_0x81(lst) # IO関連のデータの受信
                else:
                    printPayload(lst) # その他のデータ受信
            else:
                print ("checksum ng")
        except:
            if len(line) > 0:
                print ("...skip (%s)" % line) # エラー時
# 終了処理
def DoTerminate():
    global t1, bTerm
    # スレッドの停止
    bTerm = True
    
    print ("... quitting")
    time.sleep(0.5) # スリープでスレッドの終了待ちをする
        
    exit(0)
# 主処理
if __name__=='__main__':
    # パラメータの確認
    #   第一引数: シリアルポート名
    if len(sys.argv) != 2:
        print ("%s {serial port name}" % sys.argv[0])
        exit(1)
    
    # シリアルポートを開く
    try:
        ser = Serial(sys.argv[1], 115200, timeout=0.1)
        print ("open serial port: %s" % sys.argv[1])
    except:
        print ("cannot open serial port: %s" % sys.argv[1])
        exit(1)
        
    # 読み出しスレッドの開始
    t1=threading.Thread(target=readThread)
    t1.setDaemon(True)
    t1.start()
    
    # stdin からの入力処理
    while True:
        try:
            # 標準入力から１行読みだす
            l = stdin.readline().rstrip()
            
            if len(l) > 0:
                if l[0] == 'q': # q を入力すると終了
                    DoTerminate()
                    
                if l[0] == ':': # :からの系列はそのままコマンドの送信
                    cmd = l + "\r\n"
                    print ("--> "+ l)
                    ser.write(cmd)
        except KeyboardInterrupt: # Ctrl+C
            DoTerminate()
        except SystemExit:
            exit(0)
        except:
            # 例外発生時には終了
            print ("... unknown exception detected")
            break
    
    # 念のため
    exit(0)
