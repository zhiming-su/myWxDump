import requests


# 下载音频
url = 'http://127.0.0.1:5000/api/rs/video?src=FileStorage\\Video\\2025-04\\9ec2b590ffc52eafdc650bde5e227202.mp4'
r = requests.get(url)

# 保存为本地文件
with open('temp.mp4', 'wb') as f:
    f.write(r.content)


