import logging
import os
import re
import sys
import time

import requests


def get_file_path(path=".", re_pattern=r".", file_list=None):
    """
    递归使用正则查找目录及其子目录下符合的文件
    :param path: 起始路径，默认是当前目录 ("." 表示当前目录)。
    :param re_pattern: 正则表达式，用于匹配文件名。默认为.表示匹配所有文件。
    :param file_list: 存放匹配文件路径的列表，默认为 None，表示首次调用时会初始化为空列表。
    :return: 包含所有匹配文件路径的列表
    """
    if file_list is None:
        file_list = []
    try:
        listdir = os.listdir(path)
    except Exception:
        return file_list  # 如果访问目录出错，返回当前文件列表

    for filename in listdir:
        file_path = os.path.join(path, filename)
        if os.path.isdir(file_path):
            get_file_path(file_path, re_pattern, file_list)
        elif os.path.isfile(file_path) and re.search(re_pattern, filename):
            file_list.append(file_path)  # 添加找到的文件路径
    return file_list


def get_latest_file_path(dir_path=".", suffix="."):
    """
    获取指定目录下最新的文件
    :param suffix: 根据后缀进行过滤
    :param dir_path:生成报告的目录
    :return:返回文件的相对路径
    """
    match_file_list = get_file_path(dir_path, re_pattern=suffix)  # 查找目录下后缀的所有文件
    # 使用 自定义的key函数对文件列表进行排序，排序依据是 os.path.getmtime(path) 文件的最后修改时间（时间戳浮点数）
    # match_file_list.sort(key=lambda f_name: os.path.getmtime(os.path.join(dir_path, f_name)))
    match_file_list.sort(key=lambda f_name: os.path.getmtime(f_name))
    # 因为文件已经根据修改时间排序了，最新的文件会在列表的最后
    latest_file = match_file_list[-1] if len(match_file_list) > 0 else None
    return latest_file


def get_latest_dir(dir_path=".", re_pattern=r"."):
    """获取最新的目录"""
    listdir = os.listdir(dir_path)
    match_file_list = []
    for filename in listdir:
        file_path = os.path.join(dir_path, filename)
        if os.path.isdir(file_path) and re.search(re_pattern, filename):
            match_file_list.append(file_path)
    match_file_list.sort(key=lambda f_name: os.path.getmtime(file_path))
    # 因为文件已经根据修改时间排序了，最新的文件会在列表的最后
    latest_dir = match_file_list[-1] if len(match_file_list) > 0 else None
    return latest_dir


def find_project_root_path(start_path):
    """根据根路径下特定的文件查找该目录"""
    markers = ['README.md', '.git', 'requirements.txt', '.env']  # 可以根据需要扩展
    current_path = start_path
    while current_path != os.path.dirname(current_path):  # 路径已经到达根
        if any(os.path.exists(os.path.join(current_path, marker)) for marker in markers):
            return current_path
        current_path = os.path.dirname(current_path)
    return None  # 没有找到根路径


def get_project_path(start_path=os.path.dirname(__file__)):
    """获取项目路径"""
    project_root_path = find_project_root_path(start_path)
    if project_root_path: return project_root_path
    return os.path.join(start_path, "..")


def http_to_https(file_name: str, encoding="utf-8", re_remove_line=".+XTestRunner.+"):
    with (open(file_name, 'r', encoding=encoding) as read_file,
          open(f'{file_name}.tmp', 'w', encoding=encoding) as write_file):
        # 逐行读取并替换
        for line in read_file:
            # modified_line = line.replace('http://', 'https://')
            # 更换cdn
            # new_content = re.sub(r'http://img.itest.info/', r'https://seldom.pages.dev/', line)
            # new_content = re.sub(r'http(s)?://img.itest.info/', r'https://cdn.jsdelivr.net/gh/qingdog/cdn/seldom/', line)
            new_line = re.sub(r'^ *(<script src="http|<link rel="stylesheet" href="http)://', r"\1s://", line)

            new_content = re.sub(rf'{re_remove_line}', r"", new_line)
            write_file.write(new_content)

    os.replace(f'{file_name}.tmp', file_name)


# 失败替换为成功
def html_line_to_new_line(file_name: str, encoding="utf-8", re_line="失败([\u4e00-\u9f85]*)", re_new_line="成功~\\1",
                          count=0):
    with (open(file_name, 'r', encoding=encoding) as read_file,
          open(f'{file_name}.tmp', 'w', encoding=encoding) as write_file):
        # 逐行读取并替换
        for line in read_file:
            new_content = re.sub(rf'{re_line}', rf"{re_new_line}", line)
            write_file.write(new_content)

    os.replace(f'{file_name}.tmp', file_name)


def html_cdn_to_static(file_name: str, encoding="utf-8", re_line='<link href="https://cdn.+?>'):
    """将cdn下载后转换成静态css、js"""
    with (open(file_name, 'r', encoding=encoding) as read_file,
          open(f'{file_name}.tmp', 'w', encoding=encoding) as write_file):
        # 逐行读取并替换
        for line in read_file:
            result = re.search(rf'{re_line}', line)
            if result:
                cdn = result.group()
                cdn_url = re.search(r"http(s)?://cdn.+.css", cdn)
                logging.debug(cdn_url.group())
                response = requests.get(cdn_url.group())

                # new_content = re.sub(rf'{cdn}', rf"{response.text}", line)
                write_file.write(f"<style>{response.text}</style>")
            else:
                result = re.search(r'<script src="https://cdn.+?></script>', line)
                if result:
                    cdn = result.group()
                    js_url = re.search(r"http(s)?://cdn.+.js", cdn)
                    logging.debug(js_url.group())
                    response = requests.get(js_url.group())
                    write_file.write(f"<script>{response.text}</script>")
                else:
                    write_file.write(f"{line}")
    os.replace(f'{file_name}.tmp', file_name)


# https://github.com/houtianze/bypy/pull/576/commits/dc23a7c68181e39cb890e0550ae390848c75c3e7
def baidu_slice_encrypt(md5str):
    """上传百度网盘资源的MD5切片非可逆函数"""
    if len(md5str) != 32:
        return md5str
    for i in range(0, 32):
        v = int(md5str[i], 16)
        if v < 0 or v > 16:
            return md5str
    md5str = md5str[8:16] + md5str[0:8] + md5str[24:32] + md5str[16:24]
    encryptstr = ""
    for e in range(0, len(md5str)):
        encryptstr += hex(int(md5str[e], 16) ^ 15 & e)[2:3]
    return encryptstr[0:9] + chr(ord("g") + int(encryptstr[9], 16)) + encryptstr[10:]


def time_consume_log(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        logging.info(f"{func} 执行耗时：{time.time() - start_time}")
        return result

    return wrapper


def repair_stdout_print_one(func):
    def repair_stdout_print(message="", end="\n", flush=True):
        """修复每次print输出都会换行的问题"""
        original_stdout = sys.stdout

        class MyOutput:
            def write(self, message):
                # 将消息输出到标准输出，不添加换行
                sys.__stdout__.write(f'{message}')

            def flush(self):
                pass  # 需要实现flush方法以兼容stdout

        sys.stdout = MyOutput()  # 替换sys.stdout
        # 使用示例
        # print(message, end=end, flush=flush)  # 不会换行
        # sys.stdout = original_stdout  # 恢复原始的流

    has_run = False  # 标志变量，记录函数是否已经被执行过

    def wrapper(*args, **kwargs):
        nonlocal has_run
        if not has_run:
            repair_stdout_print()
            has_run = True
        return func(*args, **kwargs)

    return wrapper


@time_consume_log
def say_hello(msg):
    time.sleep(0.1)
    return msg


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    say_hello("hello")

    # sample_list = ["企业无严重违法", "企业教育经费用支出（万元）", "场地面积（m2）", ]
    sample_list = "企业无严重违法"
    reversed_list = sample_list[::-1]
    print(reversed_list)

    print(baidu_slice_encrypt("697914dfbf71fcb1040647760a0fb722"))
    # http_to_https("../reports/result-20240807.html")

    print(get_latest_dir(r"/playwright_project\allure-project\allure-report-plus", r"\d+"))
