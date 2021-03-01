---
title: "算法笔记：跳表（r2）"
date: 2020-03-01
description: ""
categories:
  - "algorithm"
tags:
  - "skiplist"
lead: "skiplist" # Lead text
comments: false # Enable Disqus comments for specific page
authorbox: true # Enable authorbox for specific page
mathjax: true
pager: true # Enable pager navigation (prev/next) for specific page
toc: true # Enable Table of Contents for specific page
---

## 实现一个skiplist

上一篇笔记里回顾了跳表的性质和思想，并且看了一眼rocksdb里的skiplist实现。

然后由于好奇，我自己写了一个skiplist，这里记录下。

该skiplist的特性：
- 不支持concurrent
<!--more-->
- 没有struct hack
- 没有fast path
- 因为使用了template所以是header only的
- 格式化依赖了fmt，日志依赖了spdlog
- 支持graphviz脚本输出

基本上中规中矩的一个实现，亮点是该skiplist可以输出一个graphviz的脚本，可以让我们很方便地调试和理解。

如：
```
./skiplist_test.out --gtest_filter=skiplist.insert5
digraph {  
  rankdir=LR 
  node [shape=record]
  nodesep=0
N0[label="<l0>HEAD"]
N1[label="<l0>10"]
N2[label="<l0>20"]
N4[label="<l0>30"]
N3[label="<l0>40"]
N5[label="<l0>50"]
N0:l0->N1:l0
N1:l0->N2:l0
N2:l0->N4:l0
N4:l0->N3:l0
N3:l0->N5:l0
}
```
输出一个5节点的skiplist，可以随意找个graphviz在线画图的[网站](https://dreampuf.github.io/GraphvizOnline/)

上面这个我们可以得到：
{{< figure src="../../resources/skiplist-of-5-nodes.png" title="a skiplist of 5 nodes" >}}

当然这个实现可以用于leetcode1206的答题。加个warpper就可以了，可参考[相关测试](https://github.com/Hazy2019/cppcraft/blob/master/src/educational/skiplist_test.cc)。

以上。