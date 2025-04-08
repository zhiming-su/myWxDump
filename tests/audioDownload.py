import requests


# 下载音频
url = 'http://127.0.0.1:5000/api/rs/audio?src=strive--ing\\2025-04-07_17-06-22_0_41989840225750246.wav'
r = requests.get(url)

# 保存为本地文件
with open('temp.wav', 'wb') as f:
    f.write(r.content)


