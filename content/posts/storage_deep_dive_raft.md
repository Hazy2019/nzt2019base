---
title: "理解raft"
date: 2020-12-19T21:20:49
description: “raft算法深入"
categories:
  - "基础架构"
tags:
  - "分布式"
menu: main
authorbox: true # Enable authorbox for specific page
pager: true # Enable pager navigation (prev/next) for specific page
toc: true # Enable Table of Contents for specific page
mathjax: true # Enable MathJax for specific page
sidebar: "right" # Enable sidebar (on the right side) per page
widgets: # Enable sidebar widgets in given order per page
  - "search"
  - "recent"
  - "taglist"
---

> 首先带几个疑问:
> 1. commit和apply分别指什么？
> 1. 收到RequestVote RPC的Server在什么情况下会Grant Vote?
> 1. raft-log必须要顺序apply吗？为什么？
> 1. 每条raft-log是否都需要对应的termId？为什么？
> 1. raft-group的配置变更是怎么做的？
> 1.

## raft算法笔记





