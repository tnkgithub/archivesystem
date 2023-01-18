from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
import pandas as pd
import scipy.spatial.distance as distance
import itertools

# 類似度の基準値
similarity_standard_value = 0.45

# 画像によるsom結果(扱いやすくするためリストに変換)
som = pd.read_csv('system/csvs/image_som_result20230110_073816.csv', index_col=0)
list_som = []
for i in som.index:
    list_som.append(i)

# 代表資料(扱いやすくするためリストに変換)
represent_image = pd.read_csv('system/csvs/rep_image_som_result20230110_094856_3-3.csv', index_col=0)
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

# タイトルのベクトル表現
title_features = pd.read_csv('system/csvs/titleVectorsNoANDNumber.csv', index_col=0)

#%%
''' テスト用
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
'''
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
    ctx["image_som"] = list_som
    if "imageID" in request.GET:
        id_list = request.GET["imageID"]
        id_split = id_list.split(' ')
        id = id_split[0]
        ctx["imageID"] = id

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
    ctx = {}
    ctx["image_title"] = image_title['col2']
    ctx["links"] = links['col2']

    ''' urlから表示したい画像のidタグを取得 '''
    if "imageID" in request.GET:
        id_list = request.GET["imageID"]
        id_split = id_list.split(' ')
        id = id_split[0]
        ctx["title_list"] = spiral_list(id)
    return render(request, 'system/title-som.html', ctx)

#%%
def sort_by_similarity(dict):
    temporary_sorted_dict = sorted(dict.items(), reverse=True, key=lambda x:x[1])
    sorted_dict = {}
    # 辞書をソート後に更新
    sorted_dict.update(temporary_sorted_dict)
    return sorted_dict

''' タイトルの類似度を計算し、ソートして返す '''
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
        if i != title:
            # コサイン類似度を計算
            sim = 1 - distance.cosine(title_features.loc[title].to_list(), title_features.loc[i].to_list())
            # 画像ファイル名を探す
            image_name = dict_title_image[i]
            ''' 類似度が基準値以上のみにする '''
            if sim >= similarity_standard_value:
                # 辞書に追加
                sorted_dict[image_name] = sim

    sorted_dict = sort_by_similarity(sorted_dict)
    sorted_list = [image]
    for key in sorted_dict.keys():
        sorted_list.append(key)
    return sorted_list

#%%
def spiral_list(image):

    sorted_list = sortForSimilarity(image)

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
            if i == toList[j]:
                image_list[j] = sorted_list[i]
                print(i, image_list[j])

    return(image_list)
