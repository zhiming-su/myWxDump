import logging
import os
import sys
import threading
import time

import _ctypes
import comtypes
import schedule

from pywxdump.api.local_server import get_real_time_msg, get_wxinfo, init_key, InitKeyRequest
from pywxdump.api.utils import ConfData
from pywxdump.mywxauto.wxauto import WeChat
import pywxdump.api.remote_server as remote_server

work_path = os.path.join(os.getcwd(), "wxdump_work")
TIMESTAMP_FILE = os.path.join(work_path, 'last_timestamp.pkl')

_scheduler_started = False  # 全局标志
_job_instance = None        # 保存任务实例
# 创建独立的调度器实例
scheduler_instance = schedule.Scheduler()

auto_init_logger = logging.getLogger("auto_init")
auto_init_logger.setLevel(logging.INFO)  # 设置日志级别

#handler = logging.StreamHandler()
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s:     %(message)s"))
auto_init_logger.addHandler(handler)
gc: ConfData = ConfData()

wx = None  # 定义全局变量

def auto_init_job():
    global _scheduler_started, _job_instance
    if not _scheduler_started:
        _job_instance = scheduler_instance.every(10).seconds.do(job)
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        _scheduler_started = True
        auto_init_logger.info("Scheduler started")
def wxauto_job():
    #pass

    global wx  # 声明为全局变量
    try:
        comtypes.CoInitialize()
        wx = WeChat()
        auto_init_logger.info("WeChat 对象初始化成功")
        remote_server.wx=wx
    except Exception as e:
        auto_init_logger.error(f"微信初始化失败: {e}")

    while True:
        try:

            msgs = wx.GetNextNewMessage(
                savepic=True,  # 保存图片
                savefile=False,  # 保存文件
                savevoice=False)  # 保存语音转文字内容
            if msgs:
                auto_init_logger.info(f"最新微信消息: {msgs}")
        except _ctypes.COMError as e:
            try:
                auto_init_logger.error(f"COM 调用失败: {e}")
                wx = WeChat()  # 重新初始化微信��口对象
                remote_server.wx = wx
            except Exception as inner_e:
                auto_init_logger.error(f"处理 COMError 时发生错误: {inner_e}")
            time.sleep(10)  # 等待一段时间后重试
        except Exception as e:
            try:
                auto_init_logger.error(f"未知错误: {e}")
            except Exception as inner_e:
                auto_init_logger.error(f"处理未知错误时发生错误: {inner_e}")
            time.sleep(10)  # 等待一段时间后重试


def job():
    #检查当前微信数量
    global _job_instance
    wx_info = get_wxinfo()
    if wx_info.get("code") != 0:
        auto_init_logger.error("获取微信信息失败")
    else:
        wx_list = wx_info.get("body")
        if not wx_list:
            auto_init_logger.error("没有检测到微信")
        else:
            auto_init_logger.info(f"检测到微信数量: {len(wx_list)}")
            wx_data = wx_list[0]
            if not wx_data:
                auto_init_logger.error("获取微信信息失败")
            else:
                # 获取微信ID
                wxid = wx_data.get("wxid")
                wx_key = wx_data.get("key")
                wx_path = wx_data.get("wx_dir")
                if not wxid:
                    auto_init_logger.error(f"获取微信ID失败")
                else:
                    my_wxid = gc.get_conf(gc.at, "last")
                    if not my_wxid or wxid != my_wxid:
                        #return ReJson(1001, body="my_wxid is required")
                        auto_init_logger.info(f"当前微信ID: {wxid},开始初始化数据！")
                        #开始初始化微信数据库
                        request_data = InitKeyRequest(
                            wx_path=wx_path,
                            key=wx_key,
                            my_wxid=wxid
                        )

                        # 调用接口函数
                        result = init_key(request_data)
                        if result.get("code") == 0:
                            auto_init_logger.info(f"初始化数据成功,返回结果: {result.get('msg')}")
                            scheduler_instance.cancel_job(_job_instance)
                            auto_init_logger.info("Job任务已取消")
                            wxauto_thread = threading.Thread(target=wxauto_job)
                            wxauto_thread.daemon = True
                            wxauto_thread.start()
                            auto_init_logger.info("wxauto_job任务已启动")
                        else:
                            auto_init_logger.error(f"初始化数据失败,返回结果: {result.get('msg')}")
                    else:
                        auto_init_logger.info(f"已经初始化了，不用初始化")
                        scheduler_instance.cancel_job(_job_instance)
                        auto_init_logger.info("Job任务已取消")
                        wxauto_thread = threading.Thread(target=wxauto_job)
                        wxauto_thread.daemon = True
                        wxauto_thread.start()
                        auto_init_logger.info("wxauto_job任务已启动")

def run_scheduler():
    while True:
        scheduler_instance.run_pending()
        time.sleep(1)


