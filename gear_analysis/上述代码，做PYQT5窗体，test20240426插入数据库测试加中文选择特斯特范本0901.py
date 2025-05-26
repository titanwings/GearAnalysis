import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QMdiSubWindow, QComboBox, QLabel, QLineEdit, QPushButton, QHBoxLayout, QWidget
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import tkinter as tk
import tkinter.filedialog
from matplotlib.figure import Figure
import re
from scipy.optimize import curve_fit
import sqlite3
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties


root = tk.Tk()
root.withdraw()
global file_path
# 打开文件选择对话框，获取选中的文件名
file_path = tk.filedialog.askopenfilename()
# 打开文件并读取内容
#with open(file_path, 'r', encoding='ANSI') as f:
 #   content = f.read()
# 打开文件以写入模式并保存修改后的内容
#with open(file_path, 'w', encoding='utf-8') as f:
 #     f.write(content)
# 打开文件并读取内容
with open(file_path, 'r', encoding='utf-8',errors='replace') as f:

     # with open('your_file.txt', encoding='utf-8', errors='replace') as file:
       for line in f:
         cleaned_line = line.replace('\ufffd', '?')  # 将替代字符替换为问号或您想要的任何字符
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
    # 使用正则表达式找到所有中文字符并将其替换为"zw"
result = re.sub(r'[\u4e00-\u9fa5]+', 'zw', content)

# 使用正则表达式找到所有中文字符并将其替换为"zw"

# 打开文件以写入模式并保存修改后的内容
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(result)


# 匹配数字-2147483.648的正则表达式模式
pattern = r'-2147483\.648'

# 将匹配到的数字-2147483.648替换为50
replacement = '-21.522'

# 使用 re.sub() 函数进行替换
result = re.sub(pattern, replacement, content)
# 打开文件以写入模式并保存修改后的内容
with open(file_path, 'w', encoding='utf-8') as f:
       f.write(result)
# 打开文件并读取内容

# 关闭应用程序窗口
root.destroy()




with open(file_path, 'r') as file:
    content = file.readlines()
class TeethAnalyzerApp(QMainWindow):
        # 省略其他代码

    def __init__(self):
            super().__init__()
            # 使用 f-string 将文件路径添加到标题中
            self.setWindowTitle(f'Teeth Analyzer App - {file_path}')

            #self.setWindowTitle('Teeth Analyzer App'&file_path)
            self.setGeometry(100, 100, 1920, 1080)
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)

            self.layout = QHBoxLayout()
            self.combo_box = QComboBox()
            # 打开文本文件进行读取
            with open(file_path, "r") as file:
                # 逐行读取文件内容
                for line in file:
                    # 在每一行中查找包含 "Zahu-Nr" 的字段
                    if "Zahn-Nr.:" in line:
                        global extracted_text
                        # 找到字段后，获取后面四十位字符串并去除空格
                        # 从 "Zahn-Nr" 字段的位置之前开始提取整行
                        # extracted_text = line[:line.find("Zahn-Nr")].strip()
                        zahn_nr_index = line.find("Zahn-Nr.:")
                        if zahn_nr_index != -1:  # 如果找到了 "Zahn-Nr" 字段
                            extracted_text = line[zahn_nr_index:].strip()
                        # extracted_text = line[line.find("Zahn-Nr") + len("Zahn-Nr"):].strip()
                        # 将提取的字符串添加到下拉框中
                        # Com_box.addItem(extracted_text)

                        # 左侧控件
                        input_string = extracted_text
                        new_string = re.sub(r"\s", "", input_string)
                        # 定义正则表达式模式来匹配齿数、齿面、齿向高度和齿形直径
                        pattern_z = r"Zahn-Nr.:(\d+)(links|rechts)\/\d+Wertez=(\d+)"
                        pattern_d = r"Zahn-Nr.:(\d+)(links|rechts)\/\d+Werted=(\d+\.\d+)"

                        # 使用正则表达式进行匹配
                        match_z = re.search(pattern_z, new_string)
                        match_d = re.search(pattern_d, new_string)

                        if match_z:
                            zahn_nr = match_z.group(1)  # 匹配到的齿数
                            zahnseite = "左齿面" if match_z.group(2) == "links" else "右齿面"  # 根据匹配到的内容确定左右齿面
                            zahn_height = match_z.group(3)  # 匹配到的齿向高度

                            print("齿数: ", zahn_nr)
                            print("齿面: ", zahnseite)
                            print("齿向高度: ", zahn_height)
                            comboxselect = "齿数" + zahn_nr + " 齿面" + zahnseite + " 齿向高度" + zahn_height
                            print(comboxselect)
                        elif match_d:
                            zahn_nr = match_d.group(1)  # 匹配到的齿数
                            zahnseite = "左齿面" if match_d.group(2) == "links" else "右齿面"  # 根据匹配到的内容确定左右齿面
                            zahn_diameter = match_d.group(3)  # 匹配到的齿形直径

                            print("齿数: ", zahn_nr)
                            print("齿面: ", zahnseite)
                            print("齿形直径: ", zahn_diameter)
                            comboxselect = "齿数" + zahn_nr + " 齿面" + zahnseite + " 齿形直径" + zahn_diameter
                            print(comboxselect)
                        else:
                            print("未找到匹配的信息")
                            global option_data_mapping
                        option_data_mapping = {comboxselect: [extracted_text]

                                               }

                        # print("option_data_mapping",extracted_text())
                        self.combo_box.addItem(comboxselect)
                        word = input_string  # 请将此替换为你要查找的单词
                        index = next(i for i, line in enumerate(content) if word in line)
                        actual_teeth_x = np.arange(0, 480)
                        actual_teeth_x = [list(map(float, line.split())) for line in content[index + 1: index + 41]]
                        actual_teeth_y = np.array(actual_teeth_x).flatten()


                        actual_teeth_x = np.arange(0, 480)
                        standard_teeth_x = np.arange(0, 480)
                        standard_teeth_y = np.zeros(480)
                        import sqlite3

                        # 连接到数据库
                        with sqlite3.connect('curve_data.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute('''CREATE TABLE IF NOT EXISTS DataPoint (
                                                id INTEGER PRIMARY KEY,
                                                curve_idno TEXT,
                                         y_value REAL
                                            )''')

                            # 生成插入数据的 SQL 语句
                            data = []
                            i=1
                            for i in range(480):
                                curve_idno =comboxselect
                                curve_id = input_string
                                x_value = i
                               #x_value = actual_teeth_x[i]  # 根据索引获取 x_value
                                y_value = actual_teeth_y[i]  # 根据索引获取 y_value
                                i=i+1
                                data.append((curve_idno, curve_id, x_value, y_value))
                           # for i in range(480):
                            #curve_idno = comboxselect
                            #curve_id = input_string
                            #x_value = np.arange(1, 481)  # 根据索引获取 x_value
                            #y_value = actual_teeth_y  # 根据索引获取 y_value
                            #for x_value, y_value in zip(actual_teeth_x, actual_teeth_y):
                             #   data.append((curve_idno, curve_id, x_value, y_value))

                            # 生成插入数据的 SQL 语句
                            insert_sql = "INSERT INTO DataPoint (curve_idno, curve_id, x_value, y_value) VALUES (?, ?, ?, ?);"

                            # 执行批量插入操作
                            cursor.executemany(insert_sql, data)

                            # 提交更改并关闭连接
                            conn.commit()


                            #try:
                                # 检查 DataPoint 表是否存在，如果不存在则创建
                               # cursor.execute(
                                #    "CREATE TABLE IF NOT EXISTS DataPoint (point_id INTEGER PRIMARY KEY, curve_idno INTEGER, curve_id INTEGER, x_value REAL, y_value REAL, FOREIGN KEY (curve_id) REFERENCES Curve(curve_id));")

                                # 插入数据点
                             #   data_points = [(input_string, word, float(x), float(y)) for x, y in
                              #                 zip(actual_teeth_x, actual_teeth_y)]
                               # cursor.executemany(
                                #    "INSERT INTO DataPoint (curve_idno，curve_id, x_value, y_value) VALUES (?, ?, ?, ?)",
                                 #   data_points)

                                #conn.commit()
                                #print("数据插入成功！")

                            #except sqlite3.Error as e:
                             #   print(f"发生错误：{e}")
                        conn.close()
                        # input_string = "Zahn-Nr.: 20 rechts / 480 Werte d= 155.61"

            #self.label2 = QLabel("Enter another value:")
            self.layout.addWidget(self.combo_box)

            self.textbox1 = QLineEdit()
            self.layout.addWidget(self.textbox1)

            #self.layout.addWidget(self.label2)
            self.textbox2 = QLineEdit()
            self.layout.addWidget(self.textbox2)

            self.process_button = QPushButton("Process Data")
            self.process_button.clicked.connect(self.process_data)
            self.layout.addWidget(self.process_button)
            self.mdi = QMdiArea()  # 定义 mdi 属性
            # 右侧 Mdi 子窗口
            self.mdi = QMdiArea(self)
            self.layout.addWidget(self.mdi)

            self.central_widget.setLayout(self.layout)
    def process_data(self):

           #selected_item = self.combo_box.get()  # 获取ComboBox中选择的文本
           #query_data(selected_item)

#def query_data(selected_item):
          #print(selected_item )
          global x_values, y_values, word, word1, actual_teeth_x, actual_teeth_y, standard_teeth_y, fit, fit_x, fit_y, distance, start_x_range, end_x_range, total_max_distance, b_fit, Ff, standard_teeth_x

         # self.label2.setText(self.combo_box.currentText())  # 请将此替换为你要查找的单词

            # 连接到数据库


        # 指定要查询的curve_idno

          curve_idno = self.combo_box.currentText().strip()
          #self.label2.setText(curve_idno)

          conn = sqlite3.connect('curve_data.db')
          cursor = conn.cursor()
     # 查询数据库获取指定curve_idno的480个点的数据
          #cursor.execute("SELECT x_value, y_value FROM DataPoint WHERE curve_idno=? LIMIT 480", (curve_idno,))
          #results = cursor.fetchall()
          try:
              # 执行查询语句

              cursor.execute("SELECT x_value, y_value FROM DataPoint WHERE curve_idno=? LIMIT 480", (curve_idno,))
              results = cursor.fetchall()
          except sqlite3.Error as e:
              print(f"Error executing query: {e}")
              # 在这里添加其他错误处理,例如弹出错误提示框
              return

          # 关闭连接
          conn.close()

            # 从查询结果中提取x和y值
          x_values = []
          y_values = []
          for result in results:
            x_values.append(result[0])
            y_values.append(result[1])
          actual_teeth_x = x_values
          actual_teeth_y = y_values
          standard_teeth_x = np.arange(0, 480)
          standard_teeth_y = np.zeros(480)
          actual_teeth_x = np.array(x_values)  # 将列表转换为NumPy数组
          actual_teeth_y = np.array(y_values)  # 将列表转换为NumPy数组

            # 继续进行其他的计算和操作

          fit = np.polyfit(actual_teeth_x, actual_teeth_y, 1)
          a, b = fit

          fit_x = actual_teeth_x
          fit_y = a * fit_x + b
          distances = np.abs(a * actual_teeth_x - actual_teeth_y + b) / np.sqrt(a ** 2 + 1)
          start_x_range = 50
          end_x_range = 400
          evaluation_range = (actual_teeth_x >= start_x_range) & (actual_teeth_x <= end_x_range)

          indices_above_zero = np.where(actual_teeth_y[evaluation_range] - fit_y[evaluation_range] > 0)[0]
          indices_below_zero = np.where(actual_teeth_y[evaluation_range] - fit_y[evaluation_range] < 0)[0]

          distances_above_zero = np.abs(actual_teeth_y[evaluation_range][indices_above_zero] - (
                    a * actual_teeth_x[evaluation_range][indices_above_zero] + b)) / np.sqrt(a ** 2 + 1)
          distances_below_zero = np.abs(actual_teeth_y[evaluation_range][indices_below_zero] - (
                    a * actual_teeth_x[evaluation_range][indices_below_zero] + b)) / np.sqrt(a ** 2 + 1)

          max_distance_above_zero = np.max(distances_above_zero)
          max_distance_below_zero = np.max(distances_below_zero)

          total_max_distance = max_distance_above_zero + max_distance_below_zero

          x1 = actual_teeth_x[evaluation_range][indices_above_zero]
          y1 = actual_teeth_y[evaluation_range][indices_above_zero]
          standard_y1 = standard_teeth_y[evaluation_range][indices_above_zero]
          distance1 = np.abs(y1 - standard_y1)

          x2 = actual_teeth_x[evaluation_range][indices_below_zero]
          y2 = actual_teeth_y[evaluation_range][indices_below_zero]
          standard_y2 = standard_teeth_y[evaluation_range][indices_below_zero]
          distance2 = np.abs(y2 - standard_y2)

          Ff = np.max(distance1) + np.max(distance2)
          print("拟合直线的斜率为:", Ff)

          self.plot_graph()

          pass

    def plot_graph(self):
            selected_item = self.combo_box.currentText()
            font_path = 'simhei.ttf'  # 替换为您的字体文件路径
            font_prop = FontProperties(fname=font_path)
            sub_window = QMdiSubWindow()
            sub_window.setWindowTitle(selected_item)
            sub_window.setGeometry(0, 0, 600, 600)

            fig = Figure()

            ax = fig.add_subplot(2, 1, 1, label="points")
            # 绘制实际齿形线、标准齿形线和拟合线
           # ax.axis["right"].set_visible(False)
            #ax.axis["top"].set_visible(False)
            ax.set_title('Profile', fontsize=16, fontstyle='italic')
            ax.set_title('left flank', fontsize=16, fontstyle='italic', loc='left')
            ax.set_title('right flank', fontsize=16, fontstyle='italic', loc='right')
            fig.text(0.05, 0.95, selected_item, fontsize=16, fontstyle='italic', color='blue', fontproperties=font_prop)
            ax.plot(actual_teeth_y, actual_teeth_x,'r-', label='Actual Teeth', linewidth=1.5)  # 去掉点的标记样式
            #ax.plot(actual_teeth_y, actual_teeth_x,  'bo-', label='Actual Teeth',linewidth=1)
            ax.plot(standard_teeth_y, standard_teeth_x, 'b--', label='Standard Teeth', linewidth=1)
            ax.plot(fit_y, fit_x, 'g-', label='Fitted Line', linewidth=1)

            # 显示总误差
            ax.text(0.5, 10, f"ffa: {total_max_distance:.2f}", fontsize=12, ha='center', va='center')

            # 添加箭头注释
            ax.annotate('Fitted line start', (fit_x[0], fit_y[0]), xytext=(fit_x[0] + 1, fit_y[0] + 1),
                        arrowprops=dict(facecolor='black', shrink=0.05))

            ax1 = fig.add_subplot(2, 1, 2, label="points")
            # 绘制实际齿形线、标准齿形线和拟合线
            ax1.set_title('Lead', fontsize=16, fontstyle='italic')
            ax1.set_title('left flank', fontsize=16, fontstyle='italic', loc='left')
            ax1.set_title('right flank', fontsize=16, fontstyle='italic', loc='right')
            ax1.plot(actual_teeth_y, actual_teeth_x, 'r-', label='Actual Teeth', linewidth=1.5)  # 去掉点的标记样式
            # ax.plot(actual_teeth_y, actual_teeth_x,  'bo-', label='Actual Teeth',linewidth=1)
            ax1.plot(standard_teeth_y, standard_teeth_x, 'b--', label='Standard Teeth', linewidth=1)
            ax1.plot(fit_y, fit_x, 'g-', label='Fitted Line', linewidth=1)

            # 显示总误差
            ax1.text(0.5, 10, f"ffa: {total_max_distance:.2f}", fontsize=12, ha='center', va='center')

            # 添加箭头注释
            ax1.annotate('Fitted line start', (fit_x[0], fit_y[0]), xytext=(fit_x[0] + 1, fit_y[0] + 1),
                         arrowprops=dict(facecolor='black', shrink=0.05))

            # 添加表格
            #table_data = [['ffa', 'fHa', 'Ff'],
                         # [f'{total_max_distance:.2f}', f'{b_fit:.2f}', f'{Ff:.2f}']]

            #table = ax1.table(cellText=table_data, loc='bottom', cellLoc='center')

            # 调整子图之间的间距
            fig.subplots_adjust(left=0.1, right=0.9, top=0.8, bottom=0.2)
            # 创建图表

            plt.grid(True)  # 启用主要网格线

            # 设置主要刻度的间隔
            plt.gca().xaxis.set_major_locator(plt.MultipleLocator(1))
            plt.gca().yaxis.set_major_locator(plt.MultipleLocator(10))

            # 设置次要刻度的间隔
            plt.gca().xaxis.set_minor_locator(plt.MultipleLocator(0.2))
            plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(1))

            # 设置Y轴比例
            ax.set_aspect(1, adjustable='datalim')  # 调整Y轴的比例，这里设置为0.5
            ax.tick_params(axis='y', direction='inout')  # 设置Y轴刻度标识在两侧
            ax.tick_params(axis='both', which='major', labelsize=9, labelcolor='black')
            ax.legend(loc='center right')
            ax.set_axisbelow(True)
            ax.grid(which='both', color='gray', linestyle=':', linewidth=0.5)

            ax.annotate('100', xy=(0, 100), xytext=(3, 100),
                        arrowprops=dict(facecolor='red', shrink=0.05))
            ax.annotate('300', xy=(0, 300), xytext=(3, 300),
                        arrowprops=dict(facecolor='green', shrink=0.05))

            ax1.set_aspect(1, adjustable='datalim')  # 调整Y轴的比例，这里设置为0.5
            ax1.tick_params(axis='y', direction='inout')  # 设置Y轴刻度标识在两侧
            ax1.tick_params(axis='both', which='major', labelsize=9, labelcolor='black')
            ax1.legend(loc='center right')
            ax1.set_axisbelow(True)
            ax1.grid(which='both', color='gray', linestyle=':', linewidth=0.5)

            ax1.annotate('100', xy=(0, 100), xytext=(3, 100),
                         arrowprops=dict(facecolor='red', shrink=0.05))
            ax1.annotate('300', xy=(0, 300), xytext=(3, 300),
                         arrowprops=dict(facecolor='green', shrink=0.05))

            canvas = FigureCanvas(fig)
            sub_window.setWidget(canvas)
            self.mdi.addSubWindow(sub_window)

            sub_window.showMaximized()
             #sub_window.showNormal()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    analyzer_app = TeethAnalyzerApp()
    analyzer_app.show()
    sys.exit(app.exec_())
