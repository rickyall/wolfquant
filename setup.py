"""
name: 'wolfquant'
version: '0.0.2'
description: '构建期货交易的框架'
author: 'rickyall'
author_email： 'rickyallqi@gmail.com'
url： 'https://github.com/rickyall/wolfquant.git'
"""
import os

# 将包安装到anaconda中
package_path = '{}/site-packages/wolfquant'.format(os.__file__[:-6])
os.system('rm -rf {}'.format(package_path))
os.system('cp -rf wolfquant {}'.format(package_path))
print('安装完成！')
