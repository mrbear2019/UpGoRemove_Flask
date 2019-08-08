# -*- coding: utf-8 -*-
# 蓝本中定义的程序路由
import os, zipfile, random, base64, uuid
from werkzeug.utils import secure_filename
from removebg import RemoveBg
import PIL.Image as Image
import shutil
from datetime import datetime
from flask import render_template, session, redirect, url_for, request, abort, current_app
from . import main


# class dbKey(db.Model):
#     __tablename__ = 'UG_KEYBOX'
#     id = db.Column(db.Integer, primary_key=True)
#     Rkey = db.Column(db.String(32), unique=True)
#
#
# class dbMac(db.Model):
#     __tablename__ = 'UG_MACBOX'
#     id = db.Column(db.Integer, primary_key=True)
#     userMac = db.Column(db.String(32), unique=True)


def allowed_file(filename):  # 验证上传文件是否符合要求
    return '.' in filename and filename.rsplit('.', 1)[1] in current_app.config.get('ALLOWED_EXTENSIONS')


# def get_mac_address():  # 获取mac地址
#     mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
#     return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])


@main.route('/')
def index():
    if current_app.config.get('API_KEY') == "":
        keyExist = 0
    else:
        keyExist = 1

    # temp = get_mac_address()
    # print(temp)
    # print(dbMac.query.filter_by(userMac=temp).first())
    # db_mac = dbMac(userMac=temp)
    # db.session.add_all([db_mac])
    # db.session.commit()
    return render_template('index.html', keyExist=keyExist)


@main.route('/key', methods=['POST'])
def pushkey():
    if request.method == 'POST':
        # global API_KEY
        temp = request.form['key']
        tempcode = base64.b64encode(temp.encode('utf-8'))
        current_app.config['API_KEY'] = str(tempcode, 'utf-8')
    return redirect(url_for('main.index'))


@main.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':

        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = '密钥无效！'
        else:
            session['username'] = request.form['username']
            return redirect(url_for('main.upload_file'))
    return render_template('upError.html', error=error)


@main.route('/logout/<fileId>/<filename>')
def logout(fileId,filename):
    # session.pop('username', None)

    for userfile in os.listdir(current_app.config.get('DOWNLOAD_FOLDER')):
        if str(fileId) == userfile[0:6]:
            os.remove("%s\%s" % (current_app.config.get('DOWNLOAD_FOLDER'), userfile))
    for userzip in os.listdir(current_app.config.get('ZIP_FOLDER')):
        if str(fileId) == userzip[0:6]:
            os.remove("%s\%s" % (current_app.config.get('ZIP_FOLDER'), userzip))
    for userimg in os.listdir(current_app.config.get('UPLOAD_FOLDER')):
        if str(fileId) == userimg[0:6]:
            os.remove("%s\%s" % (current_app.config.get('UPLOAD_FOLDER'), userimg))

    return 'success'
    # return redirect(url_for('index'))


@main.route('/upload', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        fileId = random.randint(100000, 999999);
        file = request.files['file']  # 获取上传的文件
        if file and allowed_file(file.filename):
            filename = str(fileId)+secure_filename(file.filename)  # 获取上传的文件名
            file.save(os.path.join(current_app.config.get('UPLOAD_FOLDER'), filename))  # 保存文件

            return '{"Code":0,"Message":"保存数据成功","Data":[{"fileId":"'+str(fileId)+'","filename":"'+filename+'"}]}'
        else:
            return '系统检测到非法的文件格式或操作！<a href="/">返回</a> '
    else:
        try:
            name = session['username']
            return render_template('index.html')
        except KeyError:
            abort(401)


@main.route('/drawing/<fileId>/<filename>')
def drawing(fileId,filename):
    key=str(base64.b64decode(current_app.config.get('API_KEY')), 'utf-8')
    rmbg = RemoveBg(key, "error.log")
    for pic in os.listdir(current_app.config.get('UPLOAD_FOLDER')):
        if pic == filename:
            tempPic = pic.rsplit('.', 1)[0]
            url = "%s\%s" % (current_app.config.get('UPLOAD_FOLDER'), filename)
            rmbg.remove_background_from_img_file(url)

            oldImg = url + "_no_bg.png"
            newImg = "%s\%s" % (current_app.config.get('DOWNLOAD_FOLDER'), tempPic + ".png")
            try:
                shutil.move(oldImg, newImg)
                im = Image.open(newImg)
                x, y = im.size
                p = Image.new('RGBA', im.size, (255, 255, 255))
                p.paste(im, (0, 0, x, y), im)
                p.save("%s\%s" % (current_app.config.get('DOWNLOAD_FOLDER'), tempPic + '_white.png'))

                im = Image.open(newImg)
                x, y = im.size
                p = Image.new('RGBA', im.size, (0, 0, 255))
                p.paste(im, (0, 0, x, y), im)
                p.save("%s\%s" % (current_app.config.get('DOWNLOAD_FOLDER'), tempPic + '_blue.png'))

                im = Image.open(newImg)
                x, y = im.size
                p = Image.new('RGBA', im.size, (255, 0, 0))
                p.paste(im, (0, 0, x, y), im)
                p.save("%s\%s" % (current_app.config.get('DOWNLOAD_FOLDER'), tempPic + '_red.png'))

                with zipfile.ZipFile("%s\%s" % (current_app.config.get('ZIP_FOLDER'), tempPic + '.zip'), mode="w") as f:
                    for userfile in os.listdir(current_app.config.get('DOWNLOAD_FOLDER')):
                        if userfile.rsplit('.', 1)[1] == 'png':
                            f.write("%s\%s" % (current_app.config.get('DOWNLOAD_FOLDER'), userfile), userfile)

                #             os.remove("%s\%s" % (current_app.config.get('DOWNLOAD_FOLDER'), userfile))

                # return redirect(url_for('static', filename="zipFile/{}".format(tempPic + ".zip")))

                return redirect(url_for('main.complete_file', filename=filename, fileId=fileId))
            except FileNotFoundError:
                for userimg in os.listdir(current_app.config.get('UPLOAD_FOLDER')):
                    if str(fileId) == userimg[0:6]:
                        os.remove("%s\%s" % (current_app.config.get('UPLOAD_FOLDER'), userimg))
                return render_template('upError.html')
        else:
            continue
        return abort(401)
    return abort(401)


@main.route('/complete/<fileId>')
def complete_json(fileId):
    # os.remove("%s\%s" % (current_app.config.get('UPLOAD_FOLDER'), filename))
    DataNum = 0
    rejson = '{"status":200,"Message":"获取数据成功","Data":['
    for pic in os.listdir(current_app.config.get('DOWNLOAD_FOLDER')):
        if str(fileId) == pic[0:6]:
            DataNum += 1
            temp = ("%s\%s" % (current_app.config.get('DOWNLOAD_FOLDER'), pic)).split('\\')
            imgPath = '/'+temp[-3]+'/'+temp[-2]+'/'+temp[-1]
            rejson += '{"filename":"' + pic[6:] + '","filepath":"' + imgPath + '"},'
    for tempZip in os.listdir(current_app.config.get('ZIP_FOLDER')):
        if str(fileId) == tempZip[0:6]:
            DataNum += 1
            temp = ("%s\%s" % (current_app.config.get('ZIP_FOLDER'), tempZip)).split('\\')
            zipPath = '/'+temp[-3]+'/'+temp[-2]+'/'+temp[-1]
            rejson += '{"filename":"' + tempZip[6:] + '","filepath":"' + zipPath + '"}'
    rejson += ']}'
    if DataNum != 0:
        return rejson
    else:
        return '{"status":400,"Message":"获取数据失败"}'


@main.route('/complete/<fileId>/<filename>')
def complete_file(fileId,filename):
    return render_template('complete.html', fileId=fileId, filename=filename)


