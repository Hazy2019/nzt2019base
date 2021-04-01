---
title: "parameter pack和递归模板展开"
date: 2021-03-24
categories:
 - "c++"
tags:
 - "parameter_pack"
 - "template"
pager: true
sidebar: "right"
---


## 需求

做一个libevent的wrapper，有个需求，用户对某个fd的可读事件感兴趣，要求在产生这个事件时，调用他传入的某个可调用对象及其参数。
libevent的回调类似：`void LibeventCallback(int fd, short flag, void* arg);`

要求：
1、用户传入的可调用对象fn，拿的参数是可变的，第一个参数为某个特定类型，用于感知fd和flag，后续其他为用户自定义参数
<!--more-->
2、wrapper需要对fn做编译期检查，如果用户传进来参数不合法，编译期给出明确错误信息

## 实现

1. 毫无疑问第一反映是需要用到template的`parameter pack`. 
2. 需要用一些类型萃取和static_assert来做fn类型合法性检查.
3. 由于需要调用的东西是用户自定义参数，这里又需要用到完美转发，否则对于const、非const或某些右值类型又没法搞

4. 实现过程中发现，需要一个结构来存储这些可变的parameter pack，没错，就是tuple
5. 继续，发现如何把一个tuple给展开作为参数列表传给回调又是个大问题，这里需要参考附录里的第3个链接。
  1. c++11中没有std::apply,所以需要自己写一个..
  2. 具体怎么展开一个tuple呢？这里又需要用到递归模板展开..傻了吧.(PS: c++14之后有`std::integer_sequence`可以用)
  3. 获取一个parameter pack的参数个数：[sizeof...](https://en.cppreference.com/w/cpp/language/sizeof...)

## 实现
一个非最终版本的实现如下：
```cpp

namespace tuple_unpack_helper {
// for c++11
template<int... Is>
struct index {};

template<int N, int... Is>
struct gen_seq : gen_seq<N - 1, N - 1, Is...> {};

template<int... Is>
struct gen_seq<0, Is...> {
  typedef index<Is...> type;
};

template<typename Fn, typename... Args>
struct callable {
  callable(Fn &&f, Args &&... a)
      : fn(std::forward<Fn>(f)), params(std::forward<Args>(a)...) {}
  std::function<void(Args...)> fn;
  std::tuple<Args...> params;
  void call() {
    return callFunc(
        typename gen_seq<sizeof...(Args)>::
            type{}); // sizeof... to fetch parameter size of a parameter pack
  }
  template<int... S>
  void callFunc(index<S...>) {
    fn(std::get<S>(params)...); // parameter unpack --> fn(std::get<0>(params),
                                // std::get<1>(params), ...);
  }
};
template<typename Fn, typename... Args>
callable<Fn, Args...> make_callable(Fn &&callback, Args &&... params) {
  return callable<Fn, Args...>(std::forward<Fn>(callback),
                               std::forward<Args>(params)...);
}
// for c++14, we can use std::integer_sequence instead
// for c++17, we can use std::apply or std::invoke instead
} // namespace tuple_unpack_helper

short PersisReadableFlags() { return EV_PERSIST | EV_READ | EV_TIMEOUT; }
short PersisWritableFlags() { return EV_PERSIST | EV_WRITE | EV_TIMEOUT; }

template<class Callable>
class InternalEvent {
public:
  InternalEvent(struct event_base *base, int fd, short flags)
      : ev_base_(base), fd_(fd), flags_(flags), ev_(nullptr) {
    if (ev_base_ != nullptr) {
      ev_ = event_new(ev_base_, fd_, flags_,
                      InternalEvent<Callable>::LibeventCallback, this);
    }
  }
  ~InternalEvent() {
    if (ev_) {
      event_free(ev_);
    }
  }
  bool Enable(const struct timeval *tv = nullptr) {
    int rc = event_add(ev_, tv);
    return rc == 0;
  }

  bool Disable() {
    int rc = event_del(ev_);
    return rc == 0;
  }

private:
  struct event_base *ev_base_;
  int fd_;
  short flags_;
  struct event *ev_;
  static void LibeventCallback(int fd, short flag, void *arg);
};

template<class Callable>
void InternalEvent<Callable>::LibeventCallback(int fd, short flags, void *arg) {
  InternalEvent<Callable> *p = reinterpret_cast<InternalEvent<Callable> *>(arg);
  static_cast<Callable *>(p)->Trigger(fd, flags);
}

// Fn must be like:
//   Fn (int, short, Args args...)
//
template<typename Fn, typename... Args>
class CallableEvent : public InternalEvent<CallableEvent<Fn, Args...>> {
private:
  using internalevent = InternalEvent<CallableEvent<Fn, Args...>>;
  using signature = void(int, short, Args...);
  static_assert(std::is_convertible<Fn &&, std::function<signature>>::value,
                "wrong signature");

  std::function<signature> ufn_; // user callback
  std::tuple<Args...> uargs_;    // user function
public:
  //
  // call this means I am interesting with @fd 's @flags events, if that happens,
  // tell me by calling `fn(fd, flags, args...)`
  //

  CallableEvent(struct event_base *base, int fd, short flags, Fn &&fn,
                Args &&... args)
      : internalevent(base, fd, flags), ufn_(std::forward<Fn>(fn)),
        uargs_(std::forward<Args>(args)...) /*parameters unpack*/ {}

  CallableEvent(const CallableEvent<Fn, Args...> &) = delete;
  CallableEvent(CallableEvent<Fn, Args...> &&) = delete;

  void Trigger(int fd, short flags) {
    call_user_callback(
        fd, flags,
        typename tuple_unpack_helper::gen_seq<sizeof...(Args)>::type{});
  }

private:
  template<int... S>
  void call_user_callback(int fd, short flags,
                          tuple_unpack_helper::index<S...>) {
    // before user callback is called...
    //
    ufn_(fd, flags, std::get<S>(uargs_)...);
    // after user callback is called...
    //
  }
};

template<typename Fn, typename... Args>
std::shared_ptr<CallableEvent<Fn, Args...>> make_CallableEvent(struct event_base *base, int fd,
                                              short flags, Fn &&f,
                                              Args &&... args) {
  return std::make_shared<CallableEvent<Fn, Args...>>(base, fd, flags, std::forward<Fn>(f),
                                    std::forward<Args>(args)...);
}
```

如何使用见以下，感觉还是很简易的。

```
TEST(template_check, tuple_unpack) {
  auto f1 = [](int a, int b, int c, int d) {
    log_info("called! {}-{}-{}-{}", a, b, c, d);
  };
  auto c = tuple_unpack_helper::make_callable(f1, 1, 2, 3, 4);
  c.call();
}

 TEST(template_check, CallableEvent) {
   auto c = make_CallableEvent(
       nullptr, 0, 0,
       [](int fd, short flags, int a, int b) {
         log_info("it happened! {},{}", a, b);
       },
       10, 20);
   c->Trigger(0, 0);
 }

 TEST(template_check, libevent) {
   struct event_base *evbase = event_base_new();
   int calltimes = 0;
   auto e = make_CallableEvent(
       evbase, 0 /*stdin*/, PersisReadableFlags(),
       [](int fd, short flags, int &calltimes) {
         char letter;
         int n = read(fd, &letter, 1);
         log_info("fd={}, caught event={}, calltime={}, letter={:#x}", fd, flags,
                  calltimes, letter);
         calltimes++;
       },
       calltimes);

   e->Enable();
   event_base_dispatch(evbase);
 }
```

## 附

- 附：[parameter pack cppref](https://en.cppreference.com/w/cpp/language/parameter_pack)

- 附1：参考 definition of `std::thread` shown as below:
```
template< class Function, class... Args >
explicit thread( Function&& f, Args&&... args );
```

- 附2：参考几个StackOverflow的问题：

  1. [check-template-argument](https://stackoverflow.com/questions/47698552/how-to-check-if-template-argument-is-a-callable-with-a-given-signature)
  2. [function-signature](https://stackoverflow.com/questions/26792750/function-signatures-in-c-templates)
  3. [store-template-pack](https://stackoverflow.com/questions/16868129/how-to-store-variadic-template-arguments)
  4. [unpack-a-tuple](https://stackoverflow.com/questions/7858817/unpacking-a-tuple-to-call-a-matching-function-pointer)
