# ChromaPick

> 从屏幕拾取颜色，轻松转换格式。

**ChromaPick** 是一款基于 PyQt5 的轻量级桌面颜色工具。它可以从屏幕上任意位置拾取颜色，在 HEX 和 RGB 之间自由转换，随机生成颜色，一键计算互补色——界面简洁直观。

---

## 功能特性

- **屏幕拾色器** — 点击屏幕上任意位置抓取颜色，带放大镜辅助精确定位。
- **HEX / RGB 互转** — 输入任意一种格式，另一侧实时同步更新。支持 #RRGGBB、RRGGBB、#RGB 和 RGB 简写。
- **随机颜色** — 一键生成完全随机的 RGB 颜色。
- **互补色** — 一键计算当前颜色的互补色（255 - R, 255 - G, 255 - B）。
- **实时预览** — 底部大色块实时显示当前颜色。
- **输入校验** — HEX 或 RGB 输入不合法时给出红色提示。

## 下载

### 方式一：GitHub Releases

从 [Releases](https://github.com/sanchunniu/ChromaPick/releases) 页面下载最新版压缩包，解压后双击运行。

### 方式二：蓝奏云

下载地址：[https://wwaxl.lanzoum.com/b00g4cyzcf](https://wwaxl.lanzoum.com/b00g4cyzcf)  
提取密码：colr

> 蓝奏云和 GitHub Releases 的内容保持一致，任选一个渠道下载即可。

## 从源码运行

### 安装依赖

```bash
pip install PyQt5
```

### 启动

```bash
python 颜色转换器.py
```

### 打包成 EXE

```bash
pip install pyinstaller
pyinstaller -w -F ^
  --add-data "color_switch.ico;." ^
  --add-data "pick_color.ico;." ^
  --add-data "random_color.ico;." ^
  --add-data "opposite_color.ico;." ^
  --icon "color_switch.ico" "颜色转换器.py"
```

打包完成后可执行文件在 dist/ 目录下。

## 操作说明

| 控件 | 说明 |
|---|---|
| **HEX 输入框** | 输入十六进制颜色代码，如 #FF0000 或 FF0000 |
| **RGB 微调框** | 分别调整 R、G、B 值（0-255） |
| **拾色器** | 进入屏幕取色模式，点击任意像素获取颜色 |
| **随机颜色** | 随机生成一个 RGB 颜色 |
| **取互补色** | 计算当前颜色的互补色 |
| **关于** | 查看版本信息、作者及链接 |
| **退出** | 关闭程序 |

## 项目结构

```
ChromaPick/
  颜色转换器.py       # 主程序
  color_switch.ico    # 窗口图标
  pick_color.ico      # 拾色器按钮图标
  random_color.ico    # 随机颜色按钮图标
  opposite_color.ico  # 互补色按钮图标
  .gitignore
  README.md
```

## 版本信息

**V1.3** — 2026年7月26日

## 作者

**三春牛-创客**

- B站主页: [space.bilibili.com/650793568](https://space.bilibili.com/650793568)
- 仓库地址: [github.com/sanchunniu/ChromaPick](https://github.com/sanchunniu/ChromaPick)

## 许可证

本项目为开源项目，可自由使用、修改和分享。
