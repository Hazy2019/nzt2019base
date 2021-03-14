---
title: "笔记：一些日常cheatsheet"
date: 2020.12.01T08:26:49+08:00
description: 日常cheatsheet
categories:
  - "DB"
tags:
  - "cheatsheet"
authorbox: true
pager: true
toc: true
sidebar: "right"
---

日常cheatsheet～

- run valgrind for a program

```
valgrind --tool=memcheck --leak-check=full --log-file=leak.log --soname-synonyms=somalloc=NONE <some_exe> [<some_exe_args>]
```

- run tcpdump to capture mysql queries:
```
tcpdump -r /tmp/a.cap -A -S -n -nn  | grep -i -E "select|insert|update|delete|replace" | sed 's%\(.*\)\([.]\{4\}\)\(.*\)%\3%' | less
```



- `tee` with a pipe output to screen and a file
```
echo "hello" | tee abc.txt
```


- ps

- top

- tasr

- sar

<!--more-->
- iostat

- iotop

- iftop

- netstat

- tcpdump

- Makefile

- systemtap

### py scripts snippet
```
#!/usr/bin/python3
# -*- coding: utf-8 -*-
...

if __name__ == "__main__":
   ...
```

### vim
set list
set nolist
noh


- gcc

- others
  - system supervisor
  - system crontab settings
