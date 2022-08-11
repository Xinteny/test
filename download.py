import os, sys
import math
import urllib.request
import PIL.Image as Image
from PIL import ImageDraw, ImageFont

import urllib
import time
import random
import datetime
import tarfile


def downloadImage(img_url, fname, mylog):
    try:
        urllib.request.urlretrieve(img_url, filename=fname)
    except IOError as e:
        print("--", fname, "->", e)
        print(img_url, file=mylog)
    except Exception as e:
        print("--", fname, "->", e)
        print(img_url, file=mylog)


def downloadImage2(img_url, fname, mylog):
    user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 (KHTML, like Gecko) ' \
                 'Version/5.0.5 Safari/533.21.1 '
    headers = {'User-Agent': user_agent}
    try:
        req = urllib.request.Request(img_url, headers=headers)
        response = urllib.request.urlopen(req)
        bytes = response.read()
    except Exception as e:
        print("--", fname, "->", e)
        print(img_url, file=mylog)
        sys.exit(1)

    if bytes.startswith(b"<html>"):
        print("-- forbidden", fname)
        print(img_url, file=mylog)
        sys.exit(1)

    print("-- saving", fname)

    f = open(fname, 'wb')
    f.write(bytes)
    f.close()

    time.sleep(1 + random.random())


def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)


def getImageUrl(x, y, zoom):
    # zoom_level/x(竖着)/y(横着)

    # 高德瓦片，wprd03想必是和谷歌一样，有多个服务器提供服务。测试下来可以取到01到04。
    img_url = 'https://wprd01.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&style=6'.format(x=x, y=y, z=zoom)

    # 谷歌瓦片，x,y含义相同,s zoom_level
    # https://mt0.google.cn/vt/lyrs=s@180000000&hl=zh-CN&gl=cn&src=app&x=1726638&y=794572&z=21&s=Ga

    return img_url


def getAndCheckImageFilePath(file_path, x, y, zoom, file_pos):
    path = file_path + "/" + str(zoom) + "/" + str(x) + "/" + str(file_pos)
    if not os.path.exists(path):
        os.makedirs(path)
    return getImageFilePath(file_path, x, y, zoom, file_pos)


def getImageFilePath(file_path, x, y, zoom, file_pos):
    return file_path + "/" + str(zoom) + "/" + str(x) + '/' + str(file_pos) + '/' + str(y) + '.png'


def getImageGzFilePath(file_path, x, y, zoom, file_pos):
    return file_path + "/" + str(zoom) + "_" + str(x) + '_' + str(file_pos)  + '.gz'

# 图片拼接
def mergeAllImageToOne(file_path, zoom, params):
    xmin = params[0]
    ymin = params[1]
    xmax = xmin + params[2]
    ymax = ymin + params[3]
    mw = 256
    toImage = Image.new('RGB', (256 * (xmax - xmin), 256 * (ymax - ymin)))

    for x in range(xmin, xmax):
        for y in range(ymin, ymax):
            fname = getImageFilePath(file_path, x, y, zoom)
            fromImage = Image.open(fname)
            fromImage = fromImage.convert('RGB')
            draw = ImageDraw.Draw(fromImage)

            # 添加每个瓦片的文字信息
            # fontSize = 18
            # setFont = ImageFont.truetype('C:/windows/fonts/arial.ttf', fontSize)
            # fillColor = "#ffff00"
            pos = num2deg(x, y, zoom)
            # text = 'Tile: ' + str(x) + "," + str(y) + "," + str(zoom)
            # text2 = 'Lat: %.6f' % pos[0]
            # text3 = 'Lon: %.6f' % pos[1]
            # draw.text((1, 1), text, font=setFont, fill=fillColor)
            # draw.text((1, 1 + fontSize), text2, font=setFont, fill=fillColor)
            # draw.text((1, 1 + 2 * fontSize), text3, font=setFont, fill=fillColor)

            # 添加每个瓦片的边框线条
            # draw.rectangle([0, 0, mw - 1, mw - 1], fill=None, outline='red', width=1)

            # 将每个瓦片的小图绘制到大图里面。
            toImage.paste(fromImage, ((x - xmin) * mw, (y - ymin) * mw))

    toImage.save(file_path + '/' + str(zoom) + '/preview.png')
    toImage.close()


# 图片拼接
def downloadMapAllImage(file_path, zoom, params):
    xmin = params[0]
    ymin = params[1]
    xmax = xmin + params[2]
    ymax = ymin + params[3]

    if not os.path.exists(file_path):
        os.makedirs(file_path)
    mylog = open(file_path + '/err.log', mode='a', encoding='utf-8')

    cnt = 0
    pre_file_pos = 0
    for x in range(xmin, xmax):
        for y in range(ymin, ymax):

            # 1张4k,100Mb = 25600张图

            img_url = getImageUrl(x, y, zoom)
            print(img_url)

            # here
            file_pos = int(cnt / 25600)
            if file_pos != pre_file_pos or y == ymax-1:  # 够一个包了或者是最后一个包
                img_dir = getAndCheckImageFilePath(file_path, x, y, zoom, pre_file_pos)
                tar_path = getImageGzFilePath(file_path, x, y, zoom, pre_file_pos)
                make_targz(tar_path, img_dir)
            img_savepath = getAndCheckImageFilePath(file_path, x, y, zoom, file_pos)

            print(img_savepath)

            if not os.path.exists(img_savepath):
                downloadImage(img_url, img_savepath, mylog)
                # downloadImage2(img_url, img_savepath, mylog)

            cnt += 1
            pre_file_pos = file_pos

    mylog.close()


#################################################################


# 一次性打包整个根目录。空子目录会被打包。
# 如果只打包不压缩，将"w:gz"参数改为"w:"或"w"即可。
def make_targz(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


# 逐个添加文件打包，未打包空子目录。可过滤文件。
# 如果只打包不压缩，将"w:gz"参数改为"w:"或"w"即可。
def make_targz_one_by_one(output_filename, source_dir):
    tar = tarfile.open(output_filename, "w:gz")
    for root, dir, files in os.walk(source_dir):
        for file in files:
            pathfile = os.path.join(root, file)
            tar.add(pathfile)
    tar.close()


##################################################################


if __name__ == '__main__':
    starttime = datetime.datetime.now()
    # file_path = 'D:/Workspace/Yunqi/data/Gaode_Satellite_Image'
    file_path = os.getenv('OUTPUT_PATH')
    print(file_path)
    # (1) 全球地图
    # zoom = 4
    # params = [0, 0, pow(2, zoom), pow(2, zoom)]

    # (2) 中国地图
    # zoom = 9
    # params = [354, 165, 106, 91]

    # (3) 局部地图
    # zoom = 18
    # params = [215768, 99253, 4, 4]
    for zoom in range(3):
        params = [0, 0, pow(2, zoom), pow(2, zoom)]
        downloadMapAllImage(file_path, zoom, params)
        # mergeAllImageToOne(file_path, zoom, params)
        endtime = datetime.datetime.now()
        print("ok", (endtime - starttime).seconds)
