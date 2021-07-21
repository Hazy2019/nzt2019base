---
title: "c++ notes：recall of move-semantics and rvalue-reference (1)"
date: 2021-02-02
description: ""
categories:
  - "c++"
tags:
  - "rvalue-references"
  - "move-semantics"
authorbox: true # Enable authorbox for specific page
pager: true # Enable pager navigation (prev/next) for specific page
toc: true # Enable Table of Contents for specific page
weight: 2
---

几年前，整理了一份rvalue相关笔记：[以前的一份笔记](https://zhuanlan.zhihu.com/p/111826434)，梳理近况时，发现某些问题还是没有弄清楚。

## `Universal Reference`
- Q: 什么场景下需要考虑这个问题？
  A：模板元编程时，需要考虑兼容各种传入参数类型时（尤其是『左值/右值』）。基本上我感觉就是为了处理完美转发问题。比如写一个工厂函数模板，需要同时兼容传入的参数是左值和右值的情况，核心点是一个右值无法用于初始化一个左值引用，c++11之前要解决这个问题，要么写很多重复偏特化模板，要么付出拷贝参数的代价。

  c++11引入右值引用之后，上述问题可以通过`universal reference`来解决，即传入参数是左值时，形参的类型推导为左值引用，是右值时，推导为右值引用，同时只需要提供一套模板即可。
  

- Q: 什么是`Universal Reference`?
  A: 形如`T&&`, `T`不含有任何的cv限定符, 且`T`需要被推导
  
  >`G1`. 
  >If a variable or parameter is declared to have type T&& for some deduced type T, that variable or parameter is a universal reference.
  
<!--more-->
- examples:
    ```
    using Widget = int;
    Widget&& var1 = Widget(); 
    //不是`Universal Reference`，因为`T&&`不是个需要被推导的类型,`T`是`Widget`.
    //实际上var1的类型是个右值引用.

    auto&& var2 = var1;
    //是`Universal Reference`，那么var2的类型是什么？具体与var1是左值还是右值有关，由于var1是个左值，var2的类型就是左值引用。下文解释。
    ```


## rvalue or lvalue

- 什么是左值/右值？
  >`G2`.
  > If you can take the address of an expression, the expression is an lvalue.
  > If the type of an expression is an lvalue reference (e.g., T& or const T&, etc.), that expression is an lvalue. 
  > Otherwise, the expression is an rvalue.  Conceptually (and typically also in fact), rvalues correspond to temporary objects, such as those returned from functions or created through implicit type conversions. Most literal values are also rvalues.
- examples：
```
using Widget = int;
Widget&& var1 = Widget();
// 变量`var1`的类型是右值引用。
// 表达式`var1`可以被取地址，因此`var1`是左值。
```

> (cpp-ref)Even if the variable's type is rvalue reference, the expression consisting of its name is an lvalue expression;


## `Universal Reference`的推导
- 用于初始化`Universal Reference`的表达式是左值的话，`Universal Reference`是左值引用；反之如果用于初始化的本身是右值，那么`Universal Reference`是右值引用。
  >`G3`.
  > - If the expression initializing a universal reference is an lvalue, the universal reference becomes an lvalue reference.
  > - If the expression initializing the universal reference is an rvalue, the universal reference becomes an rvalue reference.

- examples:
```
using Widget = int;
Widget&& var1 = Widget();
auto&& var2 = var1;
// var2的类型是什么？
// 初始化它的值是个左值，因此var2的类型是左值引用
```

## 引用折叠(`reference deduce`)
- 场景是某个函数具有形如`template<class T> void f(T&& a);`的形式，根据传入的a的类型，T是如何推导出来的？

>`G4`.

>```
>Deduce Rules:
>T&  &&  => T& 
>T&& &   => T&
>T&  &   => T&
>T&& &&  => T&&
>```

```
template<class T>
void f(T&& a);
```
`T&&`整体类型由调用语句传入的表达式是左值还是右值决定(G3)。
通过T&&整体类型结合上面的DeduceRule可以推出T的类型。


example 1:
```
f(1); // 1 is rvalue, so T&& ==> int&&, so T => int
      // f(1) ==> f<int&&>(int&&);
```

example 2:
```
int x = 10;
f(x); // x is lvalue, so T&& ==> int&, saccording to the deducing rules shown.o T ==> int& (according to the deducing rules shown.)
      // f(x) ==> (f<int&>(int& &&) -->) f<int&>(int&)
```

## perfect forward
主要是用在1个函数模板调用另1个函数模板时：
```
template <typename T1, typename T2>
void outer(T1&& t1, T2&& t2) 
{
    inner(std::forward<T1>(t1), std::forward<T2>(t2));
}
```
- `std::forward<T>(a)`的实现：
    ```
    std::forward<T>(a) ==> static_cast<T&&>(a)
    ```

Todo: 
- [ ] how `std::bind` is impl?

## move semantics
- `std::move(a)`的实现：
    ```
    std::move(a) ==> static_cast<remove_reference<decltype(arg)>::type&&>(arg)
    ```

- what `std::move` do:
  not change var's lifetime, but make it movable.


## References
- https://zhuanlan.zhihu.com/p/111826434
- https://isocpp.org/blog/2012/11/universal-references-in-c11-scott-meyers
- https://stackoverflow.com/questions/3582001/what-are-the-main-purposes-of-using-stdforward-and-which-problems-it-solves
- https://stackoverflow.com/questions/28483250/rvalue-reference-is-treated-as-an-lvalue
- http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2002/n1385.htm
- https://stackoverflow.com/questions/18369128/how-can-i-see-the-type-deduced-for-a-template-type-parameter
- https://stackoverflow.com/questions/15663539/why-isnt-object-returned-by-stdmove-destroyed-immediately

