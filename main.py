from flask import Flask, render_template
from json import load, dump
from glob import glob
from os import rename, path, remove
from filecmp import cmp
from shutil import move

app = Flask(__name__)

with open('static\setting.json', mode='r', encoding='utf8') as json_file:
    setting = load(json_file)

# 尋找重新命名之預備檔案
def __rename_ready_files__(from_folder = "files|*"):
    from_folder = from_folder.replace('|', "\\")
    try:
        files = glob(from_folder)
        text = ""
        for i in files:
            set_data = i.split('\\')
            text += f"{set_data[-2]}|{set_data[-1]}" if i == files[0] else f"|{set_data[-1]}"
        return text
    except:
        return ""
# 執行重新命名
def __rename_files_doing__(files_f, files_e, files_i, files_n, folder = "files|*"):
    folder = folder.replace('|', "\\")
    try:
        files = glob(folder)
        z = folder.split("*")
        n = int(files_n)
        files_i = int(files_i)
        if files_i == 1:
            for i in files:
                rename(i, f"{z[0]}{files_f}{n}.{files_e}")
                n += 1
        elif files_i == 2:
            for i in files:
                rename(i, f"{z[0]}{files_f}{n:02d}.{files_e}")
                n += 1
        elif files_i == 3:
            for i in files:
                rename(i, f"{z[0]}{files_f}{n:03d}.{files_e}")
                n += 1
        elif files_i == 4:
            for i in files:
                rename(i, f"{z[0]}{files_f}{n:04d}.{files_e}")
                n += 1
        elif files_i == 5:
            for i in files:
                rename(i, f"{z[0]}{files_f}{n:05d}.{files_e}")
                n += 1
        elif files_i == 6:
            for i in files:
                rename(i, f"{z[0]}{files_f}{n:06d}.{files_e}")
                n += 1
        return "批次檔案重新命名完成！"
    except:
        return "命名錯誤！"
# 尋找重複檔案
def __find_repeat_files__(folder = "files|*"):
    try:
        folder = folder.replace('|', "\\")
        files = glob(folder)
        if len(files) != 0:
            _files_ = files
            a = files[0].split('\\')
            text = f"{a[-2]}"
            for file in files:
                check_files = []
                a = file.split('\\')
                text += f"|{a[-1]}"
                if file in _files_:
                    for _file_ in _files_:
                        if file != _file_:
                            if cmp(file, _file_):
                                check_files.append(_file_)
                                a = _file_.split('\\')
                                text += f"&{a[-1]}"
                    check_files.append(file)
                if len(check_files) == 1 or not(file in _files_):
                    text += "&nofile"
                _files_ = set(_files_) - set(check_files)
        else:
            text = "nodata"
        return text
    except:
        return ""
# 執行處理重複檔案
def __repeat_files_doing__(folder, type, infolder):
    try:
        folder = folder.replace('|', "\\")
        files = glob(folder)
        repeat_files = dict()
        if len(files) != 0:
            check_file = []
            for file in files:
                if not(file in check_file):
                    repeat_files[file] = []
                    for file_a in files:
                        if file != file_a:
                            if cmp(file, file_a):
                                repeat_files[file].append(file_a)
                                check_file.append(file_a)
                    check_file.append(file)
                    if repeat_files[file] == []:
                        repeat_files.pop(file, f"錯誤...")        
            n = 0
            if  repeat_files != {}:
                if type == "delete":
                    for key in [*repeat_files]:
                        for file in repeat_files[key]:
                            remove(file)
                            n += 1
                    return "完成！", f"已刪除{n}個重複檔案完成！"
                elif type == "move":
                    infolder = infolder.replace('|', "\\")
                    for key in [*repeat_files]:
                        move(key, infolder)
                        n += 1
                        for file in repeat_files[key]:
                            move(file, infolder)
                            n += 1
                    return "完成！", f"已移動{n}個重複檔案完成！"
            else:
               return "你在搞..." , ""
        else:
            return "你在搞...", ""
    except:
        return "錯誤！", ""

# 變更設定
def setting_save(folder, hint):
    try:
        global setting
        # 變更預設資料夾位置
        folder = folder if folder != "null_setting" else setting["folder"]
        setting["folder"] = folder
        # 關閉提示
        hint = int(hint)
        setting["a_box"] = hint

        with open('static\setting.json',mode='w',encoding='utf8') as json_file:
            dump(setting, json_file, indent=4)
        return "變更成功！"
    except:
        return "錯誤！"

##############################
############ 主頁 ############
@app.route("/")
def start_():
    return render_template("index.html", setting_a_box=setting["a_box"], folder=setting["folder"])
##############################
##############################

##############################
###### 批次檔案重新命名 ######
@app.route("/rename/findfilesfrom=<from_folder>", methods = ["GET"])
def rename_from_folder(from_folder):
    text = __rename_ready_files__(from_folder)
    return render_template("rename.html", setting_a_box=setting["a_box"], text=text)

@app.route("/rename/doing/files_f=<files_f>&files_e=<files_e>&files_i=<files_i>&files_n=<files_n>&folder=<folder>", methods = ["GET"])
def rename_doing(files_f, files_e, files_i, files_n, folder):
    result = __rename_files_doing__(files_f, files_e, files_i, files_n, folder)
    text = __rename_ready_files__(folder)
    return render_template("doing.html", head_title="SYS>rename>over", title="批次檔案重新命名結果", type="rename", folder=setting["folder"], result=result, text=text)
##############################
##############################

##############################
######## 處理重複檔案 ########
@app.route("/repeat/findfilesfrom=<from_folder>", methods = ["GET"])
def repeat_(from_folder):
    text = __find_repeat_files__(from_folder)
    return render_template("repeat.html", setting_a_box=setting["a_box"], text=text)

@app.route("/repeat/doing/folder=<folder>&type=<type>&infolder=<infolder>", methods = ["GET"])
def repeat_doing(folder, type, infolder):
    result, text = __repeat_files_doing__(folder, type, infolder)
    return render_template("doing.html", head_title="SYS>repeat>over", title="重複檔案處理結果", type="repeat", folder=setting["folder"], result=result, text=text)
##############################
##############################

##############################
########## 設定儲存 ##########
@app.route("/setting")
def setting_():
    folder = setting["folder"].replace('|', "\\")[0:-2]
    setting_a_box = "" if setting["a_box"]==1 else "checked"
    hint = "提示已開啟" if setting["a_box"]==1 else "提示已關閉"
    return render_template("setting.html", folder=folder, setting_a_box=setting_a_box,hint=hint)

@app.route("/setting/doing/folder=<folder>&hint=<hint>", methods = ["GET"])
def setting_doing(folder, hint):
    result = setting_save(folder, hint)
    return render_template("setting_doing.html", result=result)
##############################
##############################


##############################
############ 執行 ############
if __name__ == "__main__":
    app.debug = True
    app.run()
##############################
##############################