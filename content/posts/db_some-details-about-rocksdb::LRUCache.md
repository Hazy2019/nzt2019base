---
title: "some details about rocksdb::LRUCache"
date: 2021-03-08
categories:
 - "db"
tags:
 - "lrucache"
 - "new expression"
pager: true
sidebar: "right"
completed: false
---

最近有同事找我讨论问题，觉得挺有趣的记录一下。

### `rocksdb::LRUHandle::key()`的历史

第一个问题是`rocksdb::LRUHandle::key()`, 这个函数返回该handle内部存储的key，但为啥某些情况下却返回value呢？

```
68   Slice key() const {
<!--more-->
69     // For cheaper lookups, we allow a temporary Handle object
70     // to store a pointer to a key in "value".
71     if (next == this) {
72       return *(reinterpret_cast<Slice*>(value));
73     } else {
74       return Slice(key_data, key_length);
75     }
76   }
```

乍看一眼，应该是某些场景下（如初始化时）图方便的产物。

另外扫了一眼codebase，确认了下`next == this`分支不会被调用到，凭经验盲猜是某个历史遗留的代码。由于没啥说服力，我去挖坟了一下git log，发现最新rocksdb已经把这个无用分支去掉了, 问题到这里似乎应该结了.

但由于无聊我又去check了一下leveldb在这块的实现,发现这块确实是祖传代码- -！,并且在17年左右就做了一次代码清理。

{{< figure src="../../resources/leveldb-lrucache-commit.png" title="leveldb code clean at lrucache" >}}

### `new expression`的理解

- 问题描述

另外还有个问题，类似下面的语句中的new表达式，`[]`应该怎么理解，是把它理解为type的一部分呢？ 还是非type的一部分？
```
LRUHandle** new_list = new LRUHandle*[new_length];
```

- 问题讨论

我们先不去翻cpp标准，先把自己的大脑当作编译器.可以把问题抽象为如下的形式：

表达式如`T** ptr = new T*[n];`: 

假如`[]`是非type的一部分的话，语义上表达的应该是new了n个连续且类型为T的对象; ---A1

另一方面，假如`[]`是type的一部分的话,语义上表达的应该是new了一个对象，该对象的类型是长度为n/类型为T的数组. ---A2

于是可以得到两个推论，可用于验证：

若A1成立的话，那么按理`T** ptr = new （T*）[n];`应该成立 --- AA1

若A2成立的话，`T** ptr = new （T*[n]）;`应该成立 --- AA2

- 问题解决

但编译器告诉我们括号是有问题的. AA1不成立，AA2成立.

一般写法：
```
[ghostv]$ g++ -std=c++11 -x c++ - -o /tmp/a << EOF
> int main() {
>   int **a = new int*[10];
>   return 0;
> }
> EOF
```

AA1编译器报错:
```
[ghostv]$ g++ -std=c++11 -x c++ - -o /tmp/a << EOF
int main() {
  int **a = new (int*)[10];
  return 0;
}
EOF

<stdin>: In function ‘int main()’:
<stdin>:2:23: error: array bound forbidden after parenthesized type-id
<stdin>:2:23: note: try removing the parentheses around the type-id
```

AA2编译通过:
```
[ghostv]$ g++ -std=c++11 -x c++ - -o /tmp/a << EOF
int main() {
  int **a = new (int*[10]);
  return 0;
}
EOF
```

所以应该按AA2来理解.

AA1 --- Compile Error
AA2 --- Compile OK

- cppreference

现在回过头来check一下标准答案，标准里对于new表达式的定义如下，标准里说的很清楚了，array就是被包含在type里的：

{{< figure src="../../resources/cpp-ref-of-new-expr.png" title="cpp ref of new expr" >}}

- 总结一下为什么会有这个问题？

主要还是`[]`的位置引发小伙伴的难以理解. 
因为这里`[]`是被包含在type里，那么似乎直观上又与声明一个数组类型的语句相冲突：
`T[10] A;`的写法是编译不通过的：

```
[ghostv]$ g++ -std=c++11 -x c++ - -o /tmp/a << EOF
int main() {
  int* [10] A;
  return 0;
}
EOF

<stdin>: In function ‘int main()’:
<stdin>:2:8: error: expected unqualified-id before ‘[’ token
```
另一方面，可以使用一个typedef，但typedef本身似乎也是一样，`[]`在最后：
```
[ghostv]$ g++ -std=c++11 -x c++ - -o /tmp/a << EOF
int main() {
  typedef int* T[10];  T A;
  return 0;
}
EOF
```
最后，如果用template的话，就非常符合直观感受了：
```c++
#include <iostream>
struct a{};
template<typename T>
void fucktype() {
  T a;
  std::cout << sizeof(a) << std::endl; 
}
int main() {
  fucktype<a*[10]>();
  return 0;
}
```
个人猜测，引发不适的估计是为了兼容以前c的语法。



#### 顺便recall一下LRUCache

0. 关于原理，基本上不用再多说了
1. 关于rocksdb是如何使用LRUCache
2. 关于shard数，我们踩过的坑
3. 原生rocksdb::LRUCache只增加元素，达到容量上限后，没有清理元素的过程（etc. GC）
4. 哈希算法： 老版 新版
5. Usage统计：老版 新版
6. 自适应锁优化： 
