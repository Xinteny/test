import os
import gzip
def un_gz(file_name):
    """ungz zip file"""
    f_name = file_name.replace(".gz", "")
    #获取文件的名称，去掉
    g_file = gzip.GzipFile(file_name)
    #创建gzip对象
    outpath = os.path.join(os.getenv('OUTPUT_PATH'), f_name)
    open(outpath, "wb+").write(g_file.read())
    #gzip对象用read()打开后，写入open()建立的文件里。
    g_file.close()
    #关闭gzip对象
print(1111)
path = os.getenv('DATA_PATH')
print(path)
name = os.listdir(path)
filename = os.path.join(path, name)
un_gz(filename)
# print(os.getenv('DATA_PATH'))
# print(os.path.join(os.getenv('DATA_PATH'), '自定义下载文件名'))
# os.path.join(os.getenv('OUTPUT_PATH'), '生成文件名')
