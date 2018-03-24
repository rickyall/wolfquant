# windows
以win7为标准：
下载[ta-lib-0.4.0-msvc.zip](http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-msvc.zip) 并解压到 C:\ta-lib
这个是32位版本的，如果想使用64位版本的，需要重新进行编译。
- 下载并解压**ta-lib-0.4.0-msvc.zip**
- 将解压后的文件移动到C：\ta-lib
- 下载VS2017，免费版的即可，记得选择VS C++ 特性
- 编译ta-lib
    - 从开始菜单中进行[VS2015 x64 Native Tools Command Prompt]
    - 切换到C:\ta-lib\c\make\cdr\win32\msvc
    - 运行nmake
- 安装ta-lib python包
```sh
    $ git clone https://github.com/mrjbq7/ta-lib
    $ cd ta-lib
    $ python setup.py install
```