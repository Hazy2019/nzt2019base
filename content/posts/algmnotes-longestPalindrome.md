---
title: "算法笔记： 最长回文子串"
date: 2018-12-01T21:26:49+08:00
description: ""
categories:
  - "algorithm"
tags:
  - "最长回文子串"
  - "DP"
lead: "DP" # Lead text
comments: false # Enable Disqus comments for specific page
authorbox: true # Enable authorbox for specific page
pager: true # Enable pager navigation (prev/next) for specific page
toc: true # Enable Table of Contents for specific page
---

这是读书时一篇旧文搬运.几年后再次回顾下算法.

### 描述
给定一个串，求它的最长回文子串。

### DP思路

DP的关键是梳理出问题与子问题的关系。

<!--more-->
`F[i,j]`表示i..j的最长回文串的长度，那么跟其子问题的关系如下：

```
  F[i,j] = max { F[i+1, j-1] + 2 ----- if str[i] == str[j] && F[i+1, j-1] == j-1-(i+1)+1 ////如果i+1..j-1非回文但又有str[i] == str[j]怎么办？
                 F[i+1,j]        ----- otherwise1
                 F[i,j-1]        ----- otherwise2
                }
```

如果问题是判断某个串是否为回文子串，那么问题与子问题的关系则变为：
```
  isP[i,j] = {
                isP[i+1,j-1] ----- if str[i] == str[j]
                false        ----- otherwise
             }
```

### 具体编码

这个就不贴代码了.

### Manacher算法

主要是利用到了回文串的特点(中心对称)，解题路径上可以优化掉一些分支. 已求解的部分子问题，如果是某个回文串的一半，那么其另一半可以直接得到答案。

由于我们的目标不是优化到百分之百，这个算法具体我就不深究了反正以前也实现过。

### Reference

更详细的可以check以前的旧文.

- https://www.jianshu.com/p/eae9334772c2
