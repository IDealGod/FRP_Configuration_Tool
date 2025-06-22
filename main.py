import os
import subprocess
import sys
import threading
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import darkdetect
import toml
import tkinter.messagebox as messagebox

print(r"""
  ___   ____                   _           _____   ____    ____            _____    ___     ___    _     
 |_ _| |  _ \    ___    __ _  | |         |  ___| |  _ \  |  _ \          |_   _|  / _ \   / _ \  | |    
  | |  | | | |  / _ \  / _` | | |         | |_    | |_) | | |_) |           | |   | | | | | | | | | |    
  | |  | |_| | |  __/ | (_| | | |         |  _|   |  _ <  |  __/            | |   | |_| | | |_| | | |___ 
 |___| |____/   \___|  \__,_| |_|  _____  |_|     |_| \_\ |_|      _____    |_|    \___/   \___/  |_____|
                                  |_____|                         |_____|                                
"""
          "\r\n本程序由IDeal_提供，旨在提升FRP内网穿透服务的便利性\r\n"
          "IDeal_的B站：https://space.bilibili.com/1275343562\r\n"
          "便宜稳定服务器推荐：http://u5a.cn/guiEj\r\n"
      "\r\n本软件完全免费且开源，如果你是从别人那购买的，那么就是被骗了，请给差评\r\n软件开源于：https://github.com/IDealGod/FRP_Configuration_Tool\r\n"
      "                                               version_1.0  by IDeal_")
class CustomMessageBox:
    def __init__(self, parent, icon_path=None):
        self.parent = parent
        self.icon_path = icon_path

    def show(self, title, message, message_type="info"):
        top = ttk.Toplevel(self.parent)
        top.title(title)
        top.resizable(False, False)
        if self.icon_path and os.path.exists(self.icon_path):
            try:
                top.iconbitmap(self.icon_path)
            except:
                pass

        frame = ttk.Frame(top, padding=20)
        frame.pack(fill=BOTH, expand=True)

        icon_frame = ttk.Frame(frame)
        icon_frame.pack(side=LEFT, padx=(0, 15))

        if message_type == "info":
            img = "✅"
        elif message_type == "error":
            img = "❌"
        else:
            img = "⚠️"

        icon_label = ttk.Label(icon_frame, text=img, font=("Arial", 24))
        icon_label.pack()

        msg_label = ttk.Label(frame, text=message, font=("Microsoft YaHei", 12))
        msg_label.pack(side=LEFT, fill=BOTH, expand=True)

        btn_frame = ttk.Frame(top)
        btn_frame.pack(pady=(0, 10))

        btn = ttk.Button(btn_frame, text="确定", command=top.destroy, width=10)
        btn.pack()

        top.update_idletasks()
        width = top.winfo_width()
        height = top.winfo_height()
        x = (top.winfo_screenwidth() // 2) - (width // 2)
        y = (top.winfo_screenheight() // 2) - (height // 2)
        top.geometry(f'+{x}+{y}')

        top.transient(self.parent)
        top.grab_set()
        self.parent.wait_window(top)

if not os.path.exists("frpc.exe") or not os.path.exists("frpc.toml"):
    root = ttk.Window()
    root.withdraw()
    messagebox.showerror("文件缺失", "未找到 frpc.exe 或 frpc.toml，请确保它们位于当前目录下。")
    print("Frpc文件不存在，请将本软件移动到Frpc目录下。")
    sys.exit(1)

system_theme = darkdetect.theme()
theme = "darkly" if system_theme == "Dark" else "journal"
app = ttk.Window("FRPC配置工具 By IDeal_", theme, resizable=(False, False))
style = ttk.Style(theme=theme)

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

icon_path = get_resource_path("icon.ico")
msg_box = CustomMessageBox(app, icon_path)

if os.path.exists(icon_path):
    try:
        app.iconbitmap(icon_path)
    except:
        print("警告：图标文件格式不支持，使用默认图标")
else:
    print("警告：未找到图标文件，使用默认图标")

def update_config():
    try:
        config['serverAddr'] = entries['serverAddr（远程服务器IP）'].get()
        config['serverPort'] = int(entries['serverPort（远程服务器端口）'].get())

        if 'proxies' not in config:
            config['proxies'] = []

        if len(config['proxies']) == 0:
            config['proxies'].append({})

        config['proxies'][0]['name'] = entries['name（隧道名）'].get()
        config['proxies'][0]['type'] = entries['type（隧道类型）'].get()
        config['proxies'][0]['localIP'] = entries['localIP（本地IP）'].get()
        config['proxies'][0]['localPort'] = int(entries['localPort（本地端口）'].get())
        config['proxies'][0]['remotePort'] = int(entries['remotePort（远程访问端口）'].get())

        with open(file_path, 'w', encoding='utf-8') as file:
            toml.dump(config, file)
        msg_box.show("保存成功", "配置已成功保存！", "info")
    except Exception as e:
        msg_box.show("保存失败", f"保存配置时发生错误：{e}", "error")

def start_frpc():
    try:
        threading.Thread(target=run_frpc, daemon=True).start()
        msg_box.show("启动成功", "frpc 已启动！", "info")
    except Exception as e:
        msg_box.show("启动失败", f"启动 frpc 时发生错误：{e}", "error")

input_frame = ttk.Frame(app, padding=20)
input_frame.pack(fill=BOTH, expand=YES)

ttk.Label(input_frame, text="FRPC配置信息", font=("Microsoft YaHei", 18, "bold")).grid(row=0, column=0, columnspan=2,
                                                                                       pady=10)

labels = ["serverAddr（远程服务器IP）：", "serverPort（远程服务器端口）：", "name（隧道名）：",
          "type（隧道类型）：", "localIP（本地IP）：", "localPort（本地端口）：", "remotePort（远程访问端口）："]
entries = {}

for i, label_text in enumerate(labels, start=1):
    ttk.Label(input_frame, text=label_text, width=30, anchor="e",
              font=("Microsoft YaHei", 14)).grid(row=i, column=0, padx=10, pady=10, sticky="e")
    entry = ttk.Entry(input_frame, width=40, font=("Microsoft YaHei", 14))
    entry.grid(row=i, column=1, padx=10, pady=10, sticky="w")
    entries[label_text.strip("：")] = entry

ttk.Separator(input_frame, orient='horizontal').grid(row=len(labels) + 1, column=0, columnspan=2, sticky="ew", pady=10)

button_frame = ttk.Frame(app, padding=20)
button_frame.pack(fill=BOTH, expand=YES)

style.configure('TButton', font=("Microsoft YaHei", 14))
style.configure('Green.TButton', font=("Microsoft YaHei", 14), background="#7CFC00", foreground="#008000")

start_button = ttk.Button(button_frame, text="启动 frpc", command=start_frpc, style='Green.TButton')
start_button.pack(side=RIGHT, padx=10, pady=10)

save_button = ttk.Button(button_frame, text="保存配置", command=update_config, style='TButton')
save_button.pack(side=RIGHT, padx=10, pady=10)

file_path = "frpc.toml"
try:
    config = toml.load(file_path)

    if 'serverAddr' in config:
        entries['serverAddr（远程服务器IP）'].insert(0, config['serverAddr'])
    if 'serverPort' in config:
        entries['serverPort（远程服务器端口）'].insert(0, config['serverPort'])
    if 'proxies' in config and len(config['proxies']) > 0:
        if 'name' in config['proxies'][0]:
            entries['name（隧道名）'].insert(0, config['proxies'][0]['name'])
        if 'type' in config['proxies'][0]:
            entries['type（隧道类型）'].insert(0, config['proxies'][0]['type'])
        if 'localIP' in config['proxies'][0]:
            entries['localIP（本地IP）'].insert(0, config['proxies'][0]['localIP'])
        if 'localPort' in config['proxies'][0]:
            entries['localPort（本地端口）'].insert(0, config['proxies'][0]['localPort'])
        if 'remotePort' in config['proxies'][0]:
            entries['remotePort（远程访问端口）'].insert(0, config['proxies'][0]['remotePort'])
except Exception as e:
    msg_box.show("配置文件错误", f"加载配置文件时出错：{e}", "error")

def run_frpc():
    try:
        process = subprocess.Popen(['frpc.exe', '-c', 'frpc.toml'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

        return_code = process.poll()
        if return_code != 0:
            error_msg = process.stderr.read()
            msg_box.show("FRPC错误", f"frpc 运行异常：{error_msg}", "error")
    except Exception as e:
        msg_box.show("FRPC错误", f"运行 frpc 时发生错误：{e}", "error")


try:
    app.mainloop()
except KeyboardInterrupt:
    print("FRPC已关闭")