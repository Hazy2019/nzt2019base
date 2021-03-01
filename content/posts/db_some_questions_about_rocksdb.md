---
title: "rocksdb探究 - 一些问题"
date: 2020-01-07T21:26:49+08:00
description: "usages"
categories:
  - "rocksdb"
tags:
  - "rocksdb"
lead: "一些rocksdb相关问题记录" # Lead text
comments: false # Enable Disqus comments for specific page
authorbox: true # Enable authorbox for specific page
pager: true # Enable pager navigation (prev/next) for specific page
toc: true # Enable Table of Contents for specific page
---

1. 写请求batch内的多个操作是否会被拆开，为什么？
2. block-cache里的缓存项是否会因为某个sst被compact而失效？
3. event-listener的实现
4. perf-context的实现
5. ThreadLocalPtr的实现以及为什么
<!--more-->
6. ROCKSDB中的MVCC
7. rocksdb读路径下的各种迭代器/各层cache分析
8. env分析和使用
