#%%
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
import pandas as pd
import scipy.spatial.distance as distance
import itertools
# %%
som = pd.read_csv('csvs/image_som_result20230110_073816.csv', index_col=0)
list_som = []
for i in som.index:
    list_som.append(i)

title_som = pd.read_csv('csvs/title_som_result20230110_092259.csv', index_col=0)
list_title = []
for i in title_som.index:
    list_title.append(i)

represent_image = pd.read_csv('csvs/rep_image_som_result20230110_094856_3-3.csv', index_col=0)
rep_image = []
for i in represent_image.index:
    rep_image.append(i)

image_title = pd.read_csv('csvs/imageName_title_rename_dict.csv', index_col=0).to_dict()
links = pd.read_csv('csvs/imageName_link_rename_dict.csv', index_col=0).to_dict()
title_image = pd.read_csv('csvs/title_imageName_rename_dict.csv', index_col=0).to_dict()
title_features = pd.read_csv('csvs/titleVectorsNoANDNumber.csv', index_col=0)
image_title_num = pd.read_csv('csvs/imageName_title_dict.csv', index_col=0).to_dict()

# %%
def sort_by_similarity(sorted_dict):
    temporary_sorted_dict = sorted(sorted_dict.items(), reverse=True, key=lambda x:x[1])
    sorted_dict.clear()
    # 辞書をソート後に更新
    sorted_dict.update(temporary_sorted_dict)
    return sorted_dict
# %%
def sortForSimilarity(image):
    # 画像ファイル名→タイトル(管理番号あり)に変換用
    title_dict = image_title_num['col2']
    # タイトルを探す
    title = title_dict[image]
    # ソート後の辞書
    sorted_dict = {}
    # タイトル(管理番号あり)→画像ファイル名に変換用
    dict_title_image = title_image['col2']
    ''' 類似度を計算し、辞書を作成 '''
    for i in title_features.index:
        # コサイン類似度を計算
        sim = 1 - distance.cosine(title_features.loc[title].to_list(), title_features.loc[i].to_list())
        # 画像ファイル名を探す
        image_name = dict_title_image[i]
        ''' 類似度が0.3以上のみにする '''
        if sim >= 0.3:
            # 辞書に追加
            sorted_dict[image_name] = sim
    # 辞書を類似度順にソートし、一時的に別の辞書に保管
    #temporary_sorted_dict = sorted(sorted_dict.items(), reverse=True, key=lambda x:x[1])
    #temporary_sorted_dict = sort_by_similarity(sorted_dict)
    # 辞書の要素をすべて削除(そのままだと無駄な括弧が入るため)
    #sorted_dict.clear()
    # 辞書をソート後に更新
    #sorted_dict.update(temporary_sorted_dict)
    sorted_dict = sort_by_similarity(sorted_dict)
    sorted_list = []
    for key in sorted_dict.keys():
        sorted_list.append(key)
    return sorted_list
# %%
def spiral_list(sorted_list):


    LOOP = 5
    WIDTH = (2*LOOP) + 1

    E = (1, 0)
    N = (0, -1)
    W = (-1, 0)
    S = (0, 1)
    DIRECTION = itertools.cycle((E, S, W, N))

    x = LOOP
    y = LOOP
    step = 1    # 進んだ距離
    corner = 1  # まがり角の位置

    # 二次元リストを初期化
    spiral = []
    for i in range(WIDTH):
        spiral.append([0 for j in range(WIDTH)])

    for i in range(WIDTH * WIDTH):
        # まがり角に到達したら方向転換
        if step >= corner:
            step = 1
            direction = next(DIRECTION)
            dx, dy = direction

            # X方向に進むとき、まがり角が遠くなる
            if direction == E or direction == W:
                corner += 1

        spiral[y][x] = i
        step += 1
        x += dx
        y += dy

    toList = []
    toList = sum(spiral, [])
    image_list = ['-1'] * len(toList)
    # 螺旋を表示する
    for i in range(len(sorted_list)):
        for j in range(len(toList)):
            print(j, toList[j])
            if i == toList[j]:
                image_list[j] = sorted_list[i]

    return(image_list)
#%%
print(spiral_list(sortForSimilarity('po00110100.jpg')))
# %%
