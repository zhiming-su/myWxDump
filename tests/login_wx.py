import base64
import os
import tempfile
import winreg
import glob
from io import BytesIO

import psutil
import uiautomation as uia
import logging
import time

import win32gui
from PIL import Image

from pywxdump.mywxauto.wxauto import FindWindow, GetPathByHwnd

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("wechat.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def find_wechat_path():
    common_paths = [
        r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
        r"C:\Program Files\Tencent\WeChat\WeChat.exe",
        os.path.expanduser(r"~\AppData\Local\WeChat\WeChat.exe")
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path

    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\WeChat"
        )
        install_location, _ = winreg.QueryValueEx(key, "InstallLocation")
        winreg.CloseKey(key)
        wechat_exe = os.path.join(install_location, "WeChat.exe")
        if os.path.exists(wechat_exe):
            return wechat_exe
    except FileNotFoundError:
        pass

    program_files = [
        r"C:\Program Files",
        r"C:\Program Files (x86)"
    ]
    for pf in program_files:
        pattern = os.path.join(pf, "**", "WeChat.exe")
        for wechat_exe in glob.glob(pattern, recursive=True):
            if os.path.exists(wechat_exe):
                return wechat_exe

    return None

def start_wechat():
    wechat_path = find_wechat_path()

    if wechat_path:
        try:
            os.startfile(wechat_path)
            logging.info("微信已启动")

            login_window = LoginWnd()
            if login_window.login() :
                logging.info("微信正在登陆中...")
            else:
                print(login_window.get_qrcode())

        except Exception as e:
            logging.error(f"启动微信时出错: {e}")
    else:
        logging.error("未找到微信程序，请确认已安装微信")

def close_wechat():
    try:
        # 遍历所有进程，查找微信
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == 'wechat.exe':
                proc.terminate()  # 尝试正常终止进程
                proc.wait(timeout=3)  # 等待进程结束
                print("微信已退出")
                return
        print("未找到运行中的微信进程")
    except psutil.NoSuchProcess:
        print("微信进程已不存在")
    except psutil.AccessDenied:
        print("无法终止微信进程，权限不足")
    except Exception as e:
        print(f"关闭微信时出错: {e}")

class LoginWnd:
    _class_name = 'WeChatLoginWndForPC'
    UiaAPI = uia.PaneControl(ClassName=_class_name, searchDepth=1)

    def __repr__(self) -> str:
        return f"<wxauto LoginWnd Object at {hex(id(self))}>"

    def _show(self):
        self.HWND = FindWindow(classname=self._class_name)
        win32gui.ShowWindow(self.HWND, 1)
        win32gui.SetWindowPos(self.HWND, -1, 0, 0, 0, 0, 3)
        win32gui.SetWindowPos(self.HWND, -2, 0, 0, 0, 0, 3)
        self.UiaAPI.SwitchToThisWindow()

    @property
    def _app_path(self):
        HWND = FindWindow(classname=self._class_name)
        return GetPathByHwnd(HWND)

    def login(self):
        enter_button = self.UiaAPI.ButtonControl(Name='进入微信')
        if enter_button.Exists():
            enter_button.Click(simulateMove=False)
            return True
        return False

    def get_qrcode(self):
        """获取登录二维码

        Returns:
            str: 二维码图片的保存路径
        """
        switch_account_button = self.UiaAPI.ButtonControl(Name='切换账号')
        if switch_account_button.Exists():
            switch_account_button.Click(simulateMove=False)
        self._show()
        qrcode_control = self.UiaAPI.ButtonControl(Name='二维码')
        if qrcode_control.Exists():
            # 创建临时文件保存截图
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                temp_path = temp_file.name
            qrcode_control.CaptureToImage(temp_path)

            # 将图片转换为 Base64 编码
            with open(temp_path, "rb") as image_file:
                base64_str = base64.b64encode(image_file.read()).decode('utf-8')

            # 删除临时文件
            os.remove(temp_path)
            return base64_str
        else:
            logging.error("二维码控件未找到")
            return None
if __name__ == "__main__":
    start_wechat()
    print("10S后退出微信")
    time.sleep(10)
    close_wechat()