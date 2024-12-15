"""
    Written by Mrkinggg
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QGraphicsOpacityEffect
)
from PyQt5.QtGui import QPixmap, QGuiApplication, QIcon, QPalette, QColor, QPainter, QIntValidator
from PyQt5.QtCore import (
    Qt, QSize, pyqtSignal, QEvent, right, QPropertyAnimation, QRect, QParallelAnimationGroup,
    QEasingCurve, QAbstractAnimation
)
from qfluentwidgets import (
    BodyLabel, PushButton, ListWidget, ComboBox, SpinBox, LineEdit, CheckBox, ImageLabel, Slider, Flyout,
    FlyoutView, SearchLineEdit, ElevatedCardWidget, CardWidget, FlyoutViewBase, FlyoutAnimationType, PrimaryPushButton,
    SwitchButton
)
import os
import json
from pypinyin import lazy_pinyin


def load_items_from_json(file_name):
    # 从 JSON 文件加载内容并赋值给 items 变量
    # :param file_name: JSON 文件名
    # :return: 包含 JSON 数据的列表
    
    # 获取当前脚本的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 构建 JSON 文件路径
        json_file_path = os.path.join(current_dir, file_name)
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                items = json.load(f)
            return items
        except FileNotFoundError:
            print(f"错误：文件 '{file_name}' 未找到！")
            return []
        except json.JSONDecodeError:
            print(f"错误：文件 '{file_name}' 的 JSON 格式无效！")
            return []


class ItemWidget(ElevatedCardWidget):
    """单个商品显示小组件"""

    itemClicked = pyqtSignal(dict)
    buyClicked = pyqtSignal(dict)
    def __init__(self, item, parent=None):
        super().__init__(parent)
        self.item = item
        self.radius = 15  # 圆角半径
        self.background_color = QColor("#f0f0f0")  # 初始背景颜色

        # 设置布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # 商品图片
        pixmap = QPixmap(item["image"]).scaled(80, 80, Qt.KeepAspectRatio)
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        self.layout.addWidget(image_label, alignment=Qt.AlignCenter)

        # 商品名称
        name_label = QLabel(item["name"])
        name_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(name_label)

        # 商品价格
        price_layout = QHBoxLayout()
        price_pixmap = QPixmap("demo.png").scaled(20, 20, Qt.KeepAspectRatio)
        price_icon = QLabel()
        price_icon.setPixmap(price_pixmap)
        price_label = QLabel(item["price"])
        price_layout.addWidget(price_icon)
        price_layout.addWidget(price_label)
        price_layout.setAlignment(Qt.AlignCenter)
        self.layout.addLayout(price_layout)

        # 购买按钮
        buy_button = PushButton(QIcon("picture_src/shopping-cart.png"), "购买")
        buy_button.clicked.connect(self.on_buy_clicked)
        self.layout.addWidget(buy_button, alignment=Qt.AlignCenter)

        # 设置悬停显示描述
        self.setToolTip(item["describe"])

        # 绑定鼠标点击事件
        self.mousePressEvent = self.on_item_clicked

    def on_item_clicked(self, event):
        """点击商品组件时触发"""
        self.itemClicked.emit(self.item)

    def on_buy_clicked(self):
        """点击购买按钮时触发"""
        self.buyClicked.emit(self.item)


class SuccessBuyFlyoutView(FlyoutViewBase):

    def __init__(self, parent_widget, window_width, window_height, item, value, parent=None):
        super().__init__(parent)
        total_price = int(item['price']) * value  # 计算总价
        self.vBoxLayout = QVBoxLayout(self)
        self.label = BodyLabel(f"成功购买 {value} 件 {item['name']}！\n花费: {total_price} 元\n剩余金币: {parent_widget.balance} 元")
        self.button = PrimaryPushButton("关闭")

        self.button.setFixedWidth(140)

        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.setContentsMargins(20, 16, 20, 16)
        self.vBoxLayout.addWidget(self.label, alignment=Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.button, alignment=Qt.AlignCenter)
        # # 弹窗显示购买成功
        # success_message = QMessageBox(self)
        # success_message.setWindowTitle("购买成功")
        # success_message.setText(
        #     f"成功购买 {value} 件 {item['name']}！\n花费: {total_price} 元\n剩余金币: {self.balance} 元")
        # success_message.setIcon(QMessageBox.Information)
        # success_message.exec_()


class FailBuyFlyoutView(FlyoutViewBase):

    def __init__(self, parent_widget, window_width, window_height, item, value, parent=None):
        super().__init__(parent)
        total_price = int(item['price']) * value  # 计算总价
        self.vBoxLayout = QVBoxLayout(self)
        self.label = BodyLabel(
            f"金币不足！\n需要: {total_price} 元\n当前余额: {parent_widget.balance} 元")
        self.button = PrimaryPushButton("关闭")

        self.button.setFixedWidth(140)

        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.setContentsMargins(20, 16, 20, 16)
        self.vBoxLayout.addWidget(self.label, alignment=Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.button, alignment=Qt.AlignCenter)
        # failure_message = QMessageBox(self)
        # failure_message.setWindowTitle("购买失败")
        # failure_message.setText(f"金币不足！\n需要: {total_price} 元\n当前余额: {self.balance} 元")
        # failure_message.setIcon(QMessageBox.Warning)
        # failure_message.exec_()


class SSpinBox(SpinBox):
    """自定义SpinBox类，实现按下键数字增大，按上键数字减小"""
    def stepUp(self):
        """重写stepUp，增加数值"""
        self.setValue(self.value() - self.singleStep())  # 上按钮数值减少

    def stepDown(self):
        """重写stepDown，减少数值"""
        self.setValue(self.value() + self.singleStep())  # 下按钮数值增加


class ShoppingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("购物页面")

        # 获取屏幕的分辨率
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # 计算窗口宽度和高度
        self.window_width = int(screen_width * 2 / 5)
        self.window_height = int(screen_height * 1 / 2)

        self.setGeometry(100, 100, self.window_width, self.window_height)

        self.items = load_items_from_json("items_list.json")
        self.items_per_page = 6  # 每页显示的商品数量
        self.current_page = 1  # 当前页码
        self.current_category = "全部"  # 默认分类
        self.filtered_items = self.filter_items_by_category()  # 初始化商品列表
        self.total_pages = (len(self.items) + self.items_per_page - 1) // self.items_per_page
        self.user_data = load_items_from_json("user_data.json")
        self.balance = self.user_data["balance"]
        self.components = []

        self.initUI()
        self.details_widget = None  # 详情页面

    def initUI(self):
        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 右侧分类和排序
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(12, 24, 24, 24)
        self.category_list = ListWidget()
        self.category_list.setObjectName('list')
        self.category_list.addItems(["全部", "正餐", "零食", "饮料", "药品", "礼物", "道具"])
        self.category_list.setFixedWidth(self.width() // 4)
        self.category_list.setCurrentRow(0)  # 默认选择第一个“全部”
        self.category_list.currentTextChanged.connect(self.change_category)  # 连接分类改变事件


        self.sort_combobox = ComboBox()
        self.sort_combobox.addItems(["默认顺序", "按名字", "按价格", "按饱腹度", "按体力", "按心情"])
        self.sort_combobox.setFixedWidth(self.width() // 4)
        self.sort_combobox.currentTextChanged.connect(self.sort_items)

        right_layout.addWidget(BodyLabel("商品分类"))
        right_layout.addWidget(self.category_list)
        sort_layout = QHBoxLayout()
        self.adbutton = SwitchButton()
        self.adbutton.checkedChanged.connect(self.sort_items)
        sort_layout.addWidget(BodyLabel("排序方式"))
        sort_layout.addWidget(self.adbutton)
        self.adbutton.setOffText("↑")
        self.adbutton.setOnText("↓")
        right_layout.addLayout(sort_layout)
        right_layout.addWidget(self.sort_combobox)

        # 左侧商品显示区域
        left_out = QVBoxLayout()
        left_out.setContentsMargins(12,12,12,12)
        left_layout = QVBoxLayout()

        # 顶部搜索栏
        top_layout = QHBoxLayout()
        self.search_bar = SearchLineEdit()
        self.search_bar.setPlaceholderText("搜索商品")
        self.search_bar.setFixedHeight(self.window_height // 14)
        self.search_bar.setFixedWidth(self.width() // 2)  # 搜索栏宽度为窗口宽度的一半
        self.search_bar.searchSignal.connect(self.perform_search)
        top_layout.addWidget(self.search_bar)

        # 添加金币图标和金币显示
        balance_layout = QHBoxLayout()
        self.balance_icon = ImageLabel()
        pic_length = self.window_height // 15
        self.balance_icon.setPixmap(QPixmap("picture_src/coin.png").scaled \
                                        (pic_length, pic_length, Qt.KeepAspectRatio))  # 加载金币图标
        self.balance_label = QLabel(f"金币:{self.balance:.2f}")
        self.balance_label.setToolTip("为什么会有小数点？")
        balance_layout.addWidget(self.balance_icon)
        balance_layout.addWidget(self.balance_label)
        balance_layout.setAlignment(Qt.AlignRight)
        top_layout.addLayout(balance_layout)

        # 商品网格
        self.grid_layout = QGridLayout()
        self.update_grid_layout()
        left_layout.addLayout(top_layout,1)
        left_layout.addLayout(self.grid_layout,15)

        # 底部分页
        bottom_layout = QHBoxLayout()
        # 创建居中的子布局
        center_layout = QHBoxLayout()
        self.page_selector = SSpinBox()
        self.page_selector.setFocusPolicy(Qt.NoFocus)
        self.page_selector.setRange(1, self.total_pages)
        self.page_selector.setValue(self.current_page)
        self.page_selector.valueChanged.connect(self.change_page)

        center_layout.addWidget(QLabel("页码"))
        center_layout.addWidget(self.page_selector)
        center_layout.setAlignment(Qt.AlignCenter)

        # 将子布局添加到底部布局中
        bottom_layout.addLayout(center_layout)
        # 添加到父布局
        left_layout.addLayout(bottom_layout)

        # 包裹右侧布局的容器
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        right_widget.setStyleSheet("background-color: lightgray;")  # 设置淡灰色背景

        # 合并左右布局
        left_out.addLayout(left_layout)
        main_layout.addLayout(left_out)
        main_layout.addWidget(right_widget)

    def update_balance(self):
        """更新金币值显示"""
        self.balance_label.setText(f"金币:{self.balance:.2f}")

    def save_user_data(self):
        """将用户数据保存回 JSON 文件"""
        with open("user_data.json", 'w', encoding='utf-8') as file:
            json.dump(self.user_data, file, ensure_ascii=False, indent=4)

    def perform_search(self):
        """根据搜索框的输入过滤商品"""
        search_text = self.search_bar.text().strip().lower()  # 获取搜索关键词
        if not search_text:  # 如果搜索框为空，显示全部商品
            self.filtered_items = self.filter_items_by_category()
        else:
            # 根据商品名称匹配子序列（忽略大小写）
            self.filtered_items = [
                item for item in self.filter_items_by_category()
                if search_text in item["name"].lower()
            ]
        self.current_page = 1  # 搜索后重置为第一页
        self.total_pages = (len(self.filtered_items) + self.items_per_page - 1) // self.items_per_page
        self.page_selector.setRange(1, self.total_pages)
        self.page_selector.setValue(self.current_page)
        self.update_grid_layout()

    def sort_items(self):
        """根据排序方式和排序顺序对商品进行排序"""
        sort_option = self.sort_combobox.currentText()
        is_descending = self.adbutton.isChecked()  # 检查是否选中降序

        if sort_option == "按名字":
            # 按拼音排序
            self.filtered_items.sort(
                key=lambda item: "".join(lazy_pinyin(item["name"])),
                reverse=is_descending
            )
        elif sort_option == "按价格":
            self.filtered_items.sort(
                key=lambda item: float(item["price"]) if item["price"] else 0,
                reverse=is_descending
            )
        elif sort_option == "按饱腹度":
            self.filtered_items.sort(
                key=lambda item: float(item["effect_je"]) if item["effect_je"] else 0,
                reverse=is_descending
            )
        elif sort_option == "按体力":
            self.filtered_items.sort(
                key=lambda item: float(item["effect_tl"]) if item["effect_tl"] else 0,
                reverse=is_descending
            )
        elif sort_option == "按心情":
            self.filtered_items.sort(
                key=lambda item: float(item["effect_xq"]) if item["effect_xq"] else 0,
                reverse=is_descending
            )

        # 更新当前页面为第一页，并刷新网格布局
        self.current_page = 1
        self.total_pages = (len(self.filtered_items) + self.items_per_page - 1) // self.items_per_page
        self.page_selector.setRange(1, self.total_pages)
        self.page_selector.setValue(self.current_page)
        self.update_grid_layout()

    def filter_items_by_category(self):
        """根据当前分类筛选商品"""
        if self.current_category == "全部":
            return self.items
        return [item for item in self.items if item["type"] == self.current_category]

    def update_grid_layout(self):
        """根据当前页码刷新商品网格"""
        # 清除现有布局内容
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().deleteLater()

        # 计算当前页的商品索引范围
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = min(start_index + self.items_per_page, len(self.filtered_items))
        page_items = self.filtered_items[start_index:end_index]

        # 添加当前页的商品到网格
        for i, item in enumerate(page_items):
            row = i // 3
            col = i % 3
            item_widget = self.create_item_widget(item)
            self.grid_layout.addWidget(item_widget, row, col)

        # 添加空白占位小部件以补足6个商品的布局
        total_items = len(page_items)
        if total_items < self.items_per_page:
            for i in range(total_items, self.items_per_page):
                row = i // 3
                col = i % 3
                placeholder = QWidget()
                self.grid_layout.addWidget(placeholder, row, col)

    def change_category(self, category):
        """处理分类切换事件"""
        self.current_category = category
        self.filtered_items = self.filter_items_by_category()
        self.current_page = 1  # 切换分类后重置为第一页
        self.total_pages = (len(self.filtered_items) + self.items_per_page - 1) // self.items_per_page
        self.page_selector.setRange(1, self.total_pages)
        self.page_selector.setValue(self.current_page)
        self.update_grid_layout()

    def change_page(self, value):
        """处理页码改变事件"""
        self.current_page = value
        self.update_grid_layout()

    def create_item_widget(self, item):
        """创建单个商品的显示小组件"""
        widget = ItemWidget(item)
        widget.itemClicked.connect(self.show_item_details)  # 连接信号到槽
        widget.buyClicked.connect(self.show_purchase_widget)
        return widget

    def show_item_details(self, item):
        """显示商品详情页面并添加向上弹出的动画效果"""
        if self.details_widget:
            self.details_widget.deleteLater()

        self.details_widget = QWidget(self)
        self.details_widget.setObjectName("detail_widget")
        self.details_widget.setStyleSheet("""
                QWidget#detail_widget {
                    background-color: rgba(255, 255, 255, 0.95); /* 半透明白色 */
                    border: 2px solid #cccccc;                 /* 灰色边框 */
                    border-radius: 15px;                      /* 圆角边框 */
                }
            """)

        # 设置详情页大小为主窗口的 1/4
        details_width = self.window_width // 2
        details_height = self.window_height // 2

        # 初始位置在窗口下方不可见区域
        initial_x = (self.window_width - details_width) // 2
        initial_y = int((self.window_height - details_height) / 1.8)
        self.details_widget.setGeometry(initial_x, initial_y, details_width, details_height)

        # 目标位置为窗口居中位置
        target_x = initial_x
        target_y = (self.window_height - details_height) // 2

        layout = QVBoxLayout(self.details_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # 添加商品信息
        pixmap = QPixmap(item["image"]).scaled(200, 200, Qt.KeepAspectRatio)
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        layout.addWidget(image_label, alignment=Qt.AlignCenter)

        name_label = QLabel(f"商品名称: {item['name']}")
        price_label = QLabel(f"价格: {item['price']}")
        description_label = QLabel(f"描述: {item['describe']}")
        layout.addWidget(name_label)
        layout.addWidget(price_label)
        layout.addWidget(description_label)

        # 设置透明度效果
        opacity_effect = QGraphicsOpacityEffect(self.details_widget)
        self.details_widget.setGraphicsEffect(opacity_effect)

        # 创建动画组
        animation_group = QParallelAnimationGroup(self)

        # 向上弹出动画
        geometry_animation = QPropertyAnimation(self.details_widget, b"geometry")
        geometry_animation.setDuration(150)  # 动画持续时间（毫秒）
        geometry_animation.setStartValue(QRect(initial_x, initial_y, details_width, details_height))
        geometry_animation.setEndValue(QRect(target_x, target_y, details_width, details_height))
        geometry_animation.setEasingCurve(QEasingCurve.OutCubic)  # 设置缓动曲线为先快后慢

        # 透明度动画
        opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
        opacity_animation.setDuration(150)  # 动画持续时间（毫秒）
        opacity_animation.setStartValue(0.0)  # 初始透明度为完全透明
        opacity_animation.setEndValue(1.0)  # 最终透明度为完全不透明

        # 将动画添加到动画组
        animation_group.addAnimation(geometry_animation)
        animation_group.addAnimation(opacity_animation)

        self.details_widget.show()  # 必须在动画之前显示窗口
        animation_group.start()
        """
            为什么setAttribute(Qt.WA_TransparentForMouseEvents, True)在ListWidget()组件上有BUG？？？是我写的有问题吗？
            第一次开启关闭Qt.WA_TransparentForMouseEvents时所有组件均正常，第二次开启关闭Qt.WA_TransparentForMouseEvents后
            只有ListWidget()组件不再对鼠标事件产生反应，其余组件正常，当对其余组件操作后ListWidget()又恢复正常😅
            QListWidget()和ListWidget()都有上述问题
        """
        # self.components = self.findChildren(QWidget)
        # for component in self.components:
        #     if component != self.details_widget:
        #         component.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        # 安装事件过滤器
        QApplication.instance().installEventFilter(self)

    def close_details(self):
        """关闭详情页面，并添加逐渐变透明的动画效果"""
        if self.details_widget:
            # 获取当前透明效果
            opacity_effect = self.details_widget.graphicsEffect()

            if not isinstance(opacity_effect, QGraphicsOpacityEffect):
                # 如果没有设置透明效果，重新设置
                opacity_effect = QGraphicsOpacityEffect(self.details_widget)
                self.details_widget.setGraphicsEffect(opacity_effect)

            animation_group = QParallelAnimationGroup(self)

            # 创建透明度动画
            opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
            opacity_animation.setDuration(150)  # 动画持续时间（毫秒）
            opacity_animation.setStartValue(1.0)  # 初始透明度为完全不透明
            opacity_animation.setEndValue(0.0)  # 最终透明度为完全透明

            animation_group.addAnimation(opacity_animation)

            # 动画结束后销毁组件
            def on_animation_finished():
                self.details_widget.deleteLater()
                self.details_widget = None
                # 卸载事件过滤器
                QApplication.instance().removeEventFilter(self)

            opacity_animation.finished.connect(on_animation_finished)
            animation_group.start()

    def eventFilter(self, obj, event):
        """事件过滤器：点击详情页外区域关闭详情页面"""
        if self.details_widget:
            if event.type() == QEvent.MouseButtonPress:
                # 如果点击的不是详情页范围，关闭详情页
                if not self.details_widget.geometry().contains(self.mapFromGlobal(event.globalPos())):
                    self.close_details()
                    return True  # 屏蔽事件
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        """监听按键事件，按 ESC 退出详情页面"""
        if event.key() == Qt.Key_Escape and self.details_widget:
            self.close_details()
        super().keyPressEvent(event)

    def show_purchase_widget(self, item):
        """显示购买详情页面"""
        if self.details_widget:  # 如果已有详情页，关闭之前的
            self.close_details()

        self.details_widget = QWidget(self)
        self.details_widget.setObjectName("detail_widget")
        self.details_widget.setStyleSheet("""
                QWidget#detail_widget {
                    background-color: rgba(255, 255, 255, 0.95); /* 半透明白色 */
                    border: 2px solid #cccccc;                 /* 灰色边框 */
                    border-radius: 15px;                      /* 圆角边框 */
                }
            """)

        # 设置详情页大小为主窗口的 1/4
        details_width = self.window_width // 2
        details_height = self.window_height // 2

        # 初始位置在窗口下方不可见区域
        initial_x = (self.window_width - details_width) // 2
        initial_y = int((self.window_height - details_height) / 1.8)
        self.details_widget.setGeometry(initial_x, initial_y, details_width, details_height)

        # 目标位置为窗口居中位置
        target_x = initial_x
        target_y = (self.window_height - details_height) // 2

        layout = QVBoxLayout(self.details_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # 添加商品信息
        name_label = QLabel(f"商品名称: {item['name']}")
        price_label = QLabel(f"单价: {item['price']} 元")
        layout.addWidget(name_label, alignment=Qt.AlignCenter)
        layout.addWidget(price_label, alignment=Qt.AlignCenter)

        # 添加数量滑块、输入框及总价显示
        quantity_label = QLabel("选择数量:")
        slider = Slider(Qt.Horizontal)
        slider.setMinimum(1)  # 最小数量
        slider.setMaximum(100)  # 最大数量
        slider.setValue(1)  # 默认数量
        input_box = LineEdit()
        input_box.setPlaceholderText("1")
        input_box.setFixedWidth(details_width // 5)
        input_box.setValidator(QIntValidator(1, 100))  # 限制输入为1到100的整数
        input_box.setAlignment(Qt.AlignCenter)  # 居中显示
        total_price_label = QLabel(f"总价: {item['price']} 元")

        # 实现滑块与输入框的双向同步
        def slider_to_input(value):
            input_box.setText(str(value))
            update_total_price(value)

        def input_to_slider():
            if input_box.text() == "":
                # 如果输入框为空，暂不更新滑块
                return
            try:
                value = int(input_box.text())
                slider.setValue(value)
            except ValueError:
                input_box.setText(str(slider.value()))

        def update_total_price(value):
            total_price = value * int(item['price'])
            total_price_label.setText(f"总价: {total_price} 元")

        slider.valueChanged.connect(slider_to_input)  # 滑块更新同步输入框
        input_box.textChanged.connect(input_to_slider)  # 输入框更新同步滑块

        # 布局数量选择区域
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(slider)
        quantity_layout.addWidget(input_box)
        layout.addLayout(quantity_layout)
        layout.addWidget(total_price_label, alignment=Qt.AlignCenter)

        # 添加确认和取消按钮
        cc_layout = QHBoxLayout()
        confirm_button = PushButton("确认购买")
        confirm_button.clicked.connect(lambda: self.confirm_purchase(item, slider.value()))  # 将数量传递给确认函数
        cancel_button = PushButton("取消")
        cancel_button.clicked.connect(self.close_details)
        cc_layout.addWidget(confirm_button)
        cc_layout.addWidget(cancel_button)
        layout.addLayout(cc_layout)

        # 设置透明度效果
        opacity_effect = QGraphicsOpacityEffect(self.details_widget)
        self.details_widget.setGraphicsEffect(opacity_effect)

        # 创建动画组
        animation_group = QParallelAnimationGroup(self)

        # 向上弹出动画
        geometry_animation = QPropertyAnimation(self.details_widget, b"geometry")
        geometry_animation.setDuration(150)  # 动画持续时间（毫秒）
        geometry_animation.setStartValue(QRect(initial_x, initial_y, details_width, details_height))
        geometry_animation.setEndValue(QRect(target_x, target_y, details_width, details_height))
        geometry_animation.setEasingCurve(QEasingCurve.OutCubic)  # 设置缓动曲线为先快后慢

        # 透明度动画
        opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
        opacity_animation.setDuration(150)  # 动画持续时间（毫秒）
        opacity_animation.setStartValue(0.0)  # 初始透明度为完全透明
        opacity_animation.setEndValue(1.0)  # 最终透明度为完全不透明

        # 将动画添加到动画组
        animation_group.addAnimation(geometry_animation)
        animation_group.addAnimation(opacity_animation)

        self.details_widget.show()  # 必须在动画之前显示窗口
        animation_group.start()

        # self.components = self.findChildren(QWidget)
        # for component in self.components:
        #     if component != self.details_widget:
        #         component.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        # 安装事件过滤器
        QApplication.instance().installEventFilter(self)

    def confirm_purchase(self, item, value):
        """处理购买确认逻辑"""
        total_price = int(item['price']) * value  # 计算总价

        if self.balance >= total_price:
            # 钱包余额足够购买
            self.balance -= total_price  # 扣除金额
            self.update_balance()
            self.user_data["balance"] = self.balance

            stuff = item["name"]
            default_quantity = 0  # 当键不存在时赋予的默认值
            # 检查并添加新键
            if stuff not in self.user_data["bag"]:
                self.user_data["bag"][stuff] = default_quantity

            self.user_data["bag"][stuff] += value

            new_record = {
                "item_name": stuff,
                "quantity": value,
                "total_price": total_price
            }

            self.user_data["purchase_history"].append(new_record)

            self.save_user_data()
            Flyout.make(SuccessBuyFlyoutView(self, self.window_width, self.window_height, item, value),
                        self.details_widget, self.details_widget, aniType=FlyoutAnimationType.PULL_UP)

        else:
            # 钱包余额不足
            Flyout.make(FailBuyFlyoutView(self, self.window_width, self.window_height, item, value),
                        self.details_widget, self.details_widget, aniType=FlyoutAnimationType.PULL_UP)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    window = ShoppingApp()
    window.show()
    sys.exit(app.exec_())
