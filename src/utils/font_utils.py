#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.font_manager as fm
import os
import json
import logging
from typing import List, Tuple, Optional

# 获取logger实例
logger = logging.getLogger(__name__)

# 字体缓存文件路径
FONT_CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'cache', 'font_cache.json')

# 优先中文字体列表
PREFERRED_FONTS = [
    'WenQuanYi Micro Hei',
    'WenQuanYi Zen Hei', 
    'Heiti TC',
    'SimHei',
    'Microsoft YaHei',
    'Arial Unicode MS',
    'SimSun',
    'NSimSun'
]


def _ensure_cache_dir():
    """确保缓存目录存在"""
    cache_dir = os.path.dirname(FONT_CACHE_FILE)
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)


def _load_font_cache() -> Optional[dict]:
    """从缓存文件加载字体信息"""
    if not os.path.exists(FONT_CACHE_FILE):
        return None
    
    try:
        with open(FONT_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"加载字体缓存失败: {str(e)}")
        return None


def _save_font_cache(cache_data: dict) -> None:
    """保存字体信息到缓存文件"""
    try:
        _ensure_cache_dir()
        with open(FONT_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"保存字体缓存失败: {str(e)}")


def find_system_fonts() -> List[Tuple[str, str]]:
    """查找系统中可用的所有字体
    
    Returns:
        List[Tuple[str, str]]: 字体名称和字体路径的列表
    """
    # 先尝试从缓存中加载
    cache = _load_font_cache()
    if cache:
        logger.info("从缓存加载字体信息")
        return [(font['name'], font['path']) for font in cache['fonts']]
    
    # 如果缓存不存在或已过期，重新扫描
    logger.info("扫描系统字体...")
    fonts = []
    try:
        for font_path in fm.findSystemFonts():
            try:
                font_name = fm.FontProperties(fname=font_path).get_name()
                fonts.append((font_name, font_path))
            except Exception as e:
                # 忽略单个字体加载失败的情况
                continue
        
        # 保存到缓存
        cache_data = {
            'timestamp': os.path.getmtime(__file__),  # 使用当前文件的修改时间作为缓存时间戳
            'fonts': [{'name': name, 'path': path} for name, path in fonts]
        }
        _save_font_cache(cache_data)
        
        logger.info(f"发现 {len(fonts)} 种系统字体")
        return fonts
    except Exception as e:
        logger.error(f"扫描系统字体失败: {str(e)}")
        return []


def find_chinese_fonts() -> List[Tuple[str, str]]:
    """查找系统中可用的中文字体
    
    Returns:
        List[Tuple[str, str]]: 中文字体名称和字体路径的列表
    """
    all_fonts = find_system_fonts()
    chinese_fonts = []
    
    # 中文字体关键词
    chinese_keywords = ['wqy', 'uming', 'hei', 'song', 'yahei', '微软', '黑体', '宋体', '楷体']
    
    for font_name, font_path in all_fonts:
        font_filename = os.path.basename(font_path).lower()
        if any(keyword in font_filename for keyword in chinese_keywords) or \
           any(char > '\u4e00' and char < '\u9fff' for char in font_name):
            chinese_fonts.append((font_name, font_path))
    
    # 按首选字体列表排序
    def font_priority(font_tuple):
        font_name = font_tuple[0]
        for i, pref_font in enumerate(PREFERRED_FONTS):
            if pref_font in font_name:
                return i
        return len(PREFERRED_FONTS)
    
    chinese_fonts.sort(key=font_priority)
    logger.info(f"发现 {len(chinese_fonts)} 种中文字体")
    return chinese_fonts


def get_preferred_chinese_font() -> Optional[Tuple[str, str]]:
    """获取首选的中文字体
    
    Returns:
        Optional[Tuple[str, str]]: 首选字体名称和路径，如果没有找到则返回None
    """
    chinese_fonts = find_chinese_fonts()
    if not chinese_fonts:
        logger.warning("未找到中文字体")
        return None
    
    # 返回排序后的第一个字体（优先级最高）
    return chinese_fonts[0]


def set_matplotlib_fonts():
    """设置matplotlib使用中文字体"""
    # 首先尝试获取首选中文字体
    preferred_font = get_preferred_chinese_font()
    
    if preferred_font:
        font_name, font_path = preferred_font
        try:
            # 设置matplotlib字体
            import matplotlib.pyplot as plt
            plt.rcParams["font.family"] = [font_name]
            plt.rcParams["font.sans-serif"] = [font_name]
            plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题
            logger.info(f"已设置matplotlib字体为: {font_name} ({font_path})")
            return True
        except Exception as e:
            logger.error(f"设置matplotlib字体失败: {str(e)}")
    
    # 如果首选字体设置失败，使用通用字体设置
    logger.info("使用默认中文字体配置")
    try:
        import matplotlib.pyplot as plt
        plt.rcParams["font.family"] = PREFERRED_FONTS
        plt.rcParams["font.sans-serif"] = PREFERRED_FONTS
        plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题
        return True
    except Exception as e:
        logger.error(f"设置默认matplotlib字体失败: {str(e)}")
        return False


def clear_font_cache():
    """清除字体缓存"""
    if os.path.exists(FONT_CACHE_FILE):
        try:
            os.remove(FONT_CACHE_FILE)
            logger.info("字体缓存已清除")
            return True
        except Exception as e:
            logger.error(f"清除字体缓存失败: {str(e)}")
            return False
    return True


def setup_fonts():
    """设置中文字体（兼容旧接口）"""
    return set_matplotlib_fonts()