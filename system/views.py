#%%
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
import pandas as pd
import numpy as np
import itertools

# 類似度の基準値
similarity_standard_value = 0.0

#%%
# 画像によるsom結果(扱いやすくするためリストに変換)
som = pd.read_csv('system/csvs/image_som_result20230110_073816.csv', index_col=0)
list_som = []
for i in som.index:
    list_som.append(i)

# 代表資料(扱いやすくするためリストに変換)
represent_image = pd.read_csv('system/csvs/rep_image_som_result_40-60_20230224_112013.csv', index_col=0)
rep_image = []
for i in represent_image.index:
    rep_image.append(i)

# 画像ファイル名→タイトル変換用辞書
image_title = pd.read_csv('system/csvs/imageName_title_rename_dict.csv', index_col=0).to_dict()

# 画像ファイル名→タイトル(管理番号あり)変換用辞書
image_title_num = pd.read_csv('system/csvs/imageName_title_dict.csv', index_col=0).to_dict()

# 画像ファイル名→デジタル資料館の説明画面リンク変換用辞書
links = pd.read_csv('system/csvs/imageName_link_rename_dict.csv', index_col=0).to_dict()

# タイトル(管理番号あり)→画像ファイル名変換用辞書
title_image = pd.read_csv('system/csvs/title_imageName_rename_dict.csv', index_col=0).to_dict()

# 画像のベクトル表現
image_features = pd.read_csv('system/csvs/rename_featuresTitle_pca_350_MinMax.csv', index_col=0)

# タイトルのベクトル表現
title_features = pd.read_csv('system/csvs/titleVectorsNoANDNumber.csv', index_col=0)


#%%
@xframe_options_exempt

# 代表資料提示画面用
def electionView(request):
    ctx = {}
    ctx["rep_image"] = rep_image
    ctx["image_title"] = image_title['col2']
    ctx["links"] = links['col2']
    return render(request, 'system/elections.html', ctx)

# som&説明画面の親ページ
def imgSOMView(request):
    ctx = {}
    ctx["links"] = links['col2']

    ''' urlから表示したい画像のidタグを取得 '''
    if "imageID" in request.GET:
        id_list = request.GET["imageID"]
        id_split = id_list.split(' ')
        id = id_split[0]
        ctx["imageID"] = id

    if "frame" in request.GET:
        frame_list = request.GET["frame"]
        frame_split = frame_list.split(' ')
        frame = frame_split[0]
        ctx["frame"] = frame
    return render(request, 'system/img-som.html', ctx)

# som画面用
def SOM(request):
    ctx = {}
    ctx["image_title"] = image_title['col2']
    ctx["links"] = links['col2']
    if "imageID" in request.GET:
        id_list = request.GET["imageID"]
        id_split = id_list.split(' ')
        id = id_split[0]
        ctx["spiral_dict"] = spiral_image_dict(id)
        ctx["sorted_dict"] = part_image(id)

    return render(request, 'system/som.html', ctx)

# somとタイトル切り替え画面用
def menu(request):
    ctx = {}
    if "imageID" in request.GET:
        id_list = request.GET["imageID"]
        id_split = id_list.split(' ')
        id = id_split[0]
        ctx["imageID"] = id
    return render(request, 'system/menu.html', ctx)

# タイトル画面用
def titleSOMView(request):
    threshold_value = 0.5
    ctx = {}
    ctx["image_title"] = image_title['col2']
    ctx["links"] = links['col2']


    ''' urlから表示したい画像のidタグを取得 '''
    if "imageID" in request.GET:
        id_list = request.GET["imageID"]
        id_split = id_list.split(' ')
        id = id_split[0]
        ctx["spiral_dict"] = spiral_title_dict(id)
        ctx["sorted_dict"] = part_title(id)

    return render(request, 'system/title-som.html', ctx)

#%%
def sort_by_similarity(dict):
    temporary_sorted_dict = sorted(dict.items(), reverse=True, key=lambda x:x[1])
    sorted_dict = {}
    # 辞書をソート後に更新
    sorted_dict.update(temporary_sorted_dict)
    return sorted_dict

''' タイトルの類似度を計算し、ソートして返す '''
def sortForSimilarity(id):
    # 画像ファイル名→タイトル(管理番号あり)に変換用
    title_dict = image_title_num['col2']
    # タイトルを探す
    title = title_dict[id]
    # ソート後の辞書
    sorted_dict = {}
    sorted_dict[id] = 1.0
    # タイトル(管理番号あり)→画像ファイル名に変換用
    dict_title_image = title_image['col2']
    ''' 類似度を計算し、辞書を作成 '''
    for i in title_features.index:
        if i != title:
            # コサイン類似度を計算
            sim = cos_similarity(title_features.loc[title].to_list(), title_features.loc[i].to_list())
            # 画像ファイル名を探す
            image_name = dict_title_image[i]
            ''' 類似度が基準値以上のみにする '''
            if sim >= similarity_standard_value:
                # 辞書に追加
                sorted_dict[image_name] = sim
    sorted_dict = sort_by_similarity(sorted_dict)
    '''
    for key in sorted_dict.keys():
        sorted_list.append(key)
    '''
    return sorted_dict

#%%
def spiral_title_dict(id):

    sorted_dict = sortForSimilarity(id)

    sorted_key_list = []
    sorted_value_list = []
    for key, value in sorted_dict.items():
        sorted_key_list.append(key)
        sorted_value_list.append(value)


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
    sim_list = ['-1'] * len(toList)
    # 螺旋リストに代入
    for i in range(len(sorted_key_list)):
        for j in range(len(toList)):
            if i == toList[j]:
                image_list[j] = sorted_key_list[i]
                sim_list[j] = sorted_value_list[i]

    spiral_dict = dict(zip(image_list, sim_list))
    return spiral_dict


def part_title(id):
    sorted_dict = sortForSimilarity(id)
    count = 0
    part_dict = {}
    for key, value in sorted_dict.items():
        part_dict[key] = value
        count += 1
        if count == 50:
            return part_dict



''' タイトルの類似度を計算し、ソートして返す '''
def sort_image_Similarity(id):
    # ソート後の辞書
    sorted_dict = {}
    sorted_dict[id] = 1.0
    ''' 類似度を計算し、辞書を作成 '''
    for i in image_features.index:
        if i != id:
            # コサイン類似度を計算
            sim = cos_similarity(image_features.loc[id].to_list(), image_features.loc[i].to_list())
            ''' 類似度が基準値以上のみにする '''
            if sim >= similarity_standard_value:
                # 辞書に追加
                sorted_dict[i] = sim
    sorted_dict = sort_by_similarity(sorted_dict)
    '''
    for key in sorted_dict.keys():
        sorted_list.append(key)
    '''
    return sorted_dict

def spiral_image_dict(id):

    sorted_dict = sort_image_Similarity(id)

    sorted_key_list = []
    sorted_value_list = []
    for key, value in sorted_dict.items():
        sorted_key_list.append(key)
        sorted_value_list.append(value)


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
    sim_list = ['-1'] * len(toList)
    # 螺旋リストに代入
    for i in range(len(sorted_key_list)):
        for j in range(len(toList)):
            if i == toList[j]:
                image_list[j] = sorted_key_list[i]
                sim_list[j] = sorted_value_list[i]

    spiral_dict = dict(zip(image_list, sim_list))
    return spiral_dict

#%%
def part_image(id):
    sorted_dict = sort_image_Similarity(id)
    count = 0
    part_dict = {}
    for key, value in sorted_dict.items():
        part_dict[key] = value
        count += 1
        if count == 50:
            return part_dict

def cos_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))