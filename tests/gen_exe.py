# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         gen_exe.py
# Description:  使用本地源码构建 pywxdump 可执行文件
# Author:       xaoyaoo
# Date:         2023/11/10
# -------------------------------------------------------------------------------
import shutil
import os
import base64
import sys

# 指定本地源码路径（替换为你的实际路径）
LOCAL_SOURCE_PATH = r"D:\IdeaProjectsGit\PyWxDump-master\pywxdump"  # 示例路径，改为你的本地 pywxdump 源码目录

# 从本地源码中获取版本号
sys.path.insert(0, LOCAL_SOURCE_PATH)  # 将本地源码路径添加到 sys.path
import pywxdump  # 从本地导入 pywxdump
__version__ = pywxdump.__version__
ma_version = __version__.split(".")[0]
mi_version = __version__.split(".")[1]
pa_version = __version__.split(".")[2]

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode('utf-8')

def base64_to_image(base64_string, image_path):
    with open(image_path, "wb") as image_file:
        decoded_string = base64.b64decode(base64_string)
        image_file.write(decoded_string)

code = """
# -*- coding:utf-8 -*-
from pywxdump.cli import console_run
console_run()
"""

spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['wxdump.py'],
             pathex=[r'{root_path}'],  # 添加本地源码路径
             binaries=[],
             datas=[(r'{root_path}\\WX_OFFS.json', 'pywxdump'),
            {datas_741258}
            ],
             hiddenimports={hidden_imports},
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

version_info = {{
          'FileDescription': 'PyWxDump from https://github.com/xaoyaoo/PyWxDump',
          'OriginalFilename': 'None',
          'ProductVersion': '{version}.0',
          'FileVersion': '{version}.0',
          'InternalName': 'wxdump'
}}
a.version = version_info

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='wxdump',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=True,
          argv_emulation=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          onefile=True,
          icon="icon.ico",
          version='wxdump_version_info.txt'
          )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='wxdump')
'''

wxdump_version_info = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({ma_version}, {mi_version}, {pa_version}, 0),
    prodvers=({ma_version}, {mi_version}, {pa_version}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904b0',
        [StringStruct('CompanyName', 'PyWxDump'),
        StringStruct('FileDescription', 'PyWxDump from https://github.com/xaoyaoo/PyWxDump'),
        StringStruct('FileVersion', '{__version__}'),
        StringStruct('InternalName', 'wxdump.exe'),
        StringStruct('LegalCopyright', 'Copyright (C) http://github.com/xaoyaoo/PyWxDump. All rights reserved'),
        StringStruct('OriginalFilename', 'wxdump.exe'),
        StringStruct('ProductName', 'wxdump'),
        StringStruct('ProductVersion', '{__version__}'),
        StringStruct('SquirrelAwareVersion', '1')])
      ]), 
    VarFileInfo([VarStruct('Translation',  [2052, 1200])])
  ]
)
"""

# 创建输出文件夹
os.makedirs("dist", exist_ok=True)

# 将代码写入文件
with open("dist/wxdump.py", "w", encoding="utf-8") as f:
    f.write(code.strip())

current_path = os.path.dirname(os.path.abspath(__file__))
shutil.copy(os.path.join(LOCAL_SOURCE_PATH, "favicon.ico"), "dist/icon.ico")  # 从本地源码复制图标
with open("dist/wxdump_version_info.txt", "w", encoding="utf-8") as f:
    f.write(wxdump_version_info.strip())

# 从本地读取 requirements.txt
require_path = os.path.join(LOCAL_SOURCE_PATH, "requirements.txt")
if os.path.exists(require_path):
    with open(require_path, "r", encoding="utf-8") as f:
        hidden_imports = f.read().splitlines()
    hidden_imports = [i.replace('-', '_').split("=")[0].split("~")[0] for i in hidden_imports if
                      i and i not in ["setuptools", "wheel"]]
    hidden_imports += ["pywxdump", "pywxdump.db", "pywxdump.db.__init__.utils"]
else:
    hidden_imports = ["pywxdump", "pywxdump.db", "pywxdump.db.__init__.utils"]  # 默认值

# 获取本地源码目录下的所有文件用于打包
root_path = LOCAL_SOURCE_PATH
datas_741258 = []
for root, dirs, files in os.walk(root_path):
    for file in files:
        file_path = os.path.join(root, file)
        if "__pycache__" in file_path or file.endswith(".py"):
            continue
        relative_path = file_path.replace(root_path, "").lstrip(os.sep)
        dest_dir = os.path.dirname(relative_path) or '.'
        datas_741258.append(f'''(r'{file_path}', r'{dest_dir}')''')
datas_741258 = ",\n".join(datas_741258)

# 生成 spec 文件
spec_content = spec_content.format(root_path=root_path, hidden_imports=hidden_imports, datas_741258=datas_741258,
                                   version=__version__)
spec_file = os.path.join("dist", "pywxdump.spec")
with open(spec_file, 'w', encoding="utf-8") as f:
    f.write(spec_content.strip())

# 执行打包命令
cmd = f'pyinstaller --clean --distpath=dist {spec_file}'
print(cmd)
os.system(cmd)