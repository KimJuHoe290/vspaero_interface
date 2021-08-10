# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 21:54:46 2021

@author: kim03
"""
## VSPAEROの.history ファイルを読み込んでMATLABで取り扱いやすい形式に整理する
## .stab もまとめて処理する

import numpy as np
import scipy.io
import sys

args = sys.argv
FILENAME = args[1] # 

##########################################################################
####################.history の処理########################################
##########################################################################
FILENAME_h = FILENAME+".history"

f_h=open(FILENAME_h) # ファイルを開く
Lists_h=f_h.readlines() # ファイル全てを行ごとに区切って読み込む
Lists_h=[line.strip() for line in Lists_h] #改行文字を消す

SPLIT_REF = "***********************************************************\
*************************************************************************\
*****************************************************"
# 情報分割に使用する文字列

# SPLIT_REF を探す
count = 0
REF_NUM = [] # SPLIT_REF がある場所のリスト

for i in Lists_h:
    if(i==SPLIT_REF):
        REF_NUM.append(count)
    count = count + 1    

TOTAL_CASE = len(REF_NUM) # 実行ケース総数
END_POINT  = len(Lists_h)-1
REF_NUM.append(END_POINT) # リストの最終行の番号
LISTS_CHUNK = [Lists_h[REF_NUM[i]:REF_NUM[i+1]-1] for i in range(0,TOTAL_CASE)]
LISTS_RESULTS = [] # 

TARGET_REF = 'Iter      Mach       AoA      Beta       CL         CDo       CDi      CDtot      CS        L/D        E        CFx       CFy       CFz       CMx       CMy       CMz       T/QS'
# 実験結果を探すの使う


for i in range(0,TOTAL_CASE):
    TARGET = LISTS_CHUNK[i]
    ROLL_INDEX = 0
    PITCH_INDEX = 0
    YAW_INDEX = 0
    # Roll Pitch Yaw 情報を格納している列を探す
    for j in range(0,len(TARGET)):
        if("Roll__Rate" in TARGET[j]):
            ROLL_INDEX = j
        if("Pitch_Rate" in TARGET[j]):
            PITCH_INDEX = j
        if("Yaw___Rate" in TARGET[j]):
            YAW_INDEX = j
            break 
        
    RPY = [TARGET[ROLL_INDEX].split()[1],TARGET[PITCH_INDEX].split()[1], TARGET[YAW_INDEX].split()[1],]
    SUB_INDEX = TARGET.index(TARGET_REF) #渡した文字列と一致する要素のインデックスを探す
    SUB_INDEX_END = []
    # 最終イタレーションの場所を探す
    for j in range(SUB_INDEX,len(TARGET)):
        if(len(TARGET[j])==0):
            SUB_INDEX_END = j-1
            break
    
    DATA_ADD = TARGET[SUB_INDEX_END].split()[1:]
    DATA_ADD[3:3] = RPY
    LISTS_RESULTS.append(DATA_ADD) # 各種空力データのみ抜き出し
    
    
# 必要データは抜き出し終わった 抜き出したデータの並びは以下参照
# Mach AoA Beta Roll__Rate Pitch__Rate Yaw__Rate CL CDo CDi CDtot CS L/D E CFx  CFy CFz CMx CMy CMz T/QS'    
# 抜き出したデータを.matで保存する

# List to array
ARRAY_RESULTS = np.array(LISTS_RESULTS)
FLOAT_ARRAY_RESULTS_h = ARRAY_RESULTS.astype(float)
scipy.io.savemat("VSPAERO_AERO.mat", {'AERO':FLOAT_ARRAY_RESULTS_h})

##########################################################################
####################.history の処理終わり###################################
##########################################################################


##########################################################################
####################.stab の処理開始###################################
##########################################################################

FILENAME_s = FILENAME+".stab"

f_s=open(FILENAME_s) # ファイルを開く
Lists_s=f_s.readlines() # ファイル全てを行ごとに区切って読み込む
Lists_s=[line.strip() for line in Lists_s] #改行文字を消す

count = 0
REF_NUM = [] # SPLIT_REF がある場所のリスト

for i in Lists_s:
    if(i==SPLIT_REF):
        REF_NUM.append(count)
    count = count + 1    

TOTAL_CASE = len(REF_NUM) # 実行ケース総数
END_POINT  = len(Lists_s)-1
REF_NUM.append(END_POINT) # リストの最終行の番号
LISTS_CHUNK = [Lists_s[REF_NUM[i]:REF_NUM[i+1]-1] for i in range(0,TOTAL_CASE)]
LISTS_RESULTS = [] # 安定微係数の集合
LISTS_STAB_POINTS = [] # 巡航点の集合

# 情報が入っている行を探す
for i in range(0,TOTAL_CASE):
    TARGET = LISTS_CHUNK[i]
    MACH_INDEX = 0
    AOA_INDEX = 0
    BETA_INDEX = 0
    ROLL_INDEX = 0
    PITCH_INDEX = 0
    YAW_INDEX = 0
    # 重複を回避するためのフラグ
    R_F = 0
    P_F = 0
    Y_F = 0
    COEFF_START = 0 # 微係数集合が始まる行
    COEFF_END   = 0 # 微係数集合が終わる行
    # Roll Pitch Yaw 情報を格納している列を探す
    for j in range(0,len(TARGET)):
        if("Mach_" in TARGET[j]):
            MACH_INDEX = j
        if("AoA_" in TARGET[j]):
            AOA_INDEX = j
        if("Beta_" in TARGET[j]):
            BETA_INDEX = j
        if("Roll__Rate" in TARGET[j]):
            if(R_F==0):
               ROLL_INDEX = j
               R_F = 1
        if("Pitch_Rate" in TARGET[j]):
            if(P_F == 0):
               PITCH_INDEX = j
               P_F = 1
        if("Yaw___Rate" in TARGET[j]):
            if(Y_F == 0):
               YAW_INDEX = j
               Y_F = 1
        if("CFx" in TARGET[j]):
            COEFF_START = j
        if("CMn" in TARGET[j]):
            COEFF_END = j
    
    LISTS_STAB_POINTS.append([TARGET[MACH_INDEX].split()[1], TARGET[AOA_INDEX].split()[1], TARGET[BETA_INDEX].split()[1], 
                              TARGET[ROLL_INDEX].split()[1], TARGET[PITCH_INDEX].split()[1], TARGET[YAW_INDEX].split()[1]])
    
    for j in range(COEFF_START,COEFF_END+1):
        LISTS_RESULTS.append(TARGET[j].split()[1:])
        

## 巡航点情報の整理
ARRAY_STAB = np.array(LISTS_STAB_POINTS)
FLOAT_ARRAY_STAB = ARRAY_STAB.astype(float)

## 安定微係数の整理
ARRAY_COEFF = np.array(LISTS_RESULTS)
FLOAT_ARRAY_COEFF = ARRAY_COEFF.astype(float)

##########################################################################
####################.stab の処理終了###################################
##########################################################################

scipy.io.savemat("VSPAERO_AERO.mat", {'AERO':FLOAT_ARRAY_RESULTS_h,'STAB_Point':FLOAT_ARRAY_STAB,'COEFF':FLOAT_ARRAY_COEFF})


