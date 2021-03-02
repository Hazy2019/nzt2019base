---
title: "db笔记 - sse"
date: 2021.01.03T08:26:49+08:00
description: "sse"
categories:
  - "DB"
tags:
  - "sse"
  - "compile flags"
authorbox: true
pager: true
toc: true
sidebar: "right"
---

## background

>we would set env var `USE_SSE=1` when compiling Rocksdb, OTHERWISE it would always failed 
at linking stage where encountering errors of lack of some instructions such as:
`no such instruction: `shlx %rdx,%rax,%rax'`.
>but what the fuck is USE_SSE ?

<!--more-->
## compile rocksdb

`USE_SSE` is used to set some gcc flags, see what `/build_tools/build_detect_platform` says:

```
457 if test "$USE_SSE"; then
458   COMMON_FLAGS="$COMMON_FLAGS -msse4.2 -std=c++11"
459 elif test -z "$PORTABLE"; then
460   if test -n "`echo $TARGET_ARCHITECTURE | grep ^ppc64`"; then
461     # Tune for this POWER processor, treating '+' models as base models
462     POWER=`LD_SHOW_AUXV=1 /bin/true | grep AT_PLATFORM | grep -E -o power[0-9]+`
463     COMMON_FLAGS="$COMMON_FLAGS -mcpu=$POWER -mtune=$POWER "
464   elif test -n "`echo $TARGET_ARCHITECTURE | grep ^s390x`"; then
465     COMMON_FLAGS="$COMMON_FLAGS -march=z10 "
466   elif [ "$TARGET_OS" != AIX ] && [ "$TARGET_OS" != SunOS ]; then
467     COMMON_FLAGS="$COMMON_FLAGS -march=native "
468   fi
469 fi
```

## wtf is `sse`?

>SSE is an SIMD (Single Instruction Multiple Data) extension to the x86 instruction set which is used in PC computers, developed by Intel corporation.

- some gcc options:
```
-msse
-msse2
-msse3
-mssse3
-msse4
-msse4a
-msse4.1
-msse4.2
...
```
> These switches enable the use of instructions in the MMX, SSE, SSE2, SSE3, SSSE3, SSE4, SSE4A, SSE4.1, SSE4.2, AVX, AVX2, AVX512F, AVX512PF, AVX512ER, AVX512CD, AVX512VL, AVX512BW, AVX512DQ, AVX512IFMA, AVX512VBMI, SHA, AES, PCLMUL, CLFLUSHOPT, CLWB, FSGSBASE, PTWRITE, RDRND, F16C, FMA, PCONFIG, WBNOINVD, FMA4, PREFETCHW, RDPID, PREFETCHWT1, RDSEED, SGX, XOP, LWP, 3DNow!, enhanced 3DNow!, POPCNT, ABM, ADX, BMI, BMI2, LZCNT, FXSR, XSAVE, XSAVEOPT, XSAVEC, XSAVES, RTM, HLE, TBM, MWAITX, CLZERO, PKU, AVX512VBMI2, GFNI, VAES, WAITPKG, VPCLMULQDQ, AVX512BITALG, MOVDIRI, MOVDIR64B, AVX512BF16, ENQCMD, AVX512VPOPCNTDQ, AVX5124FMAPS, AVX512VNNI, AVX5124VNNIW, SERIALIZE, UINTR, HRESET, AMXTILE, AMXINT8, AMXBF16, KL, WIDEKL, AVXVNNI or CLDEMOTE extended instruction sets. Each has a corresponding -mno- option to disable use of these instructions.

for detail, plz refer to: [gcc option doc](https://gcc.gnu.org/onlinedocs/gcc/x86-Options.html)

- how to check if an env support sse4.2:

one can try it like below (from rocksdb's build_tools, too...) 

```
$CXX $COMMON_FLAGS -x c++ - -o /dev/null 2>/dev/null <<EOF
  #include <cstdint>
  #include <nmmintrin.h>
  int main() {
    volatile uint32_t x = _mm_crc32_u32(0, 0);
  }
EOF
if [ "$?" = 0 ]; then
  COMMON_FLAGS="$COMMON_FLAGS -DHAVE_SSE42"
elif test "$USE_SSE"; then
  echo "warning: USE_SSE specified but compiler could not use SSE intrinsics, disabling"
fi
```

## wtf is `march=-native`

[doc from gcc](https://gcc.gnu.org/onlinedocs/gcc/x86-Options.html)

>-march=cpu-type
>‘native’
>This selects the CPU to generate code for at compilation time by determining the processor type of the compiling machine. Using -march=native enables all instruction subsets supported by the local machine (hence the result might not run on different machines). Using -mtune=native produces code optimized for the local machine under the constraints of the selected instruction set.

Why not enable `march=-native`:
1. We've met some compiling issue because of the `gcc version`.
2. Underlying instructions set is chosen based on compiling machine where binary is generated. NOT the serving machine where the bin is running, which would create some compatibility issues.

Purpose of `march=-native`:
1. optimization.

## References

[msse2-msse3-msse4](https://stackoverflow.com/questions/10686638/whats-the-difference-among-cflgs-sse-options-of-msse-msse2-mssse3-msse4)
[why-march-native-used-rarely](https://stackoverflow.com/questions/52653025/why-is-march-native-used-so-rarely)
