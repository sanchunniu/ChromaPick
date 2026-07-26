import sys
import os
import random
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon, QPainter, QPen, QPixmap


def resource_path(relative_path):
    """获取资源文件路径，兼容开发环境和 PyInstaller 打包"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def load_icon(filename):
    """加载图标，文件不存在时返回 None"""
    path = resource_path(filename)
    return QIcon(path) if os.path.exists(path) else None


class ScreenPicker(QWidget):
    """全屏取色器覆盖层"""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)

        screen = QApplication.primaryScreen()
        self.geom = screen.geometry()
        self.screenshot = screen.grabWindow(0)
        self.pixmap = QPixmap(self.screenshot)
        self.setGeometry(self.geom)

        self.mouse_pos = None
        self.mag_size = 200
        self.scale = 8

    def paintEvent(self, event):
        if self.mouse_pos is None:
            return
        mx, my = self.mouse_pos.x(), self.mouse_pos.y()
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)

        # 放大镜
        half = self.mag_size // 2
        mag_half_raw = self.mag_size // (2 * self.scale)
        sx = max(0, mx - mag_half_raw)
        sy = max(0, my - mag_half_raw)
        mag = self.pixmap.copy(sx, sy, mag_half_raw * 2, mag_half_raw * 2)
        mag = mag.scaled(self.mag_size, self.mag_size,
                         Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

        lx = mx - half
        ly = my - half
        if lx < 0:
            lx = 0
        if ly < 0:
            ly = 0
        if lx + self.mag_size > self.geom.width():
            lx = self.geom.width() - self.mag_size
        if ly + self.mag_size > self.geom.height():
            ly = self.geom.height() - self.mag_size

        painter.drawPixmap(lx, ly, mag)
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(lx - 1, ly - 1, self.mag_size + 2, self.mag_size + 2)

        # 放大镜中心十字
        cx = lx + self.mag_size // 2
        cy = ly + self.mag_size // 2
        painter.setPen(QPen(Qt.red, 1))
        painter.drawLine(cx - 12, cy, cx + 12, cy)
        painter.drawLine(cx, cy - 12, cx, cy + 12)

        # 颜色信息
        color = self.pixmap.toImage().pixelColor(mx, my)
        text = f"RGB({color.red()}, {color.green()}, {color.blue()})  #{color.red():02X}{color.green():02X}{color.blue():02X}"
        painter.setFont(QFont("Consolas", 10))
        fm = painter.fontMetrics()
        tw = fm.horizontalAdvance(text) + 12
        th = fm.height() + 6
        info_x = lx + 4
        info_y = ly + self.mag_size - th - 4
        painter.fillRect(info_x, info_y, tw, th, QColor(0, 0, 0, 180))
        painter.setPen(Qt.white)
        painter.drawText(info_x + 6, info_y + fm.ascent() + 3, text)
        painter.end()

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.pos()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            color = self.pixmap.toImage().pixelColor(
                event.pos().x(), event.pos().y())
            self.selected_color = color
            self.close()
        elif event.button() == Qt.RightButton:
            self.selected_color = None
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.selected_color = None
            self.close()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._updating = False
        self.initUI()
        self.center()

    def initUI(self):
        self.setWindowTitle("颜色转换器")

        ico = load_icon("color_switch.ico")
        if ico:
            self.setWindowIcon(ico)

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(24, 24, 24, 24)

        # 标题
        title = QLabel("欢迎使用颜色转换器")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 副标题
        sub = QLabel(
            "你可以输入颜色的16进制字符或RGB值，或利用拾色器来获取屏幕上的颜色来进行颜色格式转换。"
        )
        sub.setFont(QFont("SimSun", 9))
        sub.setStyleSheet("color: blue;")
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)
        layout.addWidget(sub)
        layout.addSpacing(12)

        # 十六进制输入
        layout.addWidget(QLabel("十六进制值 (#RRGGBB):"))
        self.hex_input = QLineEdit()
        self.hex_input.setPlaceholderText("例如: #FF0000 或 FF0000 或 F00")
        self.hex_input.setFont(QFont("Consolas", 13))
        self.hex_input.textChanged.connect(self.on_hex_changed)
        layout.addWidget(self.hex_input)

        self.hex_error = QLabel("当前输入不合法，请检查！")
        self.hex_error.setStyleSheet("color: red; font-size: 11px;")
        self.hex_error.setVisible(False)
        layout.addWidget(self.hex_error)

        layout.addSpacing(6)

        # RGB 输入
        rgb_label = QLabel("RGB 值:")
        layout.addWidget(rgb_label)

        row = QHBoxLayout()
        self.r_spin = QSpinBox()
        self.g_spin = QSpinBox()
        self.b_spin = QSpinBox()
        for spin in (self.r_spin, self.g_spin, self.b_spin):
            spin.setRange(0, 255)
            spin.setFont(QFont("Consolas", 12))
            spin.valueChanged.connect(self.on_rgb_changed)

        row.addWidget(QLabel("R:"))
        row.addWidget(self.r_spin)
        row.addSpacing(8)
        row.addWidget(QLabel("G:"))
        row.addWidget(self.g_spin)
        row.addSpacing(8)
        row.addWidget(QLabel("B:"))
        row.addWidget(self.b_spin)
        layout.addLayout(row)

        self.rgb_error = QLabel("当前输入不合法，请检查！")
        self.rgb_error.setStyleSheet("color: red; font-size: 11px;")
        self.rgb_error.setVisible(False)
        layout.addWidget(self.rgb_error)

        layout.addSpacing(10)

        # 按钮
        btn_row = QHBoxLayout()
        self.picker_btn = QPushButton("  拾色器")
        ico = load_icon("pick_color.ico")
        if ico:
            self.picker_btn.setIcon(ico)
        self.picker_btn.setFont(QFont("Microsoft YaHei", 11))
        self.picker_btn.clicked.connect(self.start_picker)
        btn_row.addWidget(self.picker_btn)

        self.random_btn = QPushButton("  随机颜色")
        ico = load_icon("random_color.ico")
        if ico:
            self.random_btn.setIcon(ico)
        self.random_btn.setFont(QFont("Microsoft YaHei", 11))
        self.random_btn.clicked.connect(self.random_color)
        btn_row.addWidget(self.random_btn)

        self.complement_btn = QPushButton("  取互补色")
        ico = load_icon("opposite_color.ico")
        if ico:
            self.complement_btn.setIcon(ico)
        self.complement_btn.setFont(QFont("Microsoft YaHei", 11))
        self.complement_btn.clicked.connect(self.complementary_color)
        btn_row.addWidget(self.complement_btn)

        self.help_btn = QPushButton("?")
        self.help_btn.setFixedSize(26, 26)
        self.help_btn.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.help_btn.setStyleSheet("QPushButton { border: 2px solid #888; border-radius: 13px; color: #555; background: transparent; } QPushButton:hover { border-color: #333; color: #000; }")
        self.help_btn.setToolTip("互补色计算公式：\nR' = 255 - R\nG' = 255 - G\nB' = 255 - B")
        self.help_btn.setCursor(Qt.WhatsThisCursor)
        btn_row.addWidget(self.help_btn)

        layout.addLayout(btn_row)

        layout.addSpacing(10)

        # 颜色预览
        self.preview = QFrame()
        self.preview.setMinimumHeight(140)
        self.preview.setStyleSheet(
            "background-color: #000000; border: 2px solid #888888; border-radius: 4px;")
        layout.addWidget(self.preview)

        # 底部按钮
        bottom_row = QHBoxLayout()
        bottom_row.setAlignment(Qt.AlignCenter)

        self.about_btn = QPushButton("关于")
        self.about_btn.setFont(QFont("Microsoft YaHei", 9))
        self.about_btn.setFixedSize(80, 28)
        self.about_btn.clicked.connect(self.show_about)
        bottom_row.addWidget(self.about_btn)

        self.quit_btn = QPushButton("退出")
        self.quit_btn.setFont(QFont("Microsoft YaHei", 9))
        self.quit_btn.setFixedSize(80, 28)
        self.quit_btn.clicked.connect(self.close)
        bottom_row.addWidget(self.quit_btn)

        layout.addLayout(bottom_row)

        self.setLayout(layout)
        self.resize(860, 520)

        # 初始颜色 #8CF0FF
        self._updating = True
        self.r_spin.setValue(140)
        self.g_spin.setValue(240)
        self.b_spin.setValue(255)
        self.hex_input.setText("#8CF0FF")
        self._updating = False
        self.update_color(140, 240, 255)

    def closeEvent(self, event):
        QApplication.instance().quit()
        event.accept()

    def center(self):
        screen = QApplication.primaryScreen().geometry()
        geo = self.geometry()
        self.move((screen.width() - geo.width()) // 2,
                  (screen.height() - geo.height()) // 2)

    # ---------- 逻辑 ----------

    def parse_hex(self, text):
        t = text.strip().lstrip("#")
        if len(t) == 6:
            try:
                return QColor(int(t[0:2], 16), int(t[2:4], 16), int(t[4:6], 16))
            except ValueError:
                return None
        if len(t) == 3:
            try:
                return QColor(int(t[0] * 2, 16), int(t[1] * 2, 16), int(t[2] * 2, 16))
            except ValueError:
                return None
        return None

    def update_color(self, r, g, b):
        self.preview.setStyleSheet(
            f"background-color: rgb({r},{g},{b}); "
            "border: 2px solid #888888; border-radius: 4px;"
        )

    def on_hex_changed(self, text):
        if self._updating:
            return
        color = self.parse_hex(text)
        if color is not None:
            self.hex_error.setVisible(False)
            self._updating = True
            self.r_spin.setValue(color.red())
            self.g_spin.setValue(color.green())
            self.b_spin.setValue(color.blue())
            self._updating = False
            self.update_color(color.red(), color.green(), color.blue())
        else:
            self.hex_error.setVisible(bool(text.strip()))

    def on_rgb_changed(self):
        if self._updating:
            return
        r, g, b = self.r_spin.value(), self.g_spin.value(), self.b_spin.value()
        self._updating = True
        self.hex_input.setText(f"#{r:02X}{g:02X}{b:02X}")
        self.hex_error.setVisible(False)
        self.rgb_error.setVisible(False)
        self._updating = False
        self.update_color(r, g, b)

    def start_picker(self):
        self.hide()
        QTimer.singleShot(200, self._show_picker)

    def _show_picker(self):
        self.picker = ScreenPicker()
        self.picker.show()
        self._picker_timer = QTimer()
        self._picker_timer.timeout.connect(self._check_picker)
        self._picker_timer.start(100)

    def _check_picker(self):
        if not self.picker.isVisible():
            self._picker_timer.stop()
            color = getattr(self.picker, "selected_color", None)
            if color is not None:
                self._updating = True
                self.r_spin.setValue(color.red())
                self.g_spin.setValue(color.green())
                self.b_spin.setValue(color.blue())
                self.hex_input.setText(
                    f"#{color.red():02X}{color.green():02X}{color.blue():02X}")
                self.hex_error.setVisible(False)
                self.rgb_error.setVisible(False)
                self._updating = False
                self.update_color(color.red(), color.green(), color.blue())
            self.show()

    def random_color(self):
        r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        self._updating = True
        self.r_spin.setValue(r)
        self.g_spin.setValue(g)
        self.b_spin.setValue(b)
        self.hex_input.setText(f"#{r:02X}{g:02X}{b:02X}")
        self.hex_error.setVisible(False)
        self.rgb_error.setVisible(False)
        self._updating = False
        self.update_color(r, g, b)

    def complementary_color(self):
        r, g, b = self.r_spin.value(), self.g_spin.value(), self.b_spin.value()
        r, g, b = 255 - r, 255 - g, 255 - b
        self._updating = True
        self.r_spin.setValue(r)
        self.g_spin.setValue(g)
        self.b_spin.setValue(b)
        self.hex_input.setText(f"#{r:02X}{g:02X}{b:02X}")
        self.hex_error.setVisible(False)
        self.rgb_error.setVisible(False)
        self._updating = False
        self.update_color(r, g, b)


    def show_about(self):
        dlg = AboutDialog(self)
        dlg.exec_()


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于 颜色转换器")
        self.setWindowModality(Qt.WindowModal)
        self.setFixedSize(680, 420)

        ico = load_icon("color_switch.ico")
        if ico:
            self.setWindowIcon(ico)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)

        # 介绍文字
        intro = QLabel(
            "颜色转换器是一个轻量级的屏幕取色与颜色格式转换工具。\n\n"
            "支持十六进制与 RGB 相互转换，内置屏幕拾色器可\n"
            "直接抓取屏幕上任意位置的颜色，并提供随机颜色与\n"
            "互补色计算功能，方便设计师和开发者快速获取配色。"
        )
        intro.setFont(QFont("KaiTi", 12))
        intro.setWordWrap(True)
        layout.addWidget(intro)

        layout.addSpacing(6)

        # 灰色分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #cccccc;")
        layout.addWidget(line)

        layout.addSpacing(4)

        # 版本信息
        info_style = "font-size: 16px; color: #333;"
        lbl1 = QLabel("软件版本：V1.3")
        lbl1.setFont(QFont("Microsoft YaHei", 12))
        lbl1.setStyleSheet(info_style)
        layout.addWidget(lbl1)
        lbl2 = QLabel("版本日期：2026年7月26日")
        lbl2.setFont(QFont("Microsoft YaHei", 12))
        lbl2.setStyleSheet(info_style)
        layout.addWidget(lbl2)
        lbl3 = QLabel("软件作者：三春牛-创客")
        lbl3.setFont(QFont("Microsoft YaHei", 12))
        lbl3.setStyleSheet(info_style)
        layout.addWidget(lbl3)

        layout.addSpacing(6)

        # 超链接
        link_style = 'font-size: 15px;'
        bilibili = QLabel(
            '<a href="https://space.bilibili.com/650793568" '
            'style="color: #0066cc; text-decoration: underline;">'
            '作者B站主页</a>'
        )
        bilibili.setFont(QFont("Microsoft YaHei", 12))
        bilibili.setOpenExternalLinks(True)
        bilibili.setStyleSheet(link_style)
        layout.addWidget(bilibili)

        github = QLabel(
            '<a href="https://github.com/sanchunniu/ChromaPick" '
            'style="color: #0066cc; text-decoration: underline;">'
            '仓库地址（Github）（求个Star!）</a>'
        )
        github.setFont(QFont("Microsoft YaHei", 12))
        github.setOpenExternalLinks(True)
        github.setStyleSheet(link_style)
        layout.addWidget(github)

        layout.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.setFont(QFont("Microsoft YaHei", 10))
        close_btn.setFixedSize(100, 30)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        self.setLayout(layout)

        # 居中
        if parent:
            pg = parent.geometry()
            self.move(pg.center().x() - self.width() // 2,
                      pg.center().y() - self.height() // 2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
