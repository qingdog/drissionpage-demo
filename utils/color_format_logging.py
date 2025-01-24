import datetime
import logging
import sys
import os
import traceback
from typing import Literal

import utils.myutil


class ColoredFormatter(logging.Formatter):
    """定义一个日志格式化器，添加颜色代码"""

    def __init__(self, fmt=None, datefmt=None, style='%', validate=True, *, defaults=None):
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)

    def format(self, record):
        color_codes = {
            logging.DEBUG: '\033[94m',  # 蓝色
            logging.INFO: '\033[92m',  # 绿色
            logging.WARNING: '\033[93m',  # 黄色
            logging.ERROR: '\033[91m',  # 红色
            logging.CRITICAL: '\033[95m',  # 紫色
            "nocolor": '\033[0m'
        }
        # critical级别输出紫色信息 error级别输出红色信息
        record.levelname = color_codes.get(record.levelno, '\033[0m') + record.levelname + '\033[0m'
        if record.levelno == logging.CRITICAL:
            record.msg = f"{color_codes.get(logging.CRITICAL)}{record.msg}{color_codes.get("nocolor")}"
            record.exc_text = f"{color_codes.get(logging.CRITICAL)}{record.exc_text}{color_codes.get("nocolor")}"
        elif record.levelno == logging.ERROR:
            record.exc_text = f"{color_codes.get(logging.ERROR)}{record.exc_text}{color_codes.get("nocolor")}"
        return super().format(record)


def create_file_handler(log_path_name=None, log_format="%[%(asctime)] - [%(filename):%(lineno)] %(levelname) %(message)", date_format="%Y-%m-%d_%H:%M:%S",
                        style: Literal["%", "{", "$"] = "%", defaults=None):
    """创建并返回一个日志的文件处理器"""
    if log_path_name is None:
        # current_directory = os.path.dirname(os.path.abspath(__file__))
        current_directory = utils.myutil.get_project_path()  # 存储日志的目录
        # 获取当前日期和 ISO 日历信息
        today = datetime.date.today()
        year, week, _ = today.isocalendar()
        # 构造日志文件路径：年月周
        log_path = os.path.join(current_directory, "logs")
        log_path_name = os.path.join(log_path, f'{today.strftime("%Y%m")}_{week}1.log')

    dir_path = os.path.dirname(log_path_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)  # 创建目录
        print(f"\033[33m创建目录：{dir_path}\033[0m")

    file_handler = logging.FileHandler(log_path_name, encoding="UTF-8", mode='a')
    file_handler.setFormatter(logging.Formatter(fmt=log_format, datefmt=date_format, style=style, defaults=defaults))
    return file_handler


def create_console_handler(log_format="%[%(asctime)] - [%(filename):%(lineno)] %(levelname) %(message)", date_format="%Y-%m-%d_%H:%M:%S",
                           style: Literal["%", "{", "$"] = "%", defaults=None):
    """创建并返回一个日志的控制台处理器（添加颜色代码）"""
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter(fmt=log_format, datefmt=date_format, style=style, defaults=defaults))
    return console_handler


def configure_logging(logger_name=None, log_path=None):
    """配置日志处理器"""
    log_format = "{prefix}[{asctime}] - [{filename}:{lineno}] {levelname} {user}{message}"
    logger = logging.getLogger(logger_name)
    log_file_name = None
    if len(logger.handlers) == 0:  # 没有handler意为未使用过logger
        '''logging.basicConfig(level=logging.INFO, format=f'[%(asctime)s] - [%(filename)s:%(lineno)d] %(levelname)s %(message)s', datefmt=f"%Y-%m-%d_%H:%M:%S",
                            handlers=[logging.FileHandler(f"{time.strftime("%Y-%m-%d")}.log", encoding="UTF-8", mode='a'), logging.StreamHandler(sys.stdout)])'''
        file_handler = create_file_handler(log_path_name=log_path, log_format=log_format, style="{", defaults={'user': '', 'prefix': ''})
        logger.addHandler(file_handler)
        logger.addHandler(create_console_handler(log_format=log_format, style="{", defaults={'user': '', 'prefix': ''}))
        log_file_name = file_handler.baseFilename
    else:
        has_file_handler = any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)
        # 修改 StreamHandler 格式
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setFormatter(ColoredFormatter(fmt=log_format, style="{", defaults={'user': '', 'prefix': ''}))
        # 如果没有文件处理器，则添加文件处理器
        if not has_file_handler:
            file_handler = create_file_handler(log_path_name=log_path, log_format=log_format, style="{", defaults={'user': '', 'prefix': ''})
            logger.addHandler(file_handler)
            log_file_name = file_handler.baseFilename
    logger.setLevel(logging.INFO)
    return logger, log_file_name


def main(config_logger_name: str = None, log_path: str = None):
    """
    主函数，执行日志配置
    :param config_logger_name: logger的名称
    :param log_path: 记录日志的文件路径
    :return: logger对象、记录日志的文件路径
    """
    logger, log_file_path = configure_logging(logger_name=config_logger_name, log_path=log_path)
    return logger, log_file_path


if __name__ == '__main__':
    try:
        import sys

        sys.path.extend(['D:\\mytest\\UnittestDemo', '/mnt/d/mytest/UnittestDemo'])
        from utils import color_format_logging

        color_format_logging.main()
    except Exception as e:
        print(f"\033[34m{traceback.format_exc()}\033[0m")
        logging.getLogger(logging.INFO)

    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("先换行再输出DEBUG级别的日志", extra={"prefix": "\n"})
    logging.info("这是一个INFO级别的日志", extra={"user": "lucy"})
    logging.warning("\n这是一个WARNING级别的日志")
    logging.error("这是一个ERROR级别的日志", exc_info=True)
    logging.critical("这是一个CRITICAL级别的日志", exc_info=False)

    # 不继承root logger，不保持不同库的logging之间的日志格式一致，这里的logger使用独立的自定义格式输出日志
    logging.getLogger("mylogger").parent = None
    logging.getLogger("mylogger").warning("this is mylogger,no set formatter.")
