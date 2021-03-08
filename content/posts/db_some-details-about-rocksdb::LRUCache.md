---
title: "some details about rocksdb::LRUCache"
date: 2021-03-08
categories:
 - "db"
tags:
 - "lrucache"
 - "new expression"
pager: true
sidebar: "right"
completed: false
---


最近有同事找我讨论俩问题，觉得挺有趣的记录一下。

### `rocksdb::LRUHandle::key()`的历史

第一个问题是`rocksdb::LRUHandle::key()`, 这个函数返回该handle内部存储的key，但为啥某些情况下却返回value呢？

```
68   Slice key() const {
<!--more-->
69     // For cheaper lookups, we allow a temporary Handle object
70     // to store a pointer to a key in "value".
71     if (next == this) {
72       return *(reinterpret_cast<Slice*>(value));
73     } else {
74       return Slice(key_data, key_length);
75     }
76   }
```

乍看一眼，应该是某些场景下（如初始化时）图方便的产物。
另外扫了一眼codebase，确认了下`next == this`分支不会被调用到，凭经验盲猜是某个历史遗留的代码。由于没啥说服力，我去挖坟了一下git log，发现：1. 最新代码力，我去挖坟了一下git log，
发现最新rocksdb已经把这个无用分支去掉了。问题到这里似乎应该结了，但由于无聊我又去check了一下leveldb在这块的实现,发现这块确实是祖传代码- -！,并且在17年左右就做了一次代码清理。

{{< figure src="../../resources/leveldb-lrucache-commit.png" title="leveldb code clean at lrucache" >}}

### `new expression`

#### 顺便recall一下LRUCache

0. 关于原理，基本上不用再多说了
1. 关于rocksdb是如何使用LRUCache
2. 关于shard数，我们踩过的坑
3. 原生rocksdb::LRUCache只增加元素，达到容量上限后，没有清理元素的过程（etc. GC）
4. 哈希算法： 老版 新版
5. Usage统计：老版 新版
6. 自适应锁优化： 
