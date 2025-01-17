import logging
import os
import sys
import time
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


def create_file_handler(logging_format, log_date_format=None, style: Literal["%", "{", "$"] = "%", defaults=None):
    """创建并返回一个文件处理器"""
    # current_directory = os.path.dirname(os.path.abspath(__file__))
    current_directory = utils.myutil.get_project_path()  # 存储日志的目录
    log_path_name = os.path.join(current_directory, "logs", f'{time.strftime("%Y%m%d")}.log')
    # if not os.path.exists(current_directory): os.makedirs(log_path_name)  # 创建目录

    file_handler = logging.FileHandler(log_path_name, encoding="UTF-8", mode='a')
    file_handler.setFormatter(logging.Formatter(fmt=logging_format, datefmt=log_date_format, style=style, defaults=defaults))
    return file_handler


def create_console_handler(logging_format, log_date_format, style: Literal["%", "{", "$"] = "%", defaults=None):
    """创建并返回一个控制台处理器（添加颜色代码）"""
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter(fmt=logging_format, datefmt=log_date_format, style=style, defaults=defaults))
    return console_handler


def configure_logging(loger_name=None):
    """配置日志处理器"""
    logging_format = "{prefix}[{asctime}] - [{filename}:{lineno}] {levelname} {user}{message}"
    log_date_format = "%Y-%m-%d_%H:%M:%S"
    logger = logging.getLogger(loger_name)
    log_file_name = None
    if len(logger.handlers) == 0:  # 没有handler意为未使用过logger
        '''logging.basicConfig(level=logging.INFO, format=f'[%(asctime)s] - [%(filename)s:%(lineno)d] %(levelname)s %(message)s', datefmt=f"%Y-%m-%d_%H:%M:%S",
                            handlers=[logging.FileHandler(f"{time.strftime("%Y-%m-%d")}.log", encoding="UTF-8", mode='a'), logging.StreamHandler(sys.stdout)])'''
        file_handler = create_file_handler(logging_format, log_date_format, style="{", defaults={'user': '', 'prefix': ''})
        logger.addHandler(file_handler)
        logger.addHandler(create_console_handler(logging_format, log_date_format, style="{", defaults={'user': '', 'prefix': ''}))
        log_file_name = file_handler.baseFilename
    else:
        has_file_handler = any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)
        # 修改 StreamHandler 格式
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setFormatter(ColoredFormatter(fmt=logging_format, datefmt=log_date_format, style="{", defaults={'user': '', 'prefix': ''}))
        # 如果没有文件处理器，则添加文件处理器
        if not has_file_handler:
            file_handler = create_file_handler(logging_format, log_date_format)
            logger.addHandler(file_handler)
            log_file_name = file_handler.baseFilename
    logger.setLevel(logging.INFO)
    return logger, log_file_name


def main():
    """主函数，执行日志配置"""
    logger, log_file_name = configure_logging()
    return logger, log_file_name


if __name__ == '__main__':
    try:
        import sys

        sys.path.extend(['D:\\mytest\\UnittestDemo', '/mnt/d/mytest/UnittestDemo'])
        from utils import color_format_logging

        color_format_logging.main()
    except Exception as e:
        logging.critical(e, exc_info=True)

    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("先换行再输出DEBUG级别的日志", extra={"prefix": "\n"})
    logging.info("这是一个INFO级别的日志", extra={"user": "lucy"})
    logging.warning("\n这是一个WARNING级别的日志")
    logging.error("这是一个ERROR级别的日志", exc_info=True)
    logging.critical("这是一个CRITICAL级别的日志", exc_info=False)

    # 不继承root logger，不保持不同库的logging之间的日志格式一致，这里的logger使用独立的自定义格式输出日志
    logging.getLogger("mylogger").parent = None
    logging.getLogger("mylogger").warning("this is mylogger,no set formatter.")
