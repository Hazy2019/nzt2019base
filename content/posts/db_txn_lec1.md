---
title: "db笔记 - 事务1:隔离级别"
date: 2021-02-14
description: "事务"
categories:
  - "DB"
tags:
  - "txn"
authorbox: true
pager: true
toc: true
sidebar: "right"
---

## 锁

read lock
write lock
long duration lock
short duration lock
<!--more-->
predicate lock


## history

SQL-92 --> SQL-95:

## an overview of isolation degree

- P0(Dirty Write)

- Read Uncommited

- P1(Dirty Read)

- Read Commited

- P4C(Lost Update of Cursor)

- Cursor Stability

- P4(Lost Update)

- P2(Non-Repeatable Read)

- Repeatable Read

- P3(Phantom)

- Serializable

- Snapshot Isolation(Sql-95)

- Serializable Snapshot Isolation（SSI-08)

## 读写偏序问题（Read/Write Skew）


## References
- [A Critique of ANSI SQL Isolation Levels 阅读笔记](https://zhuanlan.zhihu.com/p/187597966)
- [Sql-95:A Critique of ANSI SQL Isolation Levels](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-95-51.pdf)
- [DB2 隔离级别](https://blog.csdn.net/huaxin520/article/details/8312875)
- [再谈数据库事务隔离性](https://www.cnblogs.com/ivan-uno/p/8274355.html)
- [SSI-08] Michael J. Cahill, Uwe Röhm, and Alan D.Fekete. 2008. Serializable isolation for snapshot databases. In SIGMOD ’08:Proceedings of the 2008 ACM SIGMOD international conference on Management of data, pages 729–738, New York, NY, USA. ACM.
