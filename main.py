import os
import time
#import shutil
from flask import Flask,render_template,url_for,redirect,send_from_directory,request

app = Flask(__name__)

# 浏览目录
@app.route('/')
@app.route('/<rel_path>/')
def ListDir(rel_path=''):
    if rel_path == '':
        # 名字为空，切换到根目录
        os.chdir(app.config["ROOT_FOLDER"])
    else:
        abs_path = app.config["ROOT_FOLDER"] + os.sep + rel_path
        #  如果是文件，则下载
        if os.path.isfile(abs_path):
            return redirect(url_for('Download', abs_path=abs_path))
        #  如果是目录，切换到该目录下面
        else:
            os.chdir(abs_path)
    current_abs_dir_path = os.getcwd()
    current_list = os.listdir(current_abs_dir_path)
    contents = []
    for i in sorted(current_list):
        abs_path = current_abs_dir_path + os.sep + i
        # 如果是目录，在后面添加一个sep
        if os.path.isdir(abs_path):
            extra = os.sep
        else:
            extra = ''
        content = {}
        content['name'] = i + extra
        content['mtime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.stat(abs_path).st_mtime))
        if os.path.isfile(abs_path):
            content['type'] = abs_path.split(".")[-1]
            content['size'] = str(round(os.path.getsize(abs_path) / 1024)) + ' KB'
        else:
            content['type'] = "文件夹"
            content['size'] = ""
        contents.append(content)
    # 上级目录
    rel_parent_dir_path = os.path.dirname(rel_path)
    rel_parent_dir_path = os.path.dirname(rel_parent_dir_path)
    if rel_parent_dir_path != "":
        rel_parent_dir_path += os.sep
    return render_template("home.html", contents=contents, rel_dir_path=rel_path, rel_parent_dir_path=rel_parent_dir_path, ossep=os.sep)

# 下载
@app.route('/download/<abs_path>')
def Download(abs_path):
    filename = abs_path.split(os.sep)[-1]
    abs_dir_path = abs_path[:-len(filename)]
    return send_from_directory(abs_dir_path, filename, as_attachment=True)

# 上传
@app.route('/upload', methods=['POST'])
def Upload():
    current_abs_dir_path = os.getcwd()
    if "selectfile" not in request.files:
        return "No file part"
    for file in request.files.getlist('selectfile'):
        abs_path = current_abs_dir_path + os.sep + file.filename
        print("upload file path= " + abs_path)
        file.save(abs_path)
    # 相对路径
    rel_dir_path = current_abs_dir_path.replace(app.config["ROOT_FOLDER"], "")
    print("upload rel_dir_path= " + rel_dir_path)
    if len(rel_dir_path) > 0 and rel_dir_path[0] == "\\":
        rel_dir_path = rel_dir_path[1:]
    if rel_dir_path != "":
        rel_dir_path += os.sep
    return redirect(url_for("ListDir", rel_path=rel_dir_path))

# 删除
@app.route('/delete/<rel_path>')
def Delete(rel_path):
    abs_path = os.path.join(app.config["ROOT_FOLDER"], rel_path)
    print("delete path= " + abs_path)
    if os.path.isfile(abs_path):
        os.remove(abs_path)
    elif os.path.isdir(abs_path):
        #shutil.rmtree(abs_path, ignore_errors=True) # 递归删除指定目录下的所有子目录、文件
        os.rmdir(abs_path)

    # 相对路径
    filename = rel_path.split(os.sep)[-1]
    rel_dir_path = rel_path[:-len(filename)]
    print("rel_dir_path=" + rel_dir_path)
    return redirect(url_for('ListDir', rel_path=rel_dir_path))

if __name__ == '__main__':
    # 根目录
    app.config["ROOT_FOLDER"] = "F:\\FileServer_RootDir"
    # 启动
    app.run(host="0.0.0.0", debug=True)
