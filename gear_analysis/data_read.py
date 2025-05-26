import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

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

def process_flankenlinie_data(lines, start_line, end_line):
    """
    处理Flankenlinie数据
    Args:
        lines: 文件的所有行
        start_line: Flankenlinie数据开始行
        end_line: Flankenlinie数据结束行
    Returns:
        flank_data: 处理后的Flankenlinie数据列表
    """
    flank_data = []
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
                flank_data.append({
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
        flank_data.append({
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
    
    return flank_data

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
        'flank_data': {},
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
    flank_start = None
    flank_end = None
    for i, line in enumerate(lines):
        if 'Flankenlinie:' in line:
            flank_start = i + 1
            print(f"Flankenlinie 开始行: {flank_start}")
        if 'Profil:' in line:
            flank_end = i
            print(f"Flankenlinie 结束行: {flank_end}")
            break
            
    if flank_start and flank_end:
        data_dict['flank_data'] = process_flankenlinie_data(lines, flank_start, flank_end)

    return data_dict

def plot_flank_data(data_dict):
    """
    绘制齿轮侧面数据图
    Args:
        data_dict: 包含数据的字典
    """
    plt.figure(figsize=(15, 10))
    
    # 创建两个子图
    plt.subplot(2, 1, 1)
    plt.title('齿轮侧面数据 - 有效测量点')
    
    for tooth_data in data_dict['flank_data']:
        info = tooth_data['tooth_info']
        data = tooth_data['measurements']
        valid = tooth_data['valid_points']
        valid_data = data[valid]
        label = f"齿号 {info['number']} {info['side']} (d={info['diameter']}mm)"
        plt.plot(valid_data, label=label)
    
    plt.xlabel('测量点')
    plt.ylabel('侧面值')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    
    # 添加统计信息子图
    plt.subplot(2, 1, 2)
    plt.title('齿轮侧面统计数据')
    
    tooth_nums = []
    means = []
    stds = []
    
    for tooth_data in data_dict['flank_data']:
        info = tooth_data['tooth_info']
        stats = tooth_data['statistics']
        tooth_nums.append(f"{info['number']}{info['side']}")
        means.append(stats['mean'])
        stds.append(stats['std'])
    
    x = range(len(tooth_nums))
    plt.bar(x, means, yerr=stds, capsize=5, label='平均值±标准差')
    plt.xticks(x, tooth_nums, rotation=45)
    plt.xlabel('齿号')
    plt.ylabel('测量值')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('gear_flank.png', bbox_inches='tight', dpi=300)
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
    
    # 打印Flankenlinie数据信息
    print("\nFlankenlinie数据统计:")
    for tooth_data in data['flank_data']:
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
    
    # 绘制侧面数据
    plot_flank_data(data)
    print("\n已生成侧面数据图表: gear_flank.png")

if __name__ == "__main__":
    main()
