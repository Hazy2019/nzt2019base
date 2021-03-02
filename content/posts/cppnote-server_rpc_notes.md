---
title: "c++服务端rpc笔记：读muduo有感"
date: 2018-12-01T21:26:49+08:00
description: ""
categories:
  - "c++"
tags:
  - "rpc framework"
lead: "rpc框架" # Lead text
comments: false # Enable Disqus comments for specific page
authorbox: true # Enable authorbox for specific page
pager: true # Enable pager navigation (prev/next) for specific page
toc: true # Enable Table of Contents for specific page
---

最近比较详细地缕了一遍公司内部另一个团队的存储产品（基于apache thrift），后简称为A。到目前为止，本团队存储产品自研的rpc框架，加上自己写过一个简单rpc框架用于rdb实例分裂，已经接触了3个rpc框架。准备在这篇文章总结下一些个人感想。

### 连接处理模型

- A的服务端：使用thrift-rpc的nonblock-server，连接处理模型是同步的：
  a. io线程在收到一个包后，会先把自己设为idle（具体点就是摘掉本线程上的可读写事件），扔给worker线程处理完成后再加回来。

- A的cli端的处理是同步的：
<!--more-->
  a. 一条连接发完一个包，会等待对应的收包（如果需要的话）。

结合上述两点，整体上看这个系统的吞吐不会很高，起码网络rpc这块，由于基本上pipeline的长度只有1，我甚至怀疑后端被打满会比较吃力。

### 锁

- thrift(NonBlockingServer)内部随处可见都是锁：例如，worker线程池公用一条处理队列，这个队列是由一把大锁来保护的。

基本这块我没发现有太大的优化，可以预想的是，随着io线程和worker线程的增加，性能可能无法得到线性扩展。

### 比较好的设计应该是什么样

- 善用各种异步pipeline模式


- share-nothing思想

  一个线程池共用一个总的大队列 vs. 每个线程内部自己维护队列
