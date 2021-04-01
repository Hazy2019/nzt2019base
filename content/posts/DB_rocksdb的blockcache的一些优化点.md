---
title: "rocksdb的blockcache的一些优化点"
date: 2021-03-26
categories:
 - "DB"
tags:
 - "rocksdb"
 - "blockcache"
pager: true
sidebar: "right"
---

# 引子

记一些突然间的想法，防止后续忘了，以下是正文。


# blockcahe的问题

rocksdb的blockcache目前遇到的，主要有：

1. 官方实现中没有回收机制.
  
<!--more-->
因为线上存在一些slave实例，默认不对外提供服务（有些集群允许slave读），某些节点从主切为从之后，blockcache会一直占用。
这就造成了线上机器的内存资源可能在被slave占用，但又不提供服务，造成内存浪费，亟需资源的master有时却没有足够的内存使用。
据统计，在日常内存水位报警较多的机器上，slave持有了近20%-30%的内存用量。

2. 官方实现在5.7之前blockcache的用量统计是不准确的，没有把handler计入。

这个问题就造成了内存时常用超的问题，比如配置了10GBblockcache，但最终发现该进程的内存使用达到15GB甚至20GB。


对于以上两点，我们做过一些尝试：1. 计算内存更准确一些。2.定期回收blockcache中lru链表表尾部分的一些元素。这也是很多其他厂的方案。


3. 再进一步，blockcache在我们的使用场景下也会存index和filter，也就是开启所谓的`cache_index_and_filter_blocks`选项. 由于
blockcache是sharding的，每个shard由一个锁来保护，为了降低锁竞争的概率，一种做法就是加大shard数。但在总大小确定的情况下，
shard数越大，每个shard的可允许用量越小，对于block较大的场景下（较大的sstable的index块和filter块），每个shard可承载的block数很小。
造成换入换出严重。极端场景下，blockcache将无法cache超大index块，导致的现象就是进程内存持续地没有吃上来，但端到端耗时达到百毫秒级别。

对于上述这点，官方有个尝试，就是所谓的partition metadata方案[1]，这个方案希望把sst内的大的index块和filter块拆分为小块。
附1：[partition-metadata](https://github.com/facebook/rocksdb/blob/5.17.fb/include/rocksdb/table.h#L175-L180)
附2：sstable的格式（默认）
```
<beginning_of_file>
[data block 1]
[data block 2]
...
[data block N]
[meta block 1: filter block]                  (see section: "filter" Meta Block)
[meta block 2: index block]
[meta block 3: compression dictionary block]  (see section: "compression dictionary" Meta Block)
[meta block 4: range deletion block]          (see section: "range deletion" Meta Block)
[meta block 5: stats block]                   (see section: "properties" Meta Block)
...
[meta block K: future extended block]  (we may add more meta blocks in the future)
[metaindex block]
[Footer]                               (fixed size; starts at file_size - sizeof(Footer))
<end_of_file>
```
可以看到sst的index block和filter block只有1个，通过sst_dump可以查看sst的index和filterblock的大小，我们可以发现当sst大小为256MB或512MB时，这两个块大小可能达到30-50MB的级别,如果shard数
设置太大，导致单shard小于这个大小，就会有问题。

另外这个问题也可通过控制sst的大小来解决：target_file_size_base = xxx（如64MB），target_file_size_multiplier=xxx（如1）。

4. 再再再进一步，因为lsm都是异地更新的，生成的sst都是只读的，一旦compact完成，compact的源sst就属于废弃版本了，但这些sst的block可能还留存在blockcahce里。可能造成一些资源浪费。

这个问题可以通过compact后新生成的sst预取到blockcache中来解决，但又有个问题就是如果任意的sst都预取也不太好，因为你不知道新生成的sst哪些是可能在将来会被读到的。上层业务完全可能是只写（或大量写）业务，
少量读，对于这种业务，用这个预取策略又可能造成blockcahe被填满，但其实业务并不需要读（解决办法比较粗暴的就是设置小一点的blockcache）。

总结一下第4个问题，我们需要：1. compact后的stale block稍快速点地被逐出。 2.compact后的新block按需加载到blockcache中。这两点做起来其实不难，其中第2点在[x-engine的paper](https://dl.acm.org/doi/pdf/10.1145/3299869.3314041)里似乎有提到。

附3.1：Varint64编码
```
每个byte的第1个bit用于标识是否结束(1-还没结束， 0-结束)。后续7个bit为payload。
对于小一点的数字，可以节省bytes数。但对于大的数字则需要更多bytes数存储，例如full 64bit的数据需要10Bytes。
```

附3.2：cachekey长什么样子？
```
基于rocksdb-v6.15：*PosixHelper::GetUniqueIdFromFile*/*BlockBasedTable::GetCacheKey*
1个block的cachekey分2部分，第一部分是prefix（长度为3*max-len-of-varint64+1）,第二部分是该block在sst内的偏移
1. 在posix-env下，prefix编码如下：
 rid = EncodeVarint64(rid, buf.st_dev); // 所在sst文件的st_dev
 rid = EncodeVarint64(rid, buf.st_ino); // 所在sst文件的st_ino
 rid = EncodeVarint64(rid, uversion);   // 所在sst文件的inode版本号，通过*ioctl FS_IOC_GETVERSION*获取
2. 接着再追加添加一个varint64
 EncodeVarint64(cache_key + cache_key_prefix_size, handle.offset())
```
基于附3.2，我们可以有办法得知compact相关的stale block和generated block是否在blockcache中。当然这样直接去请求blockcahe会增加一些锁开销的。还可以进一步优化。后招天马行空，就先不讨论了。


# 总结

blockcache存在的一些问题：

1. blockcache没有回收
2. blockcache用量统计不准确
3. blockcache的sharding方案对于大block不友好
4. compact的源SST的block可能还残留在blockcache中（只会在blockcache满了之后lazy地被逐出），但同时新生成的sst的block又不会「智能地」预取到blockcache中，造成资源浪费.
