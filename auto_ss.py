import os
import pyautogui as gui
import sys
import time
import numpy as np
import cv2
import img2pdf
from PIL import Image # img2pdfと一緒にインストールされたPillowを使います
from tkinter import messagebox
from natsort import natsorted


#### 実行形式でのpath取得
#path_current_dir = os.path.dirname(sys.argv[0])

# script実行時のパス
path_current_dir = os.path.dirname(os.path.abspath(__file__))
Bookname = ""

print('中断するにはCrt+Cを入力してください。\n')

InFlg = 0

#### ファイル名の入力
while True:
    try:
        Bookname = input("ファイル名を入力してください\n")
    except ValueError as ex:
        if Bookname == "":
            print(end= "")
        else:
            print("ファイル名として有効な文字列を入力してください\n")
    except TypeError:
        print()
    else:
        break

#### 座標の取得
try:
    while True:
        if InFlg == 0:
            x=input("キャプチャしたい画像の左上にカーソルを当てEnterキー押してください\n")
            XLeftTop,YLeftTop = gui.position()
            InFlg += 1

        if InFlg == 1:
            x=input("キャプチャしたい画像の右下にカーソルを当てEnterキー押してください\n")
            XRightLow,YRightLow = gui.position()
            InFlg += 1
        
        if InFlg == 2:
            cursol=input("ページ送り方向を指定してください(→:1 / ←:2)'\n")
            if cursol == "1":
                cursol = "right"
                InFlg += 1
            elif cursol == "2":
                cursol="left"
                InFlg += 1
        
        if InFlg == 3:
            Fileflg=input("ファイル出力を選択してください(1:PNG 2:Jpeg+PDF)\n")
            if Fileflg  == "1":
                InFlg += 1
            elif Fileflg == "2":
                InFlg += 1

        if InFlg == 4:
            x=input("Enterを押下した後、5秒以内にキャプチャしたい画面を全面に表示し待機してください。\n")
            InFlg += 1

        if InFlg == 5:
            break
except KeyboardInterrupt:
    print('\n終了')
    sys.exit()

Savedir = path_current_dir + "/" + Bookname #+ "/"
os.mkdir(Savedir)

Savedir += "/"

#### キャプチャ範囲の幅と高さを格納
Width =  XRightLow - XLeftTop
Height =  YRightLow - YLeftTop

#### 実行開始までのwait
time.sleep(5)

Pagecount = 1

while True:
    time.sleep(0.3)
    Pagenum = str(Pagecount).zfill(4)
    # #region = (左からの配置位置, 上からの配置位置, 幅, 高さ)
    SS = gui.screenshot(region = (XLeftTop,YLeftTop,Width,Height))
    if Fileflg == "2" :
        SS = SS.convert('RGB')

    #### 2ページ以降は前回のキャプチャ内容と比較する
    if Pagecount >= 2:

        # 前回のキャプチャ内容と今回のキャプチャを比較、一致したあと再度比較し終了判定へ
        if np.array_equal(SS,BeforeSS):#pylint: disable-this-line-in-some-way
            time.sleep(3)
            SS = gui.screenshot(region = (XLeftTop,YLeftTop,Width,Height))
            if Fileflg == "2" :
                SS = SS.convert('RGB')

            #### キャプチャ終了判定
            if np.array_equal(SS,BeforeSS):
                print("キャプチャ画像が一致したので終了します")
                break

    if Fileflg == "1":
        Fname = Savedir + Bookname + '_' + str(Pagenum) + '.png'
    elif Fileflg == "2":
        Fname = Savedir + Bookname + '_' + str(Pagenum) + '.jpg'
    SS.save(Fname)
    BeforeSS = SS
    Pagecount += 1
    gui.press(cursol)
    time.sleep(0.5)

if Fileflg =="2":
    #### pdf変換
    print("PDF化を開始します")

    pdf_FileName = Savedir + Bookname + '.pdf' # 出力するPDFの名前
    png_Folder = Savedir # 画像フォルダ
    extension  = ".jpg" # 拡張子がPNGのものを対象


    #PDF化ファイルのソート
    jpg_Finelame = []
    for i in os.listdir(png_Folder):
        if i[-3:] == "jpg":
            jpg_Finelame.append(i)
    sorted_jpg = natsorted(jpg_Finelame)



    with open(pdf_FileName,"wb") as f:
        # 画像フォルダの中にあるPNGファイルを取得し配列に追加、バイナリ形式でファイルに書き込む
        f.write(img2pdf.convert([Image.open(png_Folder+j).filename for j in sorted_jpg]))
        #f.write(img2pdf.convert([Image.open(png_Folder+j).filename for j in os.listdir(png_Folder)if j.endswith(extension)]))

    print("PDF化完了しました")
messagebox.showinfo("完了", "キャプチャが完了しました")
