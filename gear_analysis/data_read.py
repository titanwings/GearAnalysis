import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import logging
import json
import matplotlib as mpl

# 配置logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gear_analysis.log')
    ]
)

logger = logging.getLogger(__name__)

# 配置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # macOS的中文字体
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

def parse_header_line(line):
    """
    解析头部信息行
    Args:
        line: 单行文本
    Returns:
        key: 键
        value: 值
    """
    # 去除注释部分
    if '!' in line:
        line = line.split('!')[0]
    
    # 分割主要部分
    parts = line.strip().split()
    if len(parts) < 2:
        return None, None
    
    key = parts[0]
    # 将第一个部分之后的所有内容作为值
    value = ' '.join(parts[1:])
    return key, value

def parse_tooth_header(line):
    """
    解析齿号信息行
    Args:
        line: 包含齿号信息的行
    Returns:
        tooth_info: 包含齿号、方向、测量点数和直径的字典
    """
    tooth_info = {
        'number': None,
        'side': None,
        'points_count': None,
        'diameter': None
    }
    
    if 'Zahn-Nr.:' not in line:
        return None
        
    parts = line.split('/')
    # 处理第一部分（齿号和方向）
    first_part = parts[0].split(':')[1].strip()
    number_side = first_part.split()
    tooth_info['number'] = int(number_side[0])
    tooth_info['side'] = number_side[1] if len(number_side) > 1 else None
    
    # 处理第二部分（测量点数）
    if len(parts) > 1:
        points = parts[1].strip().split()[0]
        tooth_info['points_count'] = int(points)
        
        # 处理直径信息 - 在第二部分中查找
        if 'd=' in parts[1]:
            try:
                # 提取d=后面的数字
                d_str = parts[1][parts[1].find('d=') + 2:].strip()
                d_value = d_str.split()[0]  # 获取第一个数字
                tooth_info['diameter'] = float(d_value)
            except (ValueError, IndexError):
                print(f"警告：无法解析直径信息：{parts[1]}")
    
    return tooth_info

def process_gear_height_data(lines, start_line, end_line):
    """
    处理gear_height数据
    Args:
        lines: 文件的所有行
        start_line: gear_height开始行
        end_line: gear_height数据结束行
    Returns:
        gear_height_data: 处理后的gear_height的list
    """
    gear_height_data = []
    current_tooth = None
    current_data = []

    logger.debug(f"gear_height_start_line: {start_line}")
    logger.debug(f"gear_height_end_line: {end_line}")
    
    for line in lines[start_line:end_line]:
        print(line)
        if 'Zahn-Nr.:' in line:
            # 保存前一个齿的数据
            if current_tooth is not None and current_data:
                tooth_info = {
                    'number': current_tooth['number'],
                    'side': current_tooth['side'],
                    'points_count': len(current_data),
                    'height': current_tooth['height']
                }
                # 输出齿号信息
                print(f"齿号信息: {tooth_info}")
                gear_height_data.append({
                    'tooth_info': tooth_info,
                    'measurements': np.array(current_data),
                    'valid_points': np.array([x != -21.522 for x in current_data]),
                    'statistics': {
                        'max_value': np.max([x for x in current_data if x != -21.522]),
                        'min_value': np.min([x for x in current_data if x != -21.522]),
                        'mean': np.mean([x for x in current_data if x != -21.522]),
                        'std': np.std([x for x in current_data if x != -21.522])
                    }
                })
            # 解析新的齿号信息
            parts = line.split('/')
            tooth_num = parts[0].split(':')[1].strip().split()[0]
            side = parts[0].split(':')[1].strip().split()[1]
            points_count = int(parts[1].strip().split()[0])
            height = float(parts[1].strip().split('z=')[1].strip())
            current_tooth = {
                'number': int(tooth_num),
                'side': side,
                'points_count': points_count,
                'height': height
            }
            current_data = []
        elif line.strip() and not line.startswith('Zahn-Nr.:'):
            # 处理数据行
            print(f"line: {line}")
            values = [float(x) for x in line.split() if x.strip()]
            if values:
                current_data.extend(values)
        # 输出当前齿号信息和数据
        print(f"current_tooth: {current_tooth}")
        print(f"current_data: {current_data}")
        print(f"current_data_length: {len(current_data)}")
    
    # 保存最后一个齿的数据
    if current_tooth is not None and current_data:
        tooth_info = {
            'number': current_tooth['number'],
            'side': current_tooth['side'],
            'points_count': len(current_data),
            'height': current_tooth['height']
        }
        gear_height_data.append({
            'tooth_info': tooth_info,
            'measurements': np.array(current_data),
            'valid_points': np.array([x != -21.522 for x in current_data]),
            'statistics': {
                'max_value': np.max([x for x in current_data if x != -21.522]),
                'min_value': np.min([x for x in current_data if x != -21.522]),
                'mean': np.mean([x for x in current_data if x != -21.522]),
                'std': np.std([x for x in current_data if x != -21.522])
            }
        })
    
    return gear_height_data


def process_gear_diameter_data(lines, start_line, end_line):
    """
    处理gear_diameter数据
    Args:
        lines: 文件的所有行
        start_line: gear_diameter开始行
        end_line: gear_diameter数据结束行
    Returns:
        gear_diameter_data: 处理后的gear_diameter的list
    """
    gear_diameter_data = []
    current_tooth = None
    current_data = []
    
    for line in lines[start_line:end_line]:
        # print(line)
        if 'Zahn-Nr.:' in line:
            # 保存前一个齿的数据
            if current_tooth is not None and current_data:
                tooth_info = {
                    'number': current_tooth['number'],
                    'side': current_tooth['side'],
                    'points_count': len(current_data),
                    'diameter': current_tooth['diameter']
                }
                # 输出齿号信息
                print(f"齿号信息: {tooth_info}")
                gear_diameter_data.append({
                    'tooth_info': tooth_info,
                    'measurements': np.array(current_data),
                    'valid_points': np.array([x != -21.522 for x in current_data]),
                    'statistics': {
                        'max_value': np.max([x for x in current_data if x != -21.522]),
                        'min_value': np.min([x for x in current_data if x != -21.522]),
                        'mean': np.mean([x for x in current_data if x != -21.522]),
                        'std': np.std([x for x in current_data if x != -21.522])
                    }
                })
            # 解析新的齿号信息
            parts = line.split('/')
            tooth_num = parts[0].split(':')[1].strip().split()[0]
            side = parts[0].split(':')[1].strip().split()[1]
            points_count = int(parts[1].strip().split()[0])
            diameter = float(parts[1].strip().split('d=')[1].strip())
            current_tooth = {
                'number': int(tooth_num),
                'side': side,
                'points_count': points_count,
                'diameter': diameter
            }
            current_data = []
        elif line.strip() and not line.startswith('Zahn-Nr.:'):
            # 处理数据行
            values = [float(x) for x in line.split() if x.strip()]
            if values:
                current_data.extend(values)
        # 输出当前齿号信息和数据
        print(f"current_tooth: {current_tooth}")
        print(f"current_data: {current_data}")
        print(f"current_data_length: {len(current_data)}")
    
    # 保存最后一个齿的数据
    if current_tooth is not None and current_data:
        tooth_info = {
            'number': current_tooth['number'],
            'side': current_tooth['side'],
            'points_count': len(current_data),
            'diameter': current_tooth['diameter']
        }
        gear_diameter_data.append({
            'tooth_info': tooth_info,
            'measurements': np.array(current_data),
            'valid_points': np.array([x != -21.522 for x in current_data]),
            'statistics': {
                'max_value': np.max([x for x in current_data if x != -21.522]),
                'min_value': np.min([x for x in current_data if x != -21.522]),
                'mean': np.mean([x for x in current_data if x != -21.522]),
                'std': np.std([x for x in current_data if x != -21.522])
            }
        })
    
    return gear_diameter_data

def read_mka_file(file_path):
    """
    读取MKA文件
    Args:
        file_path: MKA文件路径
    Returns:
        data_dict: 包含所有数据的字典
    """
    data_dict = {
        'header': {},
        'gear_params': {},
        'gear_diameter_data': {},
        'gear_height_data': {},
        'profile_data': {}
    }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 读取文件头信息
    for line in lines[:10]:
        key, value = parse_header_line(line)
        if key and value:
            data_dict['header'][key] = value
    # 数据格式混乱 再议
    # # 读取齿轮参数
    # for line in lines[10:100]:
    #     if ':' in line:
    #         parts = line.split(':')
    #         if len(parts) >= 2:
    #             key = parts[0].strip()
    #             value = parts[1].strip()
    #             data_dict['gear_params'][key] = value

    # 预处理
    gear_diameter_start = None
    gear_diameter_end = None
    gear_height_start = None
    gear_height_end = None
    for i, line in enumerate(lines):
        # 检测齿轮直径数据段的起始位置
        if 'Flankenlinie:' in line:
            gear_diameter_start = i + 1
            logger.debug(f"齿轮直径数据段起始位置: 第{gear_diameter_start}行")
            
        # 检测齿轮直径数据段的结束位置
        if 'Profil:' in line:
            gear_diameter_end = i
            logger.debug(f"齿轮直径数据段结束位置: 第{gear_diameter_end}行")
            
        # 检测齿高数据段的起始位置
        # 使用预编译的正则表达式提高性能
        TOOTH_HEIGHT_START_PATTERN = re.compile(
            r'^Zahn-Nr\.: \d+\s+links\s*\/\s*480\s+Werte\s+z=\s*\d+$'
        )
        if TOOTH_HEIGHT_START_PATTERN.match(line):
            gear_height_start = i
            logger.debug(f"齿高数据段起始位置: 第{gear_height_start}行")
            
        # 检测齿高数据段的结束位置
        TOOTH_HEIGHT_END_PATTERN = re.compile(
            r'^Fuzwreisdurchmesser\s*\/\s*Hzwe\s*:\s*\d+\.\d+'
        )
        if TOOTH_HEIGHT_END_PATTERN.match(line):
            gear_height_end = i - 2  # 向上偏移2行作为实际结束位置
            logger.debug(f"齿高数据段结束位置: 第{gear_height_end}行")
            
        # 当所有必要的位置信息都已获取时退出循环
        if all([
            gear_diameter_start,
            gear_diameter_end,
            gear_height_start,
            gear_height_end
        ]):
            break

    data_dict['gear_diameter_data'] = process_gear_diameter_data(lines, gear_diameter_start, gear_diameter_end)
    data_dict['gear_height_data'] = process_gear_height_data(lines, gear_height_start, gear_height_end)

    return data_dict

def plot_gear_diameter_data(data_dict):
    """
    绘制齿轮侧面数据图
    Args:
        data_dict: 包含数据的字典
    """
    plt.figure(figsize=(15, 10))
    
    # 创建两个子图
    plt.subplot(2, 1, 1)
    plt.title('齿轮侧面数据 - 有效测量点', fontsize=12)
    
    for tooth_data in data_dict['gear_diameter_data']:
        info = tooth_data['tooth_info']
        data = np.array(tooth_data['measurements'])  # 确保是numpy数组
        valid = np.array(tooth_data['valid_points'])  # 确保是numpy数组
        valid_data = data[valid]
        label = f"齿号 {info['number']} {info['side']} (d={info['diameter']}mm)"
        plt.plot(valid_data, label=label)
    
    plt.xlabel('测量点', fontsize=10)
    plt.ylabel('侧面值', fontsize=10)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    plt.grid(True)
    
    # 添加统计信息子图
    plt.subplot(2, 1, 2)
    plt.title('齿轮侧面统计数据', fontsize=12)
    
    tooth_nums = []
    means = []
    stds = []
    
    for tooth_data in data_dict['gear_diameter_data']:
        info = tooth_data['tooth_info']
        stats = tooth_data['statistics']
        tooth_nums.append(f"{info['number']}{info['side']}")
        means.append(stats['mean'])
        stds.append(stats['std'])
    
    x = range(len(tooth_nums))
    plt.bar(x, means, yerr=stds, capsize=5, label='平均值±标准差')
    plt.xticks(x, tooth_nums, rotation=45, fontsize=8)
    plt.xlabel('齿号', fontsize=10)
    plt.ylabel('测量值', fontsize=10)
    plt.legend(fontsize=8)
    
    plt.tight_layout()
    plt.savefig('gear_flank.png', bbox_inches='tight', dpi=300)
    plt.close()

def plot_gear_height_data(data_dict):
    """
    绘制齿轮齿高数据图
    Args:
        data_dict: 包含数据的字典
    """
    plt.figure(figsize=(15, 15))  # 增加图表高度以容纳更多子图
    
    # 创建四个子图
    # 齿轮直径数据
    plt.subplot(4, 1, 1)
    plt.title('齿轮直径数据 - 有效测量点', fontsize=12)
    
    for tooth_data in data_dict['gear_diameter_data']:
        info = tooth_data['tooth_info']
        data = np.array(tooth_data['measurements'])
        valid = np.array(tooth_data['valid_points'])
        valid_data = data[valid]
        label = f"齿号 {info['number']} {info['side']} (d={info['diameter']}mm)"
        plt.plot(valid_data, label=label)
    
    plt.xlabel('测量点', fontsize=10)
    plt.ylabel('直径值', fontsize=10)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    plt.grid(True)
    
    # 齿轮直径统计数据
    plt.subplot(4, 1, 2)
    plt.title('齿轮直径统计数据', fontsize=12)
    
    tooth_nums = []
    means = []
    stds = []
    
    for tooth_data in data_dict['gear_diameter_data']:
        info = tooth_data['tooth_info']
        stats = tooth_data['statistics']
        tooth_nums.append(f"{info['number']}{info['side']}")
        means.append(stats['mean'])
        stds.append(stats['std'])
    
    x = range(len(tooth_nums))
    plt.bar(x, means, yerr=stds, capsize=5, label='平均值±标准差')
    plt.xticks(x, tooth_nums, rotation=45, fontsize=8)
    plt.xlabel('齿号', fontsize=10)
    plt.ylabel('直径值', fontsize=10)
    plt.legend(fontsize=8)
    
    # 齿高数据
    plt.subplot(4, 1, 3)
    plt.title('齿高数据 - 有效测量点', fontsize=12)
    
    for tooth_data in data_dict['gear_height_data']:
        info = tooth_data['tooth_info']
        data = np.array(tooth_data['measurements'])
        valid = np.array(tooth_data['valid_points'])
        valid_data = data[valid]
        label = f"齿号 {info['number']} {info['side']} (h={info['height']}mm)"
        plt.plot(valid_data, label=label)
    
    plt.xlabel('测量点', fontsize=10)
    plt.ylabel('齿高值', fontsize=10)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    plt.grid(True)
    
    # 齿高统计数据
    plt.subplot(4, 1, 4)
    plt.title('齿高统计数据', fontsize=12)
    
    tooth_nums = []
    means = []
    stds = []
    
    for tooth_data in data_dict['gear_height_data']:
        info = tooth_data['tooth_info']
        stats = tooth_data['statistics']
        tooth_nums.append(f"{info['number']}{info['side']}")
        means.append(stats['mean'])
        stds.append(stats['std'])
    
    x = range(len(tooth_nums))
    plt.bar(x, means, yerr=stds, capsize=5, label='平均值±标准差')
    plt.xticks(x, tooth_nums, rotation=45, fontsize=8)
    plt.xlabel('齿号', fontsize=10)
    plt.ylabel('齿高值', fontsize=10)
    plt.legend(fontsize=8)
    
    plt.tight_layout()
    plt.savefig('gear_analysis.png', bbox_inches='tight', dpi=300)
    plt.close()

def main():
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建MKA文件的完整路径
    file_path = os.path.join(current_dir, '202305021044 - 读取数据文件.mka')
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误：找不到文件 {file_path}")
        print("请确保MKA文件与脚本在同一目录下")
        return
    
    # 读取MKA文件
    data = read_mka_file(file_path)
    
    # 打印齿轮直径数据统计信息
    print("\n齿轮直径数据统计:")
    for tooth_data in data['gear_diameter_data']:
        info = tooth_data['tooth_info']
        stats = tooth_data['statistics']
        print(f"\n齿号 {info['number']} {info['side']}:")
        print(f"  测量直径: {info['diameter']}mm")
        print(f"  测量点数: {info['points_count']}")
        print(f"  有效点数: {np.sum(tooth_data['valid_points'])}")
        print(f"  最大值: {stats['max_value']:.3f}")
        print(f"  最小值: {stats['min_value']:.3f}")
        print(f"  平均值: {stats['mean']:.3f}")
        print(f"  标准差: {stats['std']:.3f}")
    
    # 打印齿高数据统计信息
    print("\n齿高数据统计:")
    for tooth_data in data['gear_height_data']:
        info = tooth_data['tooth_info']
        stats = tooth_data['statistics']
        print(f"\n齿号 {info['number']} {info['side']}:")
        print(f"  齿高: {info['height']}mm")
        print(f"  测量点数: {info['points_count']}")
        print(f"  有效点数: {np.sum(tooth_data['valid_points'])}")
        print(f"  最大值: {stats['max_value']:.3f}")
        print(f"  最小值: {stats['min_value']:.3f}")
        print(f"  平均值: {stats['mean']:.3f}")
        print(f"  标准差: {stats['std']:.3f}")
    
    # 绘制图形
    plot_gear_height_data(data)
    print("\n已生成齿轮分析图表: gear_analysis.png")
    
    # 最后再保存JSON数据
    json_file_path = os.path.join(current_dir, '02305021044.json')
    
    # 创建新的数据副本用于JSON序列化
    json_data = data.copy()
    for tooth_data in json_data['gear_diameter_data']:
        tooth_data['measurements'] = tooth_data['measurements'].tolist()
        tooth_data['valid_points'] = tooth_data['valid_points'].tolist()
        # 转换统计数据中的numpy数值
        for stat_key in tooth_data['statistics']:
            if isinstance(tooth_data['statistics'][stat_key], np.number):
                tooth_data['statistics'][stat_key] = float(tooth_data['statistics'][stat_key])
    
    # 处理齿高数据
    if 'gear_height_data' in json_data and json_data['gear_height_data']:
        for tooth_data in json_data['gear_height_data']:
            tooth_data['measurements'] = tooth_data['measurements'].tolist()
            tooth_data['valid_points'] = tooth_data['valid_points'].tolist()
            # 转换统计数据中的numpy数值
            for stat_key in tooth_data['statistics']:
                if isinstance(tooth_data['statistics'][stat_key], np.number):
                    tooth_data['statistics'][stat_key] = float(tooth_data['statistics'][stat_key])
    
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    
    print(f"\n数据已保存至: {json_file_path}")

if __name__ == "__main__":
    main()
