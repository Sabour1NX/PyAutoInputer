import ctypes
import sys
import os
import time
import re
import traceback
import tkinter as tk
from tkinter import messagebox, simpledialog
import win32api
import win32con
import win32clipboard
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
def log_error(error_msg):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {error_msg}\n")
CONFIG_FILE = "config.txt"
def create_default_config():
    default_content = """[Hello] >>> [2]
[World] >>> [2]"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(default_content)
    return default_content
def parse_config():
    entries = []
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                match = re.match(r"\[(.*?)\] >>> \[(\d+)\]", line)
                if match:
                    text = match.group(1)
                    wait_time = int(match.group(2))
                    entries.append((text, wait_time))
                else:
                    raise ValueError(f"Invalid config line: {line}")
    except Exception as e:
        log_error(f"Config parse error: {str(e)}")
        raise
    return entries
def send_text(text):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text)
    win32clipboard.CloseClipboard()
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(0x56, 0, 0, 0)  # V键
    win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
    win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
# GUI
class AutoTyperApp:
    def __init__(self, master):
        self.master = master
        master.title("PyAutoInputer")
        master.geometry("300x300")
        self.setup_ui()
    def setup_ui(self):
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        self.btn_edit = tk.Button(
            self.main_frame,
            text="编辑配置文件",
            command=self.edit_config,
            height=2,
            width=20
        )
        self.btn_edit.pack(pady=10)
        self.btn_start = tk.Button(
            self.main_frame,
            text="开始输入",
            command=self.start_typing,
            height=2,
            width=20
        )
        self.btn_start.pack(pady=10)
        author_frame = tk.Frame(self.main_frame)
        author_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        author_font = ("微软雅黑", 9)
        self.lbl_author = tk.Label(
            author_frame,
            text="作者: Sabour1NX_ | 版本: 1.0.1",
            font=author_font,
            fg="#666666", 
            anchor=tk.CENTER
        )
        self.lbl_author.pack(fill=tk.X)

    def edit_config(self):
        try:
            if not os.path.exists(CONFIG_FILE):
                create_default_config()
                messagebox.showinfo("提示", "已创建默认配置文件")
            
            os.startfile(CONFIG_FILE)
        except Exception as e:
            log_error(f"Edit config error: {str(e)}")
            messagebox.showerror("错误", f"打开配置文件失败：{str(e)}")
    
    def start_typing(self):
        if not os.path.exists(CONFIG_FILE):
            create_default_config()
            messagebox.showinfo("提示", "配置文件不存在，已创建默认配置")
            return
        
        try:
            entries = parse_config()
        except Exception as e:
            messagebox.showerror("错误", f"配置文件解析失败：{str(e)}")
            return
        
        self.show_countdown(entries)
    
    def show_countdown(self, entries):
        self.main_frame.destroy()
        self.countdown_frame = tk.Frame(self.master)
        self.countdown_frame.pack(expand=True, fill=tk.BOTH)
        
        self.label = tk.Label(
            self.countdown_frame,
            text="将在10秒后开始输入，请切换到目标窗口",
            font=("Arial", 12)
        )
        self.label.pack(pady=20)
        
        self.remaining = 10
        self.update_countdown(entries)
    
    def update_countdown(self, entries):
        if self.remaining > 0:
            self.label.config(text=f"将在{self.remaining}秒后开始输入，请切换到目标窗口")
            self.remaining -= 1
            self.master.after(1000, lambda: self.update_countdown(entries))
        else:
            self.start_typing_process(entries)
    
    def start_typing_process(self, entries):
        self.countdown_frame.destroy()
        self.typing_frame = tk.Frame(self.master)
        self.typing_frame.pack(expand=True, fill=tk.BOTH)
        
        self.status_label = tk.Label(
            self.typing_frame,
            text="正在输入...",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=20)
        
        self.master.after(100, lambda: self.process_entries(entries))
    
    def process_entries(self, entries, index=0):
        if index >= len(entries):
            self.show_completion()
            return
        
        text, wait_time = entries[index]
        try:
            send_text(text)
            self.status_label.config(text=f"已输入：{text}\n等待{wait_time}秒...")
        except Exception as e:
            log_error(f"Input error at index {index}: {str(e)}")
            messagebox.showerror("错误", f"输入过程中发生错误：{str(e)}")
            return
        
        self.master.after((wait_time * 1000), lambda: self.process_entries(entries, index+1))
    
    def show_completion(self):
        self.typing_frame.destroy()
        self.completion_frame = tk.Frame(self.master)
        self.completion_frame.pack(expand=True, fill=tk.BOTH)
        
        tk.Label(
            self.completion_frame,
            text="输入完成！",
            font=("Arial", 14)
        ).pack(pady=20)
        
        tk.Button(
            self.completion_frame,
            text="返回主界面",
            command=self.return_to_main,
            width=15
        ).pack(pady=10)
    
    def return_to_main(self):
        self.completion_frame.destroy()
        self.setup_ui()


def main():
    if not is_admin():
        ctypes.windll.user32.MessageBoxW(0, "非管理员权限无法运行", "错误", 0x10)
        sys.exit()
    
    root = tk.Tk()
    def excepthook(exc_type, exc_value, exc_traceback):
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        log_error(f"Unhandled exception: {error_msg}")
        messagebox.showerror("错误", f"程序发生未处理异常：{str(exc_value)}")
    
    sys.excepthook = excepthook
    try:
        app = AutoTyperApp(root)
        root.mainloop()
    except Exception as e:
        log_error(f"Main loop error: {str(e)}")
        messagebox.showerror("错误", f"程序运行错误：{str(e)}")
if __name__ == "__main__":
    main()