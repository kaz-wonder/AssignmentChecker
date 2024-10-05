#coding: utf-8
import json
from datetime import datetime, timedelta

# 曜日の数値化
weekdays = {
    "月": 0,
    "火": 1,
    "水": 2,
    "木": 3,
    "金": 4,
    "土": 5,
    "日": 6
}

def load():
    with open("main.json", "r", encoding='utf-8') as f:
        jikanwari = json.load(f)
    return jikanwari
        
jikanwari = load()

def save(x):
    global jikanwari
    with open("main.json", "w", encoding='utf-8') as f:
        json.dump(x, f, ensure_ascii=False, indent=4)
    jikanwari = x
    return jikanwari

def saves(kamoku, youbi, kigen, wasure):
    global jikanwari
    # JSONファイルに変更を保存
    # jikanwariの更新
    jikanwari[kamoku] = {
        "曜日": youbi,
        "期限": kigen,
        "提出": 0,
        "提出忘れ": wasure
    }
                    
    with open("main.json", "w", encoding='utf-8') as f:
        json.dump(jikanwari, f, ensure_ascii=False, indent=4)
        
    jikanwari = load() 

    return jikanwari



def sort_jikanwari(target):
    today = datetime.now()

    def get_shimekiri_day(kamoku_info):
        kadaihaihubi = today - timedelta(days=(today.weekday() - weekdays[kamoku_info["曜日"]]) % 7)
        shimekiri = kadaihaihubi + timedelta(days=kamoku_info["期限"])
        return shimekiri

    mitsutei_list = []
    mihaihu_list = []
    teishutsu_list = []

    for kamoku, info in target.items():
        if info["提出"] == 0:
            mitsutei_list.append((kamoku, info))
        elif info["提出"] == 2:
            mihaihu_list.append((kamoku, info))
        else:
            teishutsu_list.append((kamoku, info))

    # 未提出の課題を締め切り日が近い順に並べ替え
    mitsutei_list.sort(key=lambda x: get_shimekiri_day(x[1])) 
    
    mihaihu_list.sort(key=lambda x: weekdays[x[1]["曜日"]])

    # 提出済みの課題を曜日順に並べ替え
    teishutsu_list.sort(key=lambda x: weekdays[x[1]["曜日"]])

    sorted_jikanwari = {kamoku: info for kamoku, info in mitsutei_list + mihaihu_list + teishutsu_list}

    with open("main.json", "w", encoding='utf-8') as f:
        json.dump(sorted_jikanwari, f, ensure_ascii=False, indent=4)

    return sorted_jikanwari

# 課題配布日の計算（過去の指定曜日）
def Kadai_Haihu_Day(target_weekday):
    today = datetime.now()
    days_ago = (today.weekday() - target_weekday) % 7
    last_weekday = today - timedelta(days=days_ago)
    return last_weekday.strftime('%Y-%m-%d')

# 次回の課題配布日の計算
def Next_Kadai_Haihu_Day(target_weekday):
    today = datetime.now()
    days_until = (target_weekday - today.weekday() + 7) % 7
    next_weekday = today + timedelta(days=days_until)
    return next_weekday.strftime('%Y-%m-%d')

# 締切日を計算
def shimekiri_Day(kadaihaihubi, kigen):
    kadaihaihubi = datetime.strptime(kadaihaihubi, '%Y-%m-%d')
    simekiribi = kadaihaihubi + timedelta(days=int(kigen))
    return simekiribi.strftime('%Y-%m-%d')

def update_Raise(target):
    global jikanwari
    # 提出済みで締め切りを過ぎているものは未提出にする
    # 未提出で期限を過ぎたものは欠席にする
    
    for i in target:
        kadaihaihubi = Kadai_Haihu_Day(weekdays[target[i]["曜日"]])
        simekiribi = shimekiri_Day(kadaihaihubi, target[i]["期限"])
        
        if datetime.strptime(simekiribi, '%Y-%m-%d').date() < datetime.now().date():
            kadaihaihubi = Next_Kadai_Haihu_Day(weekdays[jikanwari[i]["曜日"]])
            simekiribi = shimekiri_Day(kadaihaihubi, jikanwari[i]["期限"])
            target[i]["提出"] = 2  #未配布
            
        else:
            today = datetime.now().date()
            simekiribi = datetime.strptime(simekiribi, '%Y-%m-%d').date()
            if simekiribi < today:  # 締め切りを過ぎている場合
                if target[i]["提出"] == 0:  # 未提出の場合
                    target[i]["提出忘れ"] += 1  
                    #ここに通知の処理を書く
                
                else:
                    target[i]["提出"] = 0  # 提出済みの場合未提出にする
            else:
                if target[i]["提出"] == 2:
                    target[i]["提出"] = 0
                
    jikanwari = target
    return jikanwari
    
                

update_Raise(jikanwari)
sort_jikanwari(jikanwari)