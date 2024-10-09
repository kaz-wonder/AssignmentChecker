#coding: utf-8
import json
from datetime import datetime, timedelta

weekdays = {
    "月": 0,
    "火": 1,
    "水": 2,
    "木": 3,
    "金": 4,
    "土": 5,
    "日": 6
}

def Load():
    with open("main.json", "r", encoding='utf-8') as f:
        jikanwari = json.load(f)
    return jikanwari
        
jikanwari = Load()

def Save(x):
    global jikanwari
    with open("main.json", "w", encoding='utf-8') as f:
        json.dump(x, f, ensure_ascii=False, indent=4)
    jikanwari = x
    return jikanwari

def Saves(kamoku, youbi, kigen, wasure):
    global jikanwari
    jikanwari[kamoku] = {
        "曜日": youbi,
        "期限": kigen,
        "提出": 0,
        "提出忘れ": wasure
    }
                    
    with open("main.json", "w", encoding='utf-8') as f:
        json.dump(jikanwari, f, ensure_ascii=False, indent=4)
        
    jikanwari = Load() 

    return jikanwari



def Sort_Jikanwari(target):
    today = datetime.now()

    def Get_Deadline(kamoku_info):
        kadaihaihubi = today - timedelta(days=(today.weekday() - weekdays[kamoku_info["曜日"]]) % 7)
        shimekiri = kadaihaihubi + timedelta(days=kamoku_info["期限"])
        return shimekiri

    miteisyutu_List = []
    mihaihu_List = []
    teishutsu_List = []

    for kamoku, info in target.items():
        if info["提出"] == 0:
            miteisyutu_List.append((kamoku, info))
        elif info["提出"] == 2:
            mihaihu_List.append((kamoku, info))
        else:
            teishutsu_List.append((kamoku, info))

    miteisyutu_List.sort(key=lambda x: Get_Deadline(x[1]))     
    mihaihu_List.sort(key=lambda x: Next_Kadai_Haihu_Day(weekdays[x[1]["曜日"]]))
    teishutsu_List.sort(key=lambda x: weekdays[x[1]["曜日"]])
    
    sorted_jikanwari = {kamoku: info for kamoku, info in miteisyutu_List + mihaihu_List + teishutsu_List}

    with open("main.json", "w", encoding='utf-8') as f:
        json.dump(sorted_jikanwari, f, ensure_ascii=False, indent=4)

    return sorted_jikanwari


def Kadai_Haihu_Day(target_weekday):
    """課題配布日の計算（過去の指定曜日）"""
    today = datetime.now()
    days_ago = (today.weekday() - target_weekday) % 7
    last_weekday = today - timedelta(days=days_ago)
    return last_weekday.strftime('%Y-%m-%d')


def Next_Kadai_Haihu_Day(target_weekday):
    """次回の課題配布日の計算"""
    today = datetime.now()
    days_until = (target_weekday - today.weekday() + 7) % 7
    next_weekday = today + timedelta(days=days_until)
    return next_weekday.strftime('%Y-%m-%d')


def Deadline_Day(kadaihaihubi, kigen):
    """締め切り日の計算"""
    kadaihaihubi = datetime.strptime(kadaihaihubi, '%Y-%m-%d')
    simekiribi = kadaihaihubi + timedelta(days=int(kigen))
    return simekiribi.strftime('%Y-%m-%d')

def Update_Raise(target):
    """課題配布状況の更新"""
    global jikanwari
    
    for i in target:
        
        kadaihaihubi = Kadai_Haihu_Day(weekdays[target[i]["曜日"]])
        simekiribi = Deadline_Day(kadaihaihubi, target[i]["期限"])
        today = datetime.now().date()
        print(i, simekiribi)
        
        if datetime.strptime(simekiribi, '%Y-%m-%d').date() < today:
            """締め切りを過ぎている場合"""
            kadaihaihubi = Next_Kadai_Haihu_Day(weekdays[jikanwari[i]["曜日"]])
            simekiribi = Deadline_Day(kadaihaihubi, jikanwari[i]["期限"])
            
            if target[i]["提出"] == 0:  #未提出の場合
                target[i]["提出忘れ"] += 1  
            
            
            else:
                """次の課題配布日を迎えてない場合"""
                target[i]["提出"] = 2  #未配布にする
        
        else:
            if datetime.strptime(kadaihaihubi, '%Y-%m-%d').date() <= datetime.now().date():
                """課題配布日を迎えている場合"""
                if target[i]["提出"] == 2:  #未配布の場合未提出にする
                    target[i]["提出"] = 0
                    
                
    jikanwari = target
    Save(jikanwari)
    return jikanwari
    
                

Update_Raise(jikanwari)
Sort_Jikanwari(jikanwari)