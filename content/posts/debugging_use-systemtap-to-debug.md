---
title: "笔记：systemtap相关"
date: 2019.11.1T21:26:49+08:00
description: how to use systemtap
categories:
  - "debugging"
tags:
  - "systemtap"
  - "debug"
lead: how to use systemtap
comments: false
authorbox: true
pager: true
toc: true
sidebar: "right"
---

本文会提及systemtap的以下几点：
 - 如何列出某个可执行文件的所有probe位点
 - 如何取变量的值
 - 如何通过某个地址的解引用取得对应值
 - 如何在.return中拿到变量的最新值
<!--more-->
 - 如何自定义用户态程序probe位点
 - 如何指定probe被调用的频率（命中次数/命中间隔时间）
 - 如何使用外部参数传入*.stp

## topic1 - quick start

## topic2 - how to track a var at probe point of func.call & func.return

## topic3 - how to mock a syscall

