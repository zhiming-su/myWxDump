from pywxdump.mywxauto.wxauto import WeChat
import time

wx = WeChat()

# 首先设置一个监听列表，列表元素为指定好友（或群聊）的昵称
listen_list = [
    '1001'
]

# 然后调用`AddListenChat`方法添加监听对象，其中可选参数`savepic`为是否保存新消息图片
# for i in listen_list:
#     wx.AddListenChat(who=i)

wx = WeChat()

# 加载更多历史消息
wx.LoadMoreMessage()

# 获取当前聊天窗口消息
msgs = wx.GetAllMessage()
print(msgs)
