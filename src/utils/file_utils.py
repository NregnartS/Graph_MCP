#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import uuid
import logging
from typing import Optional, Dict, Any, Union

# 获取logger实例
logger = logging.getLogger(__name__)


# 文件扩展名映射表
IMAGE_EXTENSIONS = {
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'svg': 'image/svg+xml',
    'pdf': 'application/pdf',
    'gif': 'image/gif',
    'bmp': 'image/bmp'
}

# 支持的图表文件格式
SUPPORTED_PLOT_FORMATS = ['png', 'jpg', 'jpeg', 'svg', 'pdf']

# 支持的Mermaid文件格式
SUPPORTED_MERMAID_FORMATS = ['png', 'svg', 'mmd']


def ensure_directory(path: str) -> bool:
    """确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
        
    Returns:
        bool: 操作是否成功
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建目录失败 '{path}': {str(e)}")
        return False


def validate_file_path(file_path: str, allowed_extensions: Optional[list] = None) -> bool:
    """验证文件路径是否合法
    
    Args:
        file_path: 要验证的文件路径
        allowed_extensions: 允许的文件扩展名列表（不包含点），为None时不限制
        
    Returns:
        bool: 路径是否合法
    """
    if not file_path:
        logger.error("文件路径不能为空")
        return False
        
    # 检查是否包含非法字符
    invalid_chars = set('<>":|?*')
    if any(char in invalid_chars for char in file_path):
        logger.error(f"文件路径包含非法字符: {file_path}")
        return False
        
    # 检查路径长度（不同系统有不同限制，这里设置一个合理的值）
    if len(file_path) > 4096:
        logger.error(f"文件路径过长: {file_path}")
        return False
    
    # 检查文件扩展名
    if allowed_extensions:
        ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        if ext not in allowed_extensions:
            logger.error(f"不支持的文件格式 '{ext}'，支持的格式: {', '.join(allowed_extensions)}")
            return False
    
    return True


def get_file_extension(file_path: str) -> str:
    """获取文件扩展名（小写，不含点）
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件扩展名
    """
    return os.path.splitext(file_path)[1].lower().lstrip('.')


def generate_unique_filename(directory: str, base_name: str, extension: str) -> str:
    """生成唯一的文件名
    
    Args:
        directory: 目录路径
        base_name: 基础文件名
        extension: 文件扩展名（不含点）
        
    Returns:
        str: 唯一的文件路径
    """
    # 确保扩展名不含点
    if extension.startswith('.'):
        extension = extension[1:]
        
    # 生成基本路径
    base_path = os.path.join(directory, f"{base_name}.{extension}")
    
    # 如果文件已存在，添加唯一标识符
    if os.path.exists(base_path):
        # 使用UUID生成唯一标识符
        unique_id = uuid.uuid4().hex[:8]
        base_path = os.path.join(directory, f"{base_name}_{unique_id}.{extension}")
    
    return base_path


def generate_temp_file(directory: str, prefix: str = 'temp', extension: str = 'tmp') -> str:
    """生成临时文件路径
    
    Args:
        directory: 目录路径
        prefix: 文件名前缀
        extension: 文件扩展名（不含点）
        
    Returns:
        str: 临时文件路径
    """
    # 确保目录存在
    ensure_directory(directory)
    
    # 生成唯一的临时文件名
    unique_id = uuid.uuid4().hex[:8]
    temp_file_path = os.path.join(directory, f"{prefix}_{unique_id}.{extension}")
    
    return temp_file_path


def get_file_mime_type(file_path: str) -> Optional[str]:
    """获取文件的MIME类型
    
    Args:
        file_path: 文件路径
        
    Returns:
        Optional[str]: MIME类型，如果不支持则返回None
    """
    ext = get_file_extension(file_path)
    return IMAGE_EXTENSIONS.get(ext)


def delete_file_safely(file_path: str) -> bool:
    """安全删除文件
    
    Args:
        file_path: 要删除的文件路径
        
    Returns:
        bool: 删除是否成功
    """
    if not os.path.exists(file_path):
        return True
        
    try:
        os.remove(file_path)
        logger.debug(f"文件已删除: {file_path}")
        return True
    except Exception as e:
        logger.warning(f"删除文件失败 '{file_path}': {str(e)}")
        return False


def write_text_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
    """写入文本文件
    
    Args:
        file_path: 文件路径
        content: 要写入的内容
        encoding: 字符编码
        
    Returns:
        bool: 写入是否成功
    """
    try:
        # 确保目录存在
        ensure_directory(os.path.dirname(os.path.abspath(file_path)))
        
        # 写入文件
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        logger.debug(f"文本文件已写入: {file_path}")
        return True
    except Exception as e:
        logger.error(f"写入文本文件失败 '{file_path}': {str(e)}")
        return False


def read_text_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
    """读取文本文件
    
    Args:
        file_path: 文件路径
        encoding: 字符编码
        
    Returns:
        Optional[str]: 文件内容，如果读取失败则返回None
    """
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return None
        
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error(f"读取文本文件失败 '{file_path}': {str(e)}")
        return None


def get_absolute_path(relative_path: str) -> str:
    """获取绝对路径
    
    Args:
        relative_path: 相对路径
        
    Returns:
        str: 绝对路径
    """
    return os.path.abspath(relative_path)


def get_file_size(file_path: str) -> Optional[int]:
    """获取文件大小（字节）
    
    Args:
        file_path: 文件路径
        
    Returns:
        Optional[int]: 文件大小，如果文件不存在则返回None
    """
    if not os.path.exists(file_path):
        return None
        
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        logger.error(f"获取文件大小失败 '{file_path}': {str(e)}")
        return None


def is_file_readable(file_path: str) -> bool:
    """检查文件是否可读
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 文件是否可读
    """
    return os.path.exists(file_path) and os.access(file_path, os.R_OK)


def is_file_writable(file_path: str) -> bool:
    """检查文件是否可写
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 文件是否可写
    """
    # 如果文件不存在，检查目录是否可写
    if not os.path.exists(file_path):
        directory = os.path.dirname(os.path.abspath(file_path))
        return os.path.exists(directory) and os.access(directory, os.W_OK)
    
    # 如果文件存在，检查文件是否可写
    return os.access(file_path, os.W_OK)