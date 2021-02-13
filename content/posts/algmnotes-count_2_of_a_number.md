---
title: "算法笔记：计算1到n中2出现的个数"
date: 2018-06-01T20:26:39+08:00
description: ""
categories:
  - "algorithm"
tags:
  - "数位枚举"
lead: "枚举" # Lead text
comments: false # Enable Disqus comments for specific page
authorbox: true # Enable authorbox for specific page
pager: true # Enable pager navigation (prev/next) for specific page
mathjax: true # Enable MathJax for specific page
toc: true # Enable Table of Contents for specific page
---

这是读书时一篇旧文搬运.几年后再次回顾下算法.

## 问题

给定一个数字n，求1到n序列中2出现的总次数。n最大值可能是10^9。

## 思路

### 暴力

依次求解1..n每个数含有多少个2，最后求和。

给定数字n，其位数（10进制）为`logn`，具体的时间复杂度大致如下：

$T(n) = log_{10}n + log_{10}{(n-1)} + ... + log_{10}{1} = log_{10}{n!} = O(log_{10}{n!})$

$\Rightarrow $

$T(n) = O(log{n^n}) = O(nlogn)$

所以，暴力法时间复杂度是`nlogn`的

### 数位枚举

换一个枚举思路，正常的枚举是 i -> i+1 -> i+2 ...这样,现采用数位遍历的方式，假设n是K位数,所有出现的2，出现的位置只能在这个范围内：[0,K-1]。（从0开始比较好算）
所以问题可以转变为：对于每个$d\in[0,K-1]$,求符合条件为$\in[1,n]$且第d位为2的数字的个数和$S_d$.
最后累加$\sum_{d=1}^KS_d$.

对于第d位为2的数字个数如何求解？很容易我们可以归纳出数字个数与第d位数字与2的大小关系有关：

PS: 以下的d是从0开始取的。

给定n，假设第d位数字小于2,举个例子：

n = 716130, d = 2， 第d位数字为1，该位为2且满足小于等于n的数字是：200 - 299， 1200 - 1299， 2200 - 2299， ..., 715200 - 715299，显然有716 * 100个，规约一下有: 
$$
S_d = n / 10^{d+1} * 10^d  \qquad \text{if} \ digit(d,n) \lt2
$$

类似地，假设第d位数字大于2，举个例子：

n = 716130, d = 3， 第d位数字为6，该位为2且满足小于等于n的数字是：2000 - 2999，12000-12999，...,712000-712999，显然有72*1000个，规约下，有：
$$
S_d = （n / 10^{d+1}+1） * 10^d  \qquad \text{if} \ digit(d,n) \gt2
$$

最后一种可能，假设第d位数字等于2，举个例子：
n = 716230, d = 2，第d位数字为2，该位为2且满足小于等于n的数字应该就是第d位小于2的情况下的$S_d$再加上余出来的716200 - 716230这31个数字，规约下，有：

$$
S_d = n / 10^{d+1} * 10^d +  (n - (n \mod 10^{d}) + 1)   \qquad \text{if} \ digit(d,n) = 2
$$

最后遍历n的每一位，求出这些数字在累加即可。

总结下来，难点在于如何转变为数位枚举的思维方式，即把一般直觉上的子问题：给定一个数字，求这个数字含有的2的个数，转为，求2在这些数字里的第d位一共出现了几次==>转为数符合这样的数的个数问题。
另外对于某个数字含有多个2而言（如202），其实是被枚举过程计算多次的，从而符合2的总个数要求。
```
 0  1 ...  9
10 11 ... 19
20 21 ... 29
```
这个算法时间复杂度是`O（logn）`

其实领悟到一个道理，就是转变思维方式的重要性，当某件事你发现特别难以推进时，不妨考虑跳出原来的视角，从其他角度入手解决问题。

## Reference

- Crack the Coding Interview 18.4
- [时间复杂度$O(logn!) \Rightarrow O(nlogn) $的等价分析](https://blog.csdn.net/hzh_0000/article/details/80955511)
