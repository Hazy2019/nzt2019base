---
title: "digest of 5.25"
date: 2021-05-30
categories:
 - "other"
tags:
 - "digest"
pager: true
sidebar: "right"
---


图数据库综述 RENZO ANGLES and CLAUDIO GUTIERREZ. Survey of graph database models[J]. ACM Computing Surveys, Vol. 40, No. 1, Article 1, Publication date: February 2008. 
about rocksdb's BloomFilter: https://github.com/facebook/rocksdb/wiki/RocksDB-Bloom-Filter
whole_key_filtering --> false的副作用
check usage：std::enable_if_t .  std::decay_t 
check usage：folly::Future
<!--more-->
+ basic usage --done
+ https://wanghenshui.github.io/2020/11/01/future-promise.html
rocksdb's SeekForPrev
fbthrift
future_xxxx   return一个future给框架（src/service/GraphService.cpp:91），然后框架做了啥？

next： executor & fiber concept
https://stackoverflow.com/questions/1208028/significance-of-a-inl-file-in-c
rocksdb's eventlistener
c++ virtual function recall: https://stackoverflow.com/questions/2391679/why-do-we-need-virtual-functions-in-c
c++ vtable impl. `late binding`
pure virtual function
virtual function design pattern: effective c++ 170page-
non virtual interface(NVI) pattern, strategy pattern

std::move does not move things. recall>
/////from comments in folly::MPMCQueue
/// One of the common usages of this method is to enqueue via the
/// move constructor, something like q.write(std::move(x)).  If write
/// returns false because the queue is full then x has not actually been
/// consumed, which looks strange.  To understand why it is actually okay
/// to use x afterward, remember that std::move is just a typecast that
/// provides an rvalue reference that enables use of a move constructor
/// or operator.  std::move doesn't actually move anything.  It could
/// more accurately be called std::rvalue_cast or std::move_permission.
+ for example，std::unique_ptr 被move时，到底move了啥？
std::mutex & std::condition_variable 
std::find_if:https://github.com/vesoft-inc/nebula-storage/pull/463
[[noreturn]] https://stackoverflow.com/questions/10538291/what-is-the-point-of-noreturn
modules/storage/src/kvstore/raftex/RaftPart.cpp:1650
"Stale log! Local lastLogId......

gflag使用
debug by systemtap: how to access user space global variables
debug by gdb:
oom问题，vmtouch。
如何run单机版本？
检查meta_server_addrs参数相关的代码，发现注释中说明了如果这个参数为“”，则说明为单机版。
类似以下，gflag指定下一个参数，可覆盖掉配置文件中的配置，如下则覆盖meta_server_addrs为‘’。
/data/weijian.yang/WORKSPACE/nebula-graph-output/bin/nebula-metad --flagfile /data/weijian.yang/WORKSPACE/nebula-graph-output/running_dir/service-meta/nebula-metad-0.conf --meta_server_addrs ''

roadmap：
graphd ---almost(60%)
metad
storaged

storage-perf: a perf tool for storage
detail:
folly::Baton
StatusOr
std::enable_if_t
create space的PlanNode是什么类型的？盲猜PlanNode::Kind::kPassThrough
createspace执行路径/数据视图
tag
index
fulltext index
vertex
edge
folly::SharedMutex::WriteHolder
check precompile header:
from rocksdb/build_tools/build_detect_platform
640 $CXX $PLATFORM_CXXFLAGS $COMMON_FLAGS -x c++ - -o /dev/null 2>/dev/null <<EOF
641   #include <cstdint>
642   int main() {
643     uint64_t a = 0xffffFFFFffffFFFF;
644     __uint128_t b = __uint128_t(a) * a;
645     a = static_cast<uint64_t>(b >> 64);
646     (void)a;
647   }
648 EOF

 __attribute__ ((format (printf, x, y))) inside a class
https://stackoverflow.com/questions/11621043/how-should-i-properly-use-attribute-format-printf-x-y-inside-a-class

logging in nebula-graph
parser:
using flex and bison
https://pandolia.net/tinyc/ch13_bison.html
nGQL:
data model
concept:
tag/edge


CreateSpace：
   1. SpaceId生成规则是什么？
   2. Space/Part/Zone/Group/etc...的逻辑关系是什么？
   3. CreateSpace的kv编码，Raft层的kv编码？
   4. RaftPart::appendLogAsync中的三种future有什么区别？
switch (logType) {
    case LogType::ATOMIC_OP:
        retFuture = cachingPromise_.getSingleFuture();
        break;
    case LogType::COMMAND:
        retFuture = cachingPromise_.getAndRollSharedFuture();
        break;
    case LogType::NORMAL:
        retFuture = cachingPromise_.getSharedFuture();
        break;
}
  5. RaftPart::appendLogAsync的replicate日志无法并发or排队？（相关： check一下rocksdb的wal在并发时怎么处理的？write-pipeline/proxy batch）
658         if (replicatingLogs_.compare_exchange_strong(expected, true)) {
659             // We need to send logs to all followers
660             VLOG(2) << idStr_ << "Preparing to send AppendLog request";
661             sendingPromise_ = std::move(cachingPromise_);
662             cachingPromise_.reset();
663             std::swap(swappedOutLogs, logs_);
664             bufferOverFlow_ = false;
665         } else {
666             VLOG(2) << idStr_
667                     << "Another AppendLogs request is ongoing, just return";
668             return retFuture;
669         }
  6. 静态哈希分片
970 StatusOr<PartitionID> MetaClient::partId(int32_t numParts, const VertexID id) const {
971     // If the length of the id is 8, we will treat it as int64_t to be compatible
972     // with the version 1.0
973     uint64_t vid = 0;
974     if (id.size() == 8) {
975         memcpy(static_cast<void*>(&vid), id.data(), 8);
976     } else {
977         MurmurHash2 hash;
978         vid = hash(id.data());
979     }
980     PartitionID pId = vid % numParts + 1;
981     CHECK_GT(pId, 0U);
982     return pId;
983 }
    7. 几个语句执行[数据视图]
create space basketballplayer(partition_num=10,replica_factor=1,vid_type=fixed_string(32));
create tag player(name string,age int);
create tag team(name string);
insert vertex player(name,age) values "player100":("Tim Duncan", 42);
    8. systemtap 打印context variable的内容
EXPR$ expands to a string with all of $EXPR's members, equivalent to
       sprintf("{.a=%i, .b=%u, .c={...}, .d=[...]}",
                $EXPR->a, $EXPR->b)
$EXPR$$
       expands to a string with all of $var's members and submembers, equivalent to
       sprintf("{.a=%i, .b=%u, .c={.x=%p, .y=%c}, .d=[%i, ...]}",
               $EXPR->a, $EXPR->b, $EXPR->c->x, $EXPR->c->y, $EXPR->d[0])
man stapprobes
9. systemtap打印调用栈
  print_ubacktrace  + addr2line 可以定位到函数位置v  http://baotiao.github.io/2017/06/14/systemtap-tips-and-example/
通过sudo stap call_trace.stp | c++filt 将每次调用WriteToWAL函数的调用栈打印出来。这里如果编译rocksdb的时候采用demangle的方式，那么就不需要c++filt了， 否则会出现一些乱码，这里使用c++filt进行过滤。  https://blog.csdn.net/Z_Stand/article/details/108137659


[dev env]
stap安装
-----
1. check your system
lsb_release -a
uname -r
2.prerequisites: kernel-debuginfo
wget http://kojipkgs.fedoraproject.org//vol/fedora_koji_archive04/packages/kernel/5.0.9/301.fc30/x86_64/kernel-debuginfo-5.0.9-301.fc30.x86_64.rpm
wget https://kojipkgs.fedoraproject.org//vol/fedora_koji_archive04/packages/kernel/5.0.9/301.fc30/x86_64/kernel-debuginfo-common-x86_64-5.0.9-301.fc30.x86_64.rpm
3. run check: stap-prep
4. run test: sudo stap -v -e 'probe vfs.read {printf("read performed\n"); exit()}'

rpm cheat-sheet
------
查询包：rpm -q <package>
卸载包：rpm -e <package>
安装包：rpm -ivh <package-file>.rpm

[build nebula - cmake notes]
```
macro(nebula_fetch_module)
set(module_dir ${CMAKE_SOURCE_DIR}/modules/${module_NAME})
...
execute_process(COMMAND  ${GIT_EXECUTABLE} clone --single-branch --branch ${module_TAG} ${module_URL} 	${module_dir}  RESULT_VARIABLE fetch_status ERROR_VARIABLE ERROR_MESSAGE)
...
endmacro()
```

git subcommands：
  clone --single-branch --branch ${module_TAG} ${module_URL}  ${module_dir} 
  rev-parse --abbrev-ref HEAD
  remote set-branches origin --add
  config remote.origin.fetch
  fetch

build configs
-fPIC abi
  
common
*.thrift

third-party:
download and run: vesoft-third-party-2.0-x86_64-libc-2.27-gcc-8.3.0-abi-11.sh (a tar archive included, "fbthrift1" executable is here.. )

summary：
cmake will: 
1. git-clone nebula-* to local directories, i.e. modules/common, modules/storage
2. thrift targets: *_thrift_generator from ../modules/common/cmake/ThriftGenerate.cmake
