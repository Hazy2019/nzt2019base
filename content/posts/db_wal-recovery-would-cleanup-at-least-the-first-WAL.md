---
title: "wal recovery would cleanup at least the first WAL"
date: 2021-03-09
categories:
 - "db"
tags:
 - "rocksdb"
 - "write-ahead-log"
 - "rocksdb-recovery"
pager: true
sidebar: "right"
---

这段时间跟同事尝试修复长期以来项目中遗留的Rocksdb的Case，遇到些有意思的Case，这里记录一下。

## 



## some tips for rocksdb case fixing

1. 对于不支持`-march=native`环境的，可以编译时`export USE_SSE=1`.避免类似`no such instruction: `shlx %r13,%rax,%rax'`的问题。

2. 对于rocksdb的测试case，想保留测试db的，可以搞个`KEEP_DB`环境变量。测试类会根据这个环境变量决定是否清理测试DB。 

<!--more-->
3. example测试命令如下:
```
export USE_SSE=1 && make db_wal_test && KEEP_DB=1 ./db_wal_test --gtest_filter=DBWALTest.RecoveryWithLogDataForSomeCFs
```
