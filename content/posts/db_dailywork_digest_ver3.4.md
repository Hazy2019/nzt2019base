---
title: "digest of 3.4"
date: 2021-03-04
description: "digest"
categories:
  - "other"
tags:
  - "digest"
authorbox: true
pager: true
sidebar: "right"
---

0. rvalue references summary (50%)
    impl of std::forward, std::move
0.1.1 acquire & release semantics
https://en.cppreference.com/w/cpp/atomic/memory_order
https://www.modernescpp.com/index.php/acquire-release-semantic

<!--more-->
1. transaction isolation level (30% p1 done)
2. time of distributed system: TSO from percolator; logical clock(0%)
https://www.jianshu.com/p/8500882ab38c
3. paxos(0%)
4. raft questions and answers(50%, end of paper quiz) .
5. design pattern of `Buffer`
6. rpc summary: thrift and igs-server
7. acqure and release semantics in std cpp(2%)
8. why perf impacted when scand>0 in output of `sar -B`
9. how to implement a aligned version of malloc:
https://stackoverflow.com/questions/38088732/explanation-to-aligned-malloc-implementation
10. wal的savepoint干啥的 (90%)
https://wanghenshui.github.io/2019/04/25/rocksdb-wal-term-point.html
10.1 writebatch格式
       writebatch life cycle
10.2 InstrumentedMutex干啥的
10.3 pthread mutex vs. pthread mutex adaptive

11. RocksDB 2020年特性跟进 - global bloom filter
12. `USE_SSE` (90%)
https://stackoverflow.com/questions/52653025/why-is-march-native-used-so-rarely

13. 1个writebatch的life cycle
14. 读流程&写流程

15. case fixing - db_wal_test (0%)
16. case fixing - rocksdb lrucache handle `bug`(0%)
