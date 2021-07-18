---
title: "cmake cheatsheet：找不到package; PUBLIC依赖和PRIVATE依赖; ..."
date: 2021-05-19
categories:
 - "other"
tags:
 - "cmake"
pager: true
sidebar: "right"
---

### cannot find a package

经常苦于cmake的find_package无法找到某个包（包括libxxx.so和其include files）
可以设置cmake的搜索路径，显式编译，类似以下:
<!--more-->

```
cmake ../xxx -DCMAKE_INSTALL_PREFIX=${WKSPACEINSTALL} -DCMAKE_INCLUDE_PATH=${ME_INC} -DCMAKE_LIBRARY_PATH=${ME_LIB}"
```

注意这三个宏，分别代表：
- `-DCMAKE_INSTALL_PREFIX`：安装路径
- `-DCMAKE_INCLUDE_PATH`：头文件包含路径,多个路径用冒号`:`分隔
- `-DCMAKE_LIBRARY_PATH`：lib搜索路径


### PUBLIC依赖和PRIVATE依赖
`target_link_libraries()`指令存在三种关键字修饰的依赖：PUBLIC/PRIVATE/INTERFACE
分别是什么意思？
PUBLIC：头文件和源文件都包含第三方库头文件
PRIVATE：源文件包含第三方库头文件
INTERFACE：头文件包含第三方库头文件

### Tips
cmake -S . -B build -G "Unix Makefiles"

### 如何查看依赖了哪个(些)shared library？
- ldd xxx.so or ldd xxx.binary
- ldconfig -p | grep ssl

### 在cmake后的make出问题时，如何找到出错的子命令
cmake遇到问题第一时间试下`make VERBOSE=1`

在编译folly时，遇到个诡异的问题，cmake成功，并且各依赖库也能找到，但make时却提示glog中的符号undefined reference,错误大概类似：
```
make
..blah..
..blah..
[100%] Linking CXX static library libfolly_exception_counter.a
[100%] Built target folly_exception_counter
/usr/bin/ld: ../../../libfolly.a(MemoryIdler.cpp.o): in function `folly::detail::fetchStackLimits()':
/WORKSPACE/folly/folly/detail/MemoryIdler.cpp:107: undefined reference to `google::LogMessage::LogMessage(char const*, int, int, unsigned long, void (google::LogMessage::*)())'
```
`make VERBOSE=1`可以看到具体哪个命令出问题：

```
[100%] Linking CXX executable logging_example
cd /home/me/WORKSPACE/folly/_build/folly/logging/example && /usr/local/bin/cmake -E cmake_link_script CMakeFiles/logging_example.dir/link.txt --verbose=1
/usr/lib64/ccache/c++ -fPIC -fPIC -fPIC -fPIC -fPIC -rdynamic CMakeFiles/logging_example.dir/main.cpp.o -o logging_example  -Wl,-rpath,/home/me/WORKSPACE/install/lib:/usr/local/lib liblogging_example_lib.a ../../../libfolly.a /home/me/WORKSPACE/install/lib64/libfmt.a /home/me/WORKSPACE/install/lib/libboost_context.so.1.76.0 /home/me/WORKSPACE/install/lib/libboost_filesystem.so.1.76.0 /home/me/WORKSPACE/install/lib/libboost_program_options.so.1.76.0 /home/me/WORKSPACE/install/lib/libboost_regex.so.1.76.0 /home/me/WORKSPACE/install/lib/libboost_system.so.1.76.0 /home/me/WORKSPACE/install/lib/libboost_thread.so.1.76.0 -pthread /home/me/WORKSPACE/install/lib64/libdouble-conversion.a /home/me/WORKSPACE/install/lib/libgflags.a -lpthread -lglog /home/me/WORKSPACE/install/libevent-LMExs25lGT7QkQgLPyYSiRU_G55y_kOy5rbMw1-ug8M/lib/libevent.a -lz -lssl -lcrypto -lbz2 -llzma -llz4 /usr/local/lib/libzstd.so /home/me/WORKSPACE/install/lib64/libsnappy.a /home/me/WORKSPACE/install/lib/libdwarf.a -Wl,-Bstatic -liberty -Wl,-Bdynamic -laio /home/me/WORKSPACE/install/lib/libsodium.so -ldl -lunwind -lstdc++fs
/usr/bin/ld: ../../../libfolly.a(MemoryIdler.cpp.o): in function `folly::detail::fetchStackLimits()':
/home/me/WORKSPACE/folly/folly/detail/MemoryIdler.cpp:107: undefined reference to `google::LogMessage::LogMessage(char const*, int, int, unsigned long, void (google::LogMessage::*)())'
/usr/bin/ld: ../../../libfolly.a(MemoryIdler.cpp.o): in function `folly::detail::MemoryIdler::unmapUnusedStack(unsigned long)':
/home/me/WORKSPACE/folly/folly/detail/MemoryIdler.cpp:193: undefined reference to `google::ErrnoLogMessage::ErrnoLogMessage(char const*, int, int, unsigned long, void (google::LogMessage::*)())'
/usr/bin/ld: ../../../libfolly.a(SignalHandler.cpp.o): in function `folly::symbolizer::installFatalSignalHandler(std::bitset<64ul>)':
```
有-lglog，先手动跑下上面这条编译指令，果然有问题，把-lglog换成具体路径(之前已经装过，只不过不再系统路径下)下的libglog.a是可以执行成功的：
```
me@85 example]$ /usr/lib64/ccache/c++ -rdynamic CMakeFiles/logging_example.dir/main.cpp.o -o logging_example  -Wl,-rpath,/home/me/WORKSPACE/install/lib:/usr/local/lib liblogging_example_lib.a ../../../libfolly.a /home/me/WORKSPACE/install/lib64/libfmt.a /home/me/WORKSPACE/install//libboost_context.so.1.76.0 /home/me/WORKSPACE/install/lib/libboost_filesystem.so.1.76.0 /home/me/WORKSPACE/install/lib/libboost_program_options.so.1.76.0 /home/me/WORKSPACE/install/lib/libboost_regex.so.1.76.0 /home/me/WORKSPACE/install/lib/libboost_system.so.1.76.0 /home/weijian.g/WORKSPACE/install/lib/libboost_thread.so.1.76.0 -pthread /home/me/WORKSPACE/install/lib64/libdouble-conversion.a /usr/local/lib/libgflags_nothreads.a -L/home/me/WORKSPACE/install/lib64 -lglog /home/me/WORKSPACE/install/libevent-LMExs25lGT7QkQgLPyYSiRU_G55y_kOy5rbMw1-ug8M/lib/libevent.a -lzssl -lcrypto -lbz2 -llzma -llz4 /usr/local/lib/libzstd.so /home/me/WORKSPACE/install/lib64/libsnappy.a /home/me/WORKSPACE/install/lib/libdwarf.a -Wl,-Bstatic -liberty -Wl,-Bdynamic -laio /home/me/WORKSPACE/install/lib/libsodium.so -ldl -lunwind -lstdc++fs
[me@85 example]$
```
问题很明了，是CMAKE的lib搜索路径出了问题，因为我设置了`-DCMAKE_LIBRARY_PATH`,多个路径用分号隔开，我给搞成冒号了。。。。。

