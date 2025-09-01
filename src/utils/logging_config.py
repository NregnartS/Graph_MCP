# -*- coding: utf-8 -*-

import os
import logging


def setup_logging():
    """配置应用程序日志系统"""
    try:
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 确保日志目录存在 - 使用项目根目录作为基准路径
        log_dir = os.path.join(project_root, 'logs')
        
        # 检查并创建日志目录
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
                # 验证目录权限
                if not os.access(log_dir, os.W_OK):
                    print(f"警告: 日志目录缺少写权限")
            except Exception as e:
                print(f"创建日志目录失败: {str(e)}")
        
        # 首先创建logger实例，避免循环引用
        logger = logging.getLogger('PlottingService')
        logger.setLevel(logging.DEBUG)  # 默认直接设置为DEBUG级别，确保所有日志都能被捕获
        logger.propagate = False  # 防止日志传播到root logger
        
        # 清除已有的处理器
        if logger.handlers:
            logger.handlers.clear()
        
        # 创建格式化器，添加更多信息
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # 控制台默认只显示INFO及以上
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 主日志文件处理器 - 记录所有级别日志
        main_file_path = os.path.join(log_dir, 'plotting_service.log')
        try:
            # 尝试创建或打开文件以验证权限
            with open(main_file_path, 'a') as f:
                f.write("\n--- 服务重启日志记录开始 ---")
            
            main_file_handler = logging.FileHandler(main_file_path, encoding='utf-8')
            main_file_handler.setLevel(logging.DEBUG)  # 记录所有级别日志
            main_file_handler.setFormatter(formatter)
            logger.addHandler(main_file_handler)
        except Exception as e:
            print(f"配置主日志文件失败: {str(e)}")
        
        # 错误日志文件处理器 - 只记录错误及以上级别日志
        error_file_path = os.path.join(log_dir, 'plotting_service_error.log')
        try:
            # 尝试创建或打开文件以验证权限
            with open(error_file_path, 'a') as f:
                f.write("\n--- 服务重启错误日志记录开始 ---")
            
            error_file_handler = logging.FileHandler(error_file_path, encoding='utf-8')
            error_file_handler.setLevel(logging.ERROR)  # 只记录错误及以上
            error_file_handler.setFormatter(formatter)
            logger.addHandler(error_file_handler)
        except Exception as e:
            print(f"配置错误日志文件失败: {str(e)}")
        
        # 配置第三方库的日志级别，避免过多调试信息
        logging.getLogger('mcp').setLevel(logging.WARNING)
        logging.getLogger('fastapi').setLevel(logging.WARNING)
        logging.getLogger('uvicorn').setLevel(logging.WARNING)
        
        # 记录日志配置信息
        logger.info("日志系统初始化完成")
        logger.info(f"当前工作目录: {os.getcwd()}")
        logger.info(f"项目根目录: {project_root}")
        logger.info(f"日志目录: {log_dir}")
        
        return logger
        
    except Exception as e:
        print(f"日志系统初始化失败: {str(e)}")
        # 创建一个简单的备用日志记录器，确保至少有日志输出
        logger = logging.getLogger('PlottingService')
        logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        logger.addHandler(console_handler)
        logger.error(f"日志系统初始化失败，已启用备用控制台日志: {str(e)}")
        return logger


# 初始化日志系统并导出logger实例
logger = setup_logging()