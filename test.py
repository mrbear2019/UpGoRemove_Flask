import os,zipfile,base64



UPLOAD_FOLDER = '%s\\uploadFile' %os.getcwd()  # 上传路径
DOWNLOAD_FOLDER = '%s\\downloadFile' %os.getcwd()  # 下载路径
ZIP_FOLDER = '%s\\zipFile' %os.getcwd()  # 压缩路径
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])  # 允许上传的文件类型


def main():
    encodestr = base64.b64encode('RDovcHJvamVjdC9weXRob24vYXV4c3lzX3d6L2FwcC9zdGF0aWMvTUlTRmlsZS/pu4Tmlofkuq4yMDE4MDQyM++8iDgyMTYwOe+8iS5qcGc='.encode('utf-8'))
    print(str(encodestr, 'utf-8'))
    print(str(base64.b64decode(encodestr), 'utf-8'))
    print(os.urandom(16))


if __name__ == '__main__':
    main()