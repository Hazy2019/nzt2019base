---
title: "分布式笔记 - Raft(入门)"
date: 2017-04-19T21:20:49
description: “raft算法深入"
categories:
  - "分布式"
tags:
  - "分布式"
menu: main
authorbox: true # Enable authorbox for specific page
pager: true # Enable pager navigation (prev/next) for specific page
toc: true # Enable Table of Contents for specific page
mathjax: true # Enable MathJax for specific page
sidebar: "right" # Enable sidebar (on the right side) per page
widgets: # Enable sidebar widgets in given order per page
  - "search"
  - "recent"
  - "taglist"
resources:
- name: "12"
  src: "12.png"
---


### Q&A
##### 线性一致性？
个人认为，分布式系统的一致性与多核内存模型中涉及的一致性异曲同工，所以分布式系统的线性一致性我认为可以参考类似多核系统的线性一致性定义来理解。

##### `fsm: finite-state-machine`
个人理解为有状态分布式服务的每个独立实例（进程+数据），本质上都可以是个有限状态机（fsm）
一个存储服务往往采用分片方式来横向扩容，每个分片中采用多个实例来保证高可用，这些实例某种程度上是一致的，可以称为replicated fsm.

##### `log entry`和`log`分别是？
所有写入日志称为`log`
某条写入日志称为`log entry`

##### `commit`和`apply`分别指什么？
`a log entry is committed`是指某条log已被确认到达大多数节点.
`a log is applied`是指某条日志已被`fsm`执行.

##### leader回应client的时间点？
一个日志的生命周期主要有几个时间点：
 * leader本地写入log成功
 * 被leader标记为commited
 * 被leader标记为applied
 
论文的$5.3节说明，在applied之后(fsm执行后才能拿到结果)才将结果返回至client.
>When the entry has been safely replicated (as described below), the leader applies the entry to its state machine and returns the result of that execution to the client.

##### <span id="request_vote_param_myth">RPC-RequestVote</span>里，为什么带了最后一个日志项（log entry）的下标和它的term（而不是commitIndex或applyIndex对应的日志项）

##### voteFor如何维护的？（例如: 什么时候重置为null? 当`follower`grant了某个候选者之后，voteFor如何处理？）
这个问题论文里并没有具体进行讨论（可能只是个实现细节，没有讨论的必要）


##### currentTerm如何维护的？（例如：在选举阶段，当`follower`grant某个候选者之后，是否需要修改自己的currentTerm? 如果选举阶段不修改，那么连续两次选举（上一次SplitVote）如何处理？）

##### 只需要放写操作进raft-log吗？
直觉上，读操作并不会改变fsm的状态，所以(在没check论文前)个人感觉上<sup>待验证</sup>，只需要保证读leader的即可保证强一致（线性一致性），从某个follower读则是最终一致

<sup>[2]</sup>中有专门一章讨论只读优化问题。



### raft算法描述

#### 每个节点维护的上下文 
```
Log {
    LogEntry ent[];
    bool IsNewerThan(const Log &other_log);
}

LogEntry {
  int   term;
  Cmd   command;
}

Ctx {
  Log                                log;
  int                                currentTerm;  
  ServerId                           voteFor;
  
  ServerId                           selfId;
  ENUM {FOLLOWER, CANDIDATE, LEADER} state;
  
  uint                               commitIndex;
  uint                               lastApplied;

  ServerId                           clusterMap[];

  uint                               nextIndex[];
  uint                               matchIndex[];
}

```


#### leader选举
* 触发：
  在`election-timeout`时间内没收到leader的`RPC-AppendEntries`
  <br />
  >`election-timeout`是某范围内的随机时间，用于防止多个follwer同时发起选举造成split vote(没人赢得选举).

* 怎么做：

  - 选举发起方：
    ```
    1.   ctx.currentTerm += 1
    2.   ctx.state = CANDIDATE
    3.   ctx.voteFor = ctx.selfId
    
    4.1. resVote = {}
    4.2. for i in ctx.clusterMap {
            resVote[i] = RPC-RequestVote(
                ctx.currentTerm, 
                ctx.selfId, 
                "last log entry's index",   // [why？](#request_vote_param_myth)
                "last log entry's term"     // [why？](#request_vote_param_myth)
                ) --> i
        }
    4.3. reset `election-timeout` timer

    5. before `election-timeout` reached: 
        5.1 if majority of resVote is True:  // I'm winning the election!
                ctx.state = LEADER
                re-initialize ctx.nextIndex[] and ctx.matchIndex[]: 
                    ctx.nextIndex[]  <-- "last log entry's index" + 1
                    ctx.matchIndex[] <-- 0
                for i in ctx.clusterMap {
                }
        5.2 if RPC-RequestVote is recvieved:  // 论文里没单独讨论,以下为个人推断，需验证
                reply False because ctx.state != FOLLOWER 

        5.3 if RPC-AppendEntries is recvieved:
                if RPC is valid:
                else:
    
        5.4 if `election-timeout` is triggered:
                goto `1` to restart election.
    ```
  - Log的新旧程度（which log is more up-to-date）比较方式：
    ```
    bool Log::IsNewerThanOrEqual(const Log &otherlog) {
        if this->last_log_entry.Term > otherlog->last_log_entry.Term:
            return True;
        else if this->last_log_entry.Term == otherlog->last_log_entry.Term:
            if this->last_log_entry.Index > this->last_log_entry.Index:
                return True;
        return False; 
    }       
    ```
    
  - `RPC-RequestVote`接收方：
    ```
    如果满足：
      ctx.state == FOLLOWER                                                     &&
      ctx.currentTerm <= `term of "RPC-RequestVote"`                            &&
      ctx.voteFor == NULL or ctx.voteFor == `candidateId of "RPC-RequestVote"`  && 
      `candidateId of "RPC-RequestVote"`'s log IsNewerThanOrEqual ctx.Log
    那么:
      返回GrantVote
      ==> 接收方是否需要修改voteFor/currentTerm? //论文里没给出具体细节和讨论，需要查看实现
    ```

    <br/>

    - voteFor和currentTerm在这里的维护方式并没有给出，可能不是特别重要，属于实现细节，仅需满足以下这个即可。个人倾向于currentTerm需在Grant Vote时也更新为candidateId的term，否则如果出现split-vote，下一次选举就没法进行了<sup>待验证</sup>。
      > Each server will vote for at most one candidate in a given term.
- 选举策略的安全性
    
#### log复制
- RPC-AppendEntries 方向
    leader      --> follower 
    leader      --> candidate
    new leader  --> old leader
- 触发
    leader定期发起.(即使没有新的写入，也需要发送空包到follower，避免follower发起选举)

- 日志项匹配性质：
    - 两个日志项的term和index相同，就认为这两个日志项一致（或称之为“相同”`the same`）。
    - 若两份日志内某个日志项一致，那么在该日志项之前的所有日志项也一致。

- 日志冲突的处理原则：
    - 日志冲突的定义：某个日志项的index相同，但term却不同。
    - 以leader的日志为准，最终达到的效果：follower找到自己日志里最后一个与leader相匹配的日志项（其index记为l1），清除掉在其之后的所有日志项，leader最后一个日志项index记为l2, follower将从leader拷贝[l1+1,l2]的日志项。

- 怎么做
    - leader:
        ```
        for each x in followers:
            选取一定范围内的日志（nextIndex）： collect log-entries between (nextIndex[x],my last log-entry]

            RPC-AppendEntries(
                currentTerm,
                leaderId,
                prevLogIndex,  // log index of the log which is right before log-entries[0]
                prevLogTerm,   // log term of the log which is right before log-entries[0]
                log-entries[], // 
                leaderCommit   // to tell the follower which log is ok-to-apply 
            )
        ```
- 收到后的行为：
    - follower:
        - 收到一个RPC-AppendEntries，找到自己日志中的prevLogIndex所在日志项，check下是否匹配，若不匹配或不存在，返回false,leader将回退nextIndex进行回溯。
        
        - 减少follower因日志项部匹配拒绝RPC的次数的优化：

        {{< figure src="../../resources/12.png" title="s0-leader s4-follower" >}}

    - `candidate`/`old leader`在收到一个合法RPC-AppendEntries后，还涉及角色状态的转换。


- 
### 

### 要点总结
- 日志项匹配性质（Log Matching Property）
    - If two entries in different logs have the same index
and term, then they store the same command.
    - If two entries in different logs have the same index
and term, then the logs are identical in all preceding
entries.


### 引用
[1] raft小论文: In Search of an Understandable Consensus Algorithm

[2] CONSENSUS: BRIDGING THEORY AND PRACTICE