---
title: "c++笔记：STL容器迭代器失效场景"
date: 2019-04-11T11:12
description: ""
categories:
  - "c++"
tags:
  - "stl"
  - "container iterator"
lead: "stl迭代器失效场景" # Lead text
comments: false # Enable Disqus comments for specific page
authorbox: true # Enable authorbox for specific page
pager: true # Enable pager navigation (prev/next) for specific page
toc: true # Enable Table of Contents for specific page
---

## CheatSheet
(完整版见下面 Ref1 or cppref)
note:
>顺序型容器
- deque插入or删除操作会导致迭代器失效.
- <B>list则不会</B>（参考其实现）（迭代器&元素的引用都不会随着插入/删除操作而失效）.

--------

>关联型容器
- 迭代器和元素引用的有效性不受影响

--------

>unordered关联型容器
- rehash时会失效迭代器

--------


## stl的list

- 实现上是双向链表
- 迭代器是`a bidirectional iterator to value_type`
- `size()`时间复杂度：c++98的最坏时间复杂度为O(n)， c++11则是常数时间。

------

- 另外有什么办法可以移动链表节点呢？（像我们自己实现一个双向链表那样,挪动几个指针）
```
+---+ --> +---+ --> +---+
| a |     | b |     | c |            a -> b -> c
+---+ <-- +---+ <-- +---+

    +------------------------+
    |                        |
+---+     +---+ <-- +---+ <--+
| a |     | b |     | c |            a -> c -> b
+---+ <-+ +---+ --> +---+ ---+
        |                    |
        +--------------------+
``` 
`splice()`应该可以达到这个目的:
>This effectively inserts those elements into the container and removes them from x, altering the sizes of both containers. The operation <B>does not involve the construction or destruction</B> of any element. They are transferred, no matter whether x is an lvalue or an rvalue, or whether the value_type supports move-construction or not.

需要与`std::swap`区别一下： 做个比喻，有俩菜篮子，swap做的事情是交换菜篮子里的内容（涉及移动or拷贝），splice是交换俩菜篮子（不涉及移动or拷贝）



## References

- [Invalidation Rule of STL Containers](https://stackoverflow.com/questions/6438086/iterator-invalidation-rules)