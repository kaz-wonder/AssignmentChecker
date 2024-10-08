#coding: utf-8
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sys, os, platform, file
from datetime import datetime, timedelta
from functools import partial

root = tk.Tk()
root.title("課題管理")
root.geometry("920x600")
root.config(bg="gray14")

jikanwari = file.Load()
file.Sort_Jikanwari(jikanwari)

label_Count = 0
weekdays = {
    "月": 0, 
    "火": 1, 
    "水": 2, 
    "木": 3, 
    "金": 4, 
    "土": 5, 
    "日": 6  
}

checkbox_Vars = []

def Reboot():
    """再起動用関数"""
    os.execv(sys.executable, ['python'] + sys.argv)

def On_Key_Event(event):
    """F5で再起動"""
    if event.keysym == 'F5':
        Reboot()

def Open_Confirmation_Window(kamoku):
    """詳細ウィンドウの表示"""
    confirmation_Window = tk.Toplevel(root)
    confirmation_Window.title(kamoku)
    confirmation_Window.geometry("300x318")
    
    teisyutujoukyou = "未提出" if jikanwari[kamoku]["提出"] == 0 else "提出済"
    
    comment = """
    {}\n\n
    配布曜日 : {}\n\n
    提出状況 : {}\n\n
    期限 : 配布日から{}日後まで\n\n
    欠席回数 : {}
    """
    comment = comment.format(kamoku, jikanwari[kamoku]["曜日"], teisyutujoukyou, jikanwari[kamoku]["期限"], jikanwari[kamoku]["提出忘れ"])

    subject_Label = tk.Label(confirmation_Window, text=comment, font=("Arial", 13, "bold"), foreground="gray92", background="gray28")
    subject_Label.grid(row=0, column=0, columnspan=3, sticky="ew")
    
    def Close_Window():
        confirmation_Window.destroy()  # ウィンドウを閉じる

    update_Button = tk.Button(confirmation_Window, text="閉じる", fg="gray92", bg="gray28", command=Close_Window)
    update_Button.grid(row=1, column=0, columnspan=3, sticky="ew")
    
    confirmation_Window.grid_columnconfigure(0, weight=1)
    confirmation_Window.grid_columnconfigure(1, weight=1)
    confirmation_Window.grid_columnconfigure(2, weight=1)

def Raice(kamoku):
    """提出処理"""
    # チェックされた項目の処理
    checked_Items = Check_All_Checkbox_Values()
    for idx in checked_Items:
        subject_Name = list(jikanwari.keys())[idx]
        Process_Subject_Submission(subject_Name)

    # 現在の課題の提出状況を処理
    Process_Subject_Submission(kamoku)

def Process_Subject_Submission(kamoku):
    """指定した科目を提出に書き換える"""
    kadaihaihubi = file.Kadai_Haihu_Day(weekdays[jikanwari[kamoku]["曜日"]])
    simekiribi = file.Deadline_Day(kadaihaihubi, jikanwari[kamoku]["期限"])

    if datetime.strptime(simekiribi, '%Y-%m-%d').date() < datetime.now().date():
        kadaihaihubi = file.Next_Kadai_Haihu_Day(weekdays[jikanwari[kamoku]["曜日"]])

    if datetime.strptime(kadaihaihubi, '%Y-%m-%d').date() <= datetime.now().date():
        jikanwari[kamoku]["提出"] = 1
        file.Save(jikanwari)
        file.Sort_Jikanwari(jikanwari)

        Update_Submission_Button(kamoku)
        Update_Main_Window()

def Update_Submission_Button(kamoku):
    """ボタンの更新を行う"""
    for widget in main_Frame.grid_slaves():
        if isinstance(widget, tk.Button) and widget.cget("text") == "取消":
            widget.destroy()

    cancel_button = tk.Button(main_Frame, text="取消", font=("Arial", 10, "bold"), command=partial(Cancel, kamoku), width=7)
    cancel_button.grid(row=label_Count + 1, column=7, padx=10)

def Cancel(kamoku):
    """提出の取り消しを行う"""
    global jikanwari
    check = Check_All_Checkbox_Values()
    jikanwari[kamoku]["提出"] = 0 
    jikanwari = file.Save(jikanwari)
    raise_Button = tk.Button(main_Frame, text="取消", font=("Arial", 10, "bold"), command=partial(Raice, kamoku), width=7)
    raise_Button.grid(row=label_Count + 1, column=7, padx=10) 

    if check:
        for i in check[:]:
            keys_list = list(jikanwari.keys())
            target = keys_list[i]
            if jikanwari[target]["提出"] == 1:
                jikanwari[target]["提出"] = 0 
            else:
                continue
            jikanwari = file.Save(jikanwari)
            
            raise_Button = tk.Button(main_Frame, text="取消", font=("Arial", 10, "bold"), command=partial(Raice, kamoku), width=7)
            raise_Button.grid(row=label_Count + 1, column=7, padx=10) 
            
    Update_Main_Window() 
    
        
def Add_Subject():
    """科目の追加を行うウィンドウの表示"""
    add_Subject_Window = tk.Toplevel(root)
    add_Subject_Window.title("科目の追加")
    add_Subject_Window.geometry("600x300")
    add_Subject_Window.config(bg="gray20")
    
    add_Subject_Frame = tk.Frame(add_Subject_Window, bg="gray28")
    add_Subject_Frame.grid(row=0, column=0, columnspan=7, padx=50, pady=25)
    add_Subject_Label = tk.Label(add_Subject_Frame, text="科目名 :",  font=("Arial", 14), fg="gray96", bg="gray28")
    add_Subject_Label.grid(row=0, column=0, padx=5)
    add_Subject_Entry = tk.Entry(add_Subject_Frame, font=("Arial", 13), fg="gray92", bg="gray28", width=40)
    add_Subject_Entry.grid(row=0, column=1, padx=15)
    
    add_Weekday_Frame = tk.Frame(add_Subject_Window, bg="gray28")
    add_Weekday_Frame.grid(row=1, column=0, columnspan=7, padx=50, pady=10)
    add_Weekday_Label = tk.Label(add_Weekday_Frame, text=" 曜日 :",  font=("Arial", 14), fg="gray96", bg="gray28")
    add_Weekday_Label.grid(row=1, column=0, padx=5)
    
    values = ["月","火","水","木","金","土","日"]
    add_Weekday_ComboBox = ttk.Combobox(add_Weekday_Frame, values=values, width=4, font=(13), background="gray28")
    add_Weekday_ComboBox.grid(row=1, column=1, padx=20)
    
    add_Deadline_Label= tk.Label(add_Weekday_Frame, text="         期限 :",  font=("Arial", 14), fg="gray96", bg="gray28")
    add_Deadline_Label.grid(row=1, column=2, padx=10)
    add_Deadline_Entry = tk.Entry(add_Weekday_Frame, font=("Arial", 13), fg="gray92", bg="gray28", width=4)
    add_Deadline_Entry.grid(row=1, column=3, padx=3)
    add_Deadline_Label2 = tk.Label(add_Weekday_Frame, text="日後まで ",  font=("Arial", 14), fg="gray96", bg="gray28")
    add_Deadline_Label2.grid(row=1, column=4, padx=10)
    
    add_Forgetcount_Frame = tk.Frame(add_Subject_Window, bg="gray28")
    add_Forgetcount_Frame.grid(row=2, column=0, columnspan=7, padx=50, pady=20)
    add_Forgetcount_Label = tk.Label(add_Forgetcount_Frame, text="提出忘れ :",  font=("Arial", 14), fg="gray96", bg="gray28")
    add_Forgetcount_Label.grid(row=0, column=0, padx=10)
    add_Forgetcount_Entry = tk.Entry(add_Forgetcount_Frame, font=("Arial", 13), fg="gray92", bg="gray28", width=4)
    add_Forgetcount_Entry.grid(row=0, column=1, padx=3)
    add_Forgetcount_Label2 = tk.Label(add_Forgetcount_Frame, text="回",  font=("Arial", 14), fg="gray96", bg="gray28")
    add_Forgetcount_Label2.grid(row=0, column=2, padx=10)
    
    def Close_Window():
        add_Subject_Window.destroy()
    
    def Registration():
        """科目の登録を行う"""
        global jikanwari
        kamoku = add_Subject_Entry.get()
        youbi = add_Weekday_ComboBox.get()
        kigen = add_Deadline_Entry.get()
        wasure = add_Forgetcount_Entry.get()
        
        if kamoku == "" or youbi == "" or kigen == "" or wasure == "":
            messagebox.showerror("エラー", "未入力の項目があります。")
            return
        
        if youbi not in weekdays.keys():
            messagebox.showerror("エラー", "曜日は日から月の間で入力してください")
            return
        
        result = messagebox.askquestion(
            "確認", 
            "科目：{}\n曜日：{}\n期限：配布から{}日後\n提出忘れ：{}回\n上記の内容でよろしいですか？".format(kamoku, youbi, kigen, wasure)
        )
        
        if result == "yes":
            try:
                if kamoku in jikanwari.keys(): 
                    result = messagebox.askquestion("警告", "既に、科目【{}】は存在します。上書きしますか？".format(kamoku))
                    if result != "yes":
                        return

                jikanwari = file.Saves(kamoku, youbi, int(kigen), int(wasure))
                jikanwari = file.Update_Raise(jikanwari)
                jikanwari = file.Sort_Jikanwari(jikanwari)
                
                Update_Main_Window()
                Close_Window()

            except Exception as e:
                messagebox.showerror("エラー", f"登録に失敗しました。\n内容を確認後もう一度お試しください。\nエラー: {str(e)}")

                        
    add_Button_Frame = tk.Frame(add_Subject_Window, bg="gray28")
    add_Button_Frame.grid(row=3, column=0, columnspan=7, padx=50, pady=20)
    quit_Button = tk.Button(add_Button_Frame, text="閉じる", font=(7), fg="gray92", bg="gray28", width=4, command=Close_Window)
    quit_Button.grid(row=3, column=1, padx=20)
    add_Registration = tk.Button(add_Button_Frame, text="登録", font=(7), fg="gray92", bg="gray28", width=4, command=Registration)
    add_Registration.grid(row=3, column=2, padx=20)
    
    add_Subject_Window.mainloop()
    
    
def Delete_Subject():
    """科目の削除を行う"""
    global jikanwari
    checked_Items = Check_All_Checkbox_Values()
    result = messagebox.askquestion("確認", "選択した{}科目を削除します。\nよろしいですか？".format(len(checked_Items)))
    if result == "yes":
        delete_List = []
        for idx in checked_Items:
            delete_List.append(list(jikanwari.keys())[idx])

        for target in delete_List:
            del jikanwari[target]
        
        file.Save(jikanwari)
        jikanwari = file.Load()    
        
        Update_Main_Window()

        
def Update_Main_Window():
    """ウィンドウの更新を行う"""
    global label_Count
    global main_Frame 
    label_Count = 0
    checkbox_Vars.clear() 
    
    widgets = main_Frame.winfo_children()[1:]
    
    for name in widgets:
        name.destroy()

    if not jikanwari:
        row_Frame = tk.Frame(main_Frame, bg="gray28", borderwidth=2, relief="raised", padx=20, pady=30)
        row_Frame.grid(row=label_Count + 1, column=0, sticky="ew", padx=5, pady=3, columnspan=7)
        
        Label = tk.Label(row_Frame, text="課題が登録されていません。\n登録ボタンから課題の登録を行ってください", font=("Arial", 13, "bold"), foreground="gray92", background="gray28")
        Label.grid(row=0, column=0, padx=10)
        return

    max_subject_width = max(len(kamoku) for kamoku in jikanwari) + 4 
    
    for kamoku in jikanwari:
        kadaihaihubi = file.Kadai_Haihu_Day(weekdays[jikanwari[kamoku]["曜日"]])
        simekiribi = file.Deadline_Day(kadaihaihubi, jikanwari[kamoku]["期限"])

        if datetime.strptime(simekiribi, '%Y-%m-%d').date() < datetime.now().date():
            kadaihaihubi = file.Next_Kadai_Haihu_Day(weekdays[jikanwari[kamoku]["曜日"]])
            simekiribi = file.Deadline_Day(kadaihaihubi, jikanwari[kamoku]["期限"])
            frame_Color = "gray28"
            
        elif datetime.strptime(simekiribi, '%Y-%m-%d').date() - datetime.now().date() <= timedelta(days=1):
            if jikanwari[kamoku]["提出"] == 0:
                frame_Color = "lightcoral"
            else:
                frame_Color = "gray28"
        else:
            frame_Color = "gray28"
        
        if jikanwari[kamoku]["提出"] == 1:
            teisyutu_Joukyou = "提出済"
            color = "green"
            button_Text = "取消"
            button_Color = "lightcoral"
            button_Command = partial(Cancel, kamoku)
            
        elif jikanwari[kamoku]["提出"] == 2:
            teisyutu_Joukyou = "未配布"
            color = "navajowhite"
            button_Text = "提出"
            button_Color = "gray"
            button_Command = partial(Raice, kamoku)
            
        else:
            teisyutu_Joukyou = "未提出"
            color = "orange"
            button_Text = "提出"
            button_Color = "gray92"
            button_Command = partial(Raice, kamoku)
            
        row_Frame = tk.Frame(main_Frame, bg=frame_Color, borderwidth=2, relief="raised", padx=20, pady=30)
        row_Frame.grid(row=label_Count + 1, column=0, sticky="ew", padx=5, pady=3, columnspan=7)

        check_var = tk.IntVar(value=0)
        checkbox = tk.Checkbutton(row_Frame, variable=check_var, bg=frame_Color, state='normal', font=("Arial", 12))
        checkbox.grid(row=0, column=0)
        checkbox_Vars.append(check_var)
        
        weekday_Label = tk.Label(row_Frame, text=jikanwari[kamoku]["曜日"], font=("Arial", 13, "bold"), foreground="gray92", background=frame_Color)
        weekday_Label.grid(row=0, column=1, padx=20)

        subject_Label = tk.Label(row_Frame, text=kamoku, font=("Arial", 15, "bold"), foreground="gray92", background=frame_Color, width=max_subject_width)
        subject_Label.grid(row=0, column=2, padx=0)

        distribution_Label = tk.Label(row_Frame, text=kadaihaihubi, font=("Arial", 14), foreground="gray92", background=frame_Color)
        distribution_Label.grid(row=0, column=3, padx=5)

        deadline_Label = tk.Label(row_Frame, text=simekiribi, font=("Arial", 14), foreground="gray92", background=frame_Color)
        deadline_Label.grid(row=0, column=4, padx=5)

        edit_Button = tk.Button(row_Frame, text="詳細", command=partial(Open_Confirmation_Window, kamoku), bg=frame_Color)
        edit_Button.grid(row=0, column=5, padx=5)
        
        teisyutu_Label = tk.Label(row_Frame, text=teisyutu_Joukyou, font=("Arial", 17, "bold"), foreground=color, background=frame_Color)
        teisyutu_Label.grid(row=0, column=6, padx=25)
        
        raise_Button = tk.Button(row_Frame, text=button_Text, font=("Arial", 15, "bold"), command=button_Command, width=7, bg=button_Color)
        raise_Button.grid(row=0, column=7, padx=10)

        label_Count += 1
        

        
def Scroll_Canvas(event):
    """スクロールする"""
    if event.delta > 0: 
        canvas.yview_scroll(-1, "units")
    else: 
        canvas.yview_scroll(1, "units")

def On_Mousewheel(event):
    if event.num == 4:
        canvas.yview_scroll(-1, "units") 
    elif event.num == 5:
        canvas.yview_scroll(1, "units") 
    
def Check_All_Checkbox_Values():
    """チェックボックスの取得"""
    check_List = []
    for idx, var in enumerate(checkbox_Vars):
        if var.get() == 1:
            check_List.append(idx)
    return check_List

"""メインウィンドウの表示"""
canvas = tk.Canvas(root, bg="gray20")
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
main_Frame = tk.Frame(canvas, bg="gray20")
main_Frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

canvas.create_window((0, 0), window=main_Frame, anchor="nw")
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.configure(yscrollcommand=scrollbar.set)


if platform.system() == 'Darwin': 
    """MAC_OS"""
    canvas.bind("<Button-4>", On_Mousewheel)
    canvas.bind("<Button-5>", On_Mousewheel)

else: 
    canvas.bind_all("<MouseWheel>", Scroll_Canvas)

"""ヘッダーの表示"""
header_Frame = tk.Frame(main_Frame, bg="gray28")
header_Frame.grid(row=0, column=0, sticky="w", columnspan=7) 

label0 = tk.Label(header_Frame, text="選択", font=("Arial", 14), relief="solid", padx=3)
label0.grid(row=0, column=0, padx=7, pady=5)

label1 = tk.Label(header_Frame, text="曜日", font=("Arial", 14), relief="solid", padx=3)
label1.grid(row=0, column=1, padx=7, pady=5)

label2 = tk.Label(header_Frame, text="科目名", font=("Arial", 14), relief="solid", padx=68)
label2.grid(row=0, column=2, padx=12, pady=5)

label3 = tk.Label(header_Frame, text="課題配布日", font=("Arial", 14), relief="solid")
label3.grid(row=0, column=3, padx=7, pady=5)

label4 = tk.Label(header_Frame, text="締切", font=("Arial", 14), relief="solid", padx=50)
label4.grid(row=0, column=4, padx=7, pady=5)

label5 = tk.Label(header_Frame, text="提出状況", font=("Arial", 14), relief="solid", padx=12)
label5.grid(row=0, column=5, padx=7, pady=5)

edit_Frame = tk.Frame(header_Frame, bg="gray20")
edit_Frame.grid(row=0, column=6) 

add_Button = tk.Button(edit_Frame, text="科目の追加", font=("Arial", 11, "bold"), relief="solid", padx=15, command=Add_Subject)
add_Button.grid(row=0, column=0, padx=10, pady=5) 

delete_Button = tk.Button(edit_Frame, text="科目の削除", font=("Arial", 11, "bold"), relief="solid", padx=15, command=Delete_Subject)
delete_Button.grid(row=1, column=0, padx=10, pady=5) 

"""画面の更新"""
Update_Main_Window()

"""再起動処理"""
root.bind("<KeyPress>", On_Key_Event)

root.mainloop()
