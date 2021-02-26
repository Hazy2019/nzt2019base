---
title: "智能指针1: shared_ptr使用梳理"
date: 2018-12-01T21:26:49+08:00
description: ""
categories:
  - "c++"
tags:
  - "shared_ptr"
lead: "智能指针" # Lead text
comments: false # Enable Disqus comments for specific page
authorbox: true # Enable authorbox for specific page
pager: true # Enable pager navigation (prev/next) for specific page
toc: true # Enable Table of Contents for specific page
---

本文提及并讨论了：
- `shared_ptr`引入背景
- 删除器
- 线程安全性
- `std::ref`
- 优先使用`make_shared`
- `enable_shared_from_this`
- 观察者模式和event-listener

## 缘起

- 裸指针资源管理内存,容易产生各种内存问题，具体有以下几种类型[1]：
  - 资源未释放，重复释放，free/delete不匹配 ...
  - 越界/段错误 
  > moduo1.7节讨论了裸指针会有哪些问题.

- 不配对的free&delete会有什么问题？
  是未定义行为.可以参考：
  - https://stackoverflow.com/questions/10854210/behaviour-of-malloc-with-delete-in-c
  - https://isocpp.org/wiki/faq/freestore-mgmt

## 基本原理 & 使用

- 需要一个东西来管理裸指针（资源），当没有人引用资源时，自动地释放它.  --- `std::shared_ptr`
- 使用略。

## 删除器
- shared_ptr可以自定义删除器（deleter），用来定义释放行为. 学习到删除器时，有个疑问是其类型在哪里定义的，查看boost的实现如下：
  可以看出，shared_ptr的模板参数只有指针对象的类型T：
  ```
  template<class T> class shared_ptr
  {
  private:

      // Borland 5.5.1 specific workaround
      typedef shared_ptr<T> this_type;

  public:
  ....
  ```

  删除器类型是在构造函数定义中带进来的：
  ```
  template<class Y>
  explicit shared_ptr( Y * p ): px( p ), pn() // Y must be complete
  {
      boost::detail::sp_pointer_construct( this, p, pn );
  }

  //
  // Requirements: D's copy constructor must not throw
  //
  // shared_ptr will release p by calling d(p)
  //
  // 构造函数只需要提供Y作为模板类型参数，
  // D不需要提供，可由构造函数的第二个参数推导得到
  template<class Y, class D> shared_ptr( Y * p, D d ): px( p ), pn( p, d )
  {
      boost::detail::sp_deleter_construct( this, p );
  }
  ....
  ```
  关于删除器的一些情报：
  1. 其类型是一个可调用对象（callable），且接受参数只有一个为Y*(take a parameter of Y*, as shown before⬆️)
  2. 必须是可拷贝的（构造`shared_ptr`时涉及一次删除器的拷贝，如果有的话）
  3. 必须是no throw的

  > 关于可调用对象：
  > - 可调用对象: 包括函数/函数指针/重载了调用运算符的类（Functor）/lambda表达式
  > - 可调用对象统一可用`std::function`来表示其类型

- 利用删除器可以有一些trick，比如实现类似golang的`defer`
  ```
  // some trick

  std::shared_ptr<void> a1(nullptr, [](void*){
        log_info("this is a defer...");
      });

  std::shared_ptr<void> a2(nullptr, [](void*){
        log_info("this is another defer...");
      });
  ```
  运行顺序如下：
  ```
  2016-02-02 06:14:56.255 [thread 704968] info [shared_ptr.cc:65] this is another defer...
  2016-02-02 06:14:56.255 [thread 704968] info [shared_ptr.cc:61] this is a defer...
  ```

  > 栈空间的元素释放顺序：同种类型元素是LIFO的.
  > order of destruction of stack variable: https://stackoverflow.com/questions/14688285/c-local-variable-destruction-order

## 线程安全

- 只有控制块本身是线程安全.（It is only the control block itself which is thread-safe.）

- why accessing  std::shared_ptr should be protected by mutex?
 - https://blog.csdn.net/Solstice/article/details/8547547
 - https://stackoverflow.com/questions/14482830/stdshared-ptr-thread-safety

- 同一个`shared_ptr`可以被多个线程同时读取
- 同一个`shared_ptr`被多个线程同时读写时，需要加锁

------- 

> - moduo1.9节
> - https://www.boost.org/doc/libs/1_75_0/libs/smart_ptr/doc/html/smart_ptr.html#shared_ptr_thread_safety

- `shared_ptr`/`atomic`/`mutex`等传递给`thread`作为其构造函数的参数时，需要用`std::ref`包裹
- 由于多线程同时读写同一个`shared_ptr`需要加锁，需要控制临界区的大小。（资源申请和释放都需要在临界区以外）

```
class App {                                                                       
public:                                                                           
  App() : id_(App::global_id_++) {                                                
    log_info("#{} of App is created!", id_);                                      
  }                                                                               
  ~App() {                                                                        
    log_info("#{} of App is destoried!", id_);                                    
  }                                                                               
  int getid() {                                                                   
    return id_;                                                                   
  }                                                                               
private:                                                                          
  int id_;                                                                        
  static int global_id_;                                                          
};                                                                                
int App::global_id_ = 0;                                                          
using AppPtr = std::shared_ptr<App>;                                              
                                                                                  
void do_something(App *a) {                                                       
  log_info("do #{} ...", (a != nullptr ? a->getid() : -1));                       
}                                                                                 
std::default_random_engine generator;                                             
std::uniform_int_distribution<int> distribution(1,6);                             
void reader(AppPtr& ap, std::mutex &apmtx) {                                        
  log_info("a and a_mtx: {},{}",(void*)(&ap), (void*)(&apmtx));                     
  std::this_thread::sleep_for(std::chrono::milliseconds(distribution(generator)));  
  AppPtr local;                                                                     
  {                                                                                 
    log_info(">>> enter critical");                                                 
    std::lock_guard<std::mutex> l(apmtx);                                           
    local = ap;                                                                     
    log_info("<<< leave critical");                                                 
  }                                                                                 
  do_something(local.get());                                                        
}                                                                                   
void writer(AppPtr& ap, std::mutex &apmtx) {                                        
  log_info("a and a_mtx: {},{}",(void*)(&ap), (void*)(&apmtx));                     
  std::this_thread::sleep_for(std::chrono::milliseconds(distribution(generator)));  
  AppPtr local_old,local_new(new App);                                              
  {                                                                                 
    log_info(">>> enter critical");                                                 
    std::lock_guard<std::mutex> l(apmtx);                                           
    local_old = ap;                                                                 
    ap = local_new;                                                                 
    log_info("<<< leave critical");                                                 
  }                                                                                 
}                                
TEST(sharedptr,threadsafety) {                                                    
  AppPtr a = std::make_shared<App>();                                             
  std::mutex a_mtx;                                                               
  std::thread t1(reader, std::ref(a), std::ref(a_mtx));                           
  std::thread t2(writer, std::ref(a), std::ref(a_mtx));                           
  t1.join();                                                                      
  t2.join();                                                                      
}                                                       
```
运行结果：
```
[thread 705061] info [shared_ptr.cc:113] #0 of App is created!
[thread 705062] info [shared_ptr.cc:134] a and a_mtx: 0x7ffe4fce86e0,0x7ffe4fce86b0
[thread 705063] info [shared_ptr.cc:146] a and a_mtx: 0x7ffe4fce86e0,0x7ffe4fce86b0
[thread 705063] info [shared_ptr.cc:113] #1 of App is created!
[thread 705063] info [shared_ptr.cc:150] >>> enter critical
[thread 705063] info [shared_ptr.cc:154] <<< leave critical
[thread 705063] info [shared_ptr.cc:116] #0 of App is destoried!
[thread 705062] info [shared_ptr.cc:138] >>> enter critical
[thread 705062] info [shared_ptr.cc:141] <<< leave critical
[thread 705062] info [shared_ptr.cc:129] do #1 ...
[thread 705061] info [shared_ptr.cc:116] #1 of App is destoried!
```
## make_shared
老生常谈了，再简要总结下：
- 效率：
使用`auto x = std::make_shared<type>(xx1,xx2,xx3);`会比使用`std::shared_ptr x(new type(xx1,xx2,xx3));`:
减少1次堆内存的申请.
后者需要申请1次type类型本身对象，和shared_ptr本身对象（控制块）2次.
- 原理：
两次new，第一次申请type+控制块大小的一片内存，第二次利用`placement new`，把type类型数据构造在指定的内存地址。
- 缺陷：
如果有`weak_ptr`引用了使用`make_shared`申请出来的智能指针对象，那么其生命周期会被`weak_ptr`延长，原因是"控制块"的生命周期等于`weak_ptr`的生命周期。

  
> https://stackoverflow.com/questions/20895648/difference-in-make-shared-and-normal-shared-ptr-in-c
> https://blog.csdn.net/SuWanWorld/article/details/103940013
> https://www.cnblogs.com/leijiangtao/p/12046333.html

## enable_shared_from_this

使用智能指针还有个问题：就是任何`this`指针不能交给`shared_ptr`管理，会导致double-free,如：

```
class App2 : public App {
  public:
    std::shared_ptr<App2> App2Fuck() {
      std::shared_ptr<App2> x(this); // would cause this to be destoried twice!
      return x;
    }
};
```
那如果强行需要在类的内部返一个`shared_ptr`出来，c++提供了`enable_shared_from_this`来做这个事（最初是boost实现的，后来被合进c++11了）。

上面这个例子毫无实用价值，具体是什么场景需要用到这个，我将在另一篇文里讨论。（或check：muduo 1.11节）

- HOWTO： https://stackoverflow.com/questions/712279/what-is-the-usefulness-of-enable-shared-from-this

## Reference
  - https://stackoverflow.com/questions/10854210/behaviour-of-malloc-with-delete-in-c
  - https://isocpp.org/wiki/faq/freestore-mgmt
  - order of destruction of stack variable: https://stackoverflow.com/questions/14688285/c-local-variable-destruction-order
  - https://www.boost.org/doc/libs/1_75_0/libs/smart_ptr/doc/html/smart_ptr.html#shared_ptr_thread_safety
  - https://stackoverflow.com/questions/712279/what-is-the-usefulness-of-enable-shared-from-this
  - muduo 1.11
