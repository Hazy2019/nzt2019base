---
title: "c++14 lamdba表达式一个code小片段分析 -- from folly::NamedThreadFactory"
date: 2021-07-18
categories:
 - "cppnotes"
tags:
 - "folly"
 - "cpp14"
pager: true
sidebar: "right"
---

### 代码片段 and 分析

```
return std::thread(
    [func = std::move(func), name = std::move(name)]() mutable {
      folly::setThreadName(name);
      func();
    });
```

<!--more-->

其中这个lambda表达式语法是cpp14的

from [cpp_ref](https://en.cppreference.com/w/cpp/language/lambda#Lambda_capture)
```
A capture with an initializer acts as if it declares and explicitly captures a variable declared with type auto, whose declarative region is the body of the lambda expression (that is, it is not in scope within its initializer), except that:

if the capture is by-copy, the non-static data member of the closure object is another way to refer to that auto variable.
if the capture is by-reference, the reference variable's lifetime ends when the lifetime of the closure object ends
This is used to capture move-only types with a capture such as x = std::move(x).

This also makes it possible to capture by const reference, with &cr = std::as_const(x) or similar.

int x = 4;
auto y = [&r = x, x = x + 1]()->int
    {
        r += 2;
        return x * x;
    }(); // updates ::x to 6 and initializes y to 25.
(since C++14)
```

