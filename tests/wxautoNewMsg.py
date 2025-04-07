
from pywxdump.wxauto.wxauto import WeChat

wx = WeChat()

# 获取下一条新消息

while True:
    msgs = wx.GetNextNewMessage(
        savepic=True,  # 保存图片
        savefile=False,  # 保存文件
        savevoice=False)  # 保存语音转文字内容
    if msgs:
        print(msgs)
    # time.sleep(1)
