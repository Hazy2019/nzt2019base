---
title: "c++ notes：recall of move-semantics and rvalue-reference"
date: 2020-09-11T11:12
description: ""
categories:
  - "c++"
tags:
  - "rvalue-references"
  - "move-semantics"
comments: false # Enable Disqus comments for specific page
authorbox: true # Enable authorbox for specific page
pager: true # Enable pager navigation (prev/next) for specific page
toc: true # Enable Table of Contents for specific page
---

## `Universal Reference`
- Q: 什么是`Universal Reference`?
  A: 形如`T&&`, `T`不含有任何的cv限定符, 且`T`需要被推导
  
  >If a variable or parameter is declared to have type T&& for some deduced type T, that variable or parameter is a universal reference.

- examples:
```
using Widget = int;
Widget&& var1 = Widget(); 
//不是`Universal Reference`，因为`T&&`不是个需要被推导的类型,`T`是`Widget`.
//实际上var1的类型是个右值引用.

auto&& var2 = var1;
//是`Universal Reference`，那么var2的类型是什么？请看下文
```


## rvalue or lvalue

- 什么是左值/右值？
  > If you can take the address of an expression, the expression is an lvalue.
  > If the type of an expression is an lvalue reference (e.g., T& or const T&, etc.), that expression is an lvalue. 
  > Otherwise, the expression is an rvalue.  Conceptually (and typically also in fact), rvalues correspond to temporary objects, such as those returned from functions or created through implicit type conversions. Most literal values are also rvalues.
- examples：
```
using Widget = int;
Widget&& var1 = Widget();
auto&& var2 = var1;
// 变量`var1`的类型是右值引用
// 表达式`var1`可以被取址
```


## `Universal Reference`的推导值
- 用于初始化`Universal Reference`的表达式是左值的话，`Universal Reference`是左值引用；反之如果用于初始化的本身是右值，那么`Universal Reference`是右值引用。
  > - If the expression initializing a universal reference is an lvalue, the universal reference becomes an lvalue reference.
  > - If the expression initializing the universal reference is an rvalue, the universal reference becomes an rvalue reference.

- examples:

## 引用折叠(`reference deduce`)
```
T&  && 
T&& &
T&  &
T&& &&
```


## References
- https://zhuanlan.zhihu.com/p/111826434
- https://isocpp.org/blog/2012/11/universal-references-in-c11-scott-meyers
- https://stackoverflow.com/questions/3582001/what-are-the-main-purposes-of-using-stdforward-and-which-problems-it-solves