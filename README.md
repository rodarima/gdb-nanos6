# Multithread helper scripts for GDB

Some scripts I developed to ease the bug-tracking process on concurrent programs
that use a runtime like OmpSs-2. To install copy the python the script you want
(say `eagle.py`) into a folder like `~/.gdb/` and add to the `~/.gdbinit` file
the following line for each script:

	source ~/.gdb/eagle.py

## Eagle

The `eagle` command is provided by the `eagle.py` script, and shows the first
frame on each thread that is located in a file which is not a dynamic library.
This is useful when in conjunction with libraries like
[TAMPI](https://github.com/bsc-pm/tampi), which locks the current task.

Example: A program is stuck in a deadlock with OmpSs-2 and TAMPI, but there are 47
threads where most of them are in `pthread_cond_wait`.

```
(gdb) info threads
  Id   Target Id                           Frame 
  1    Thread 0x7f9875aeb740 (LWP 1874986) 0x00007f9875faace5 in raise () from /usr/lib/libc.so.6
  2    Thread 0x7f987512a740 (LWP 1874991) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
* 3    Thread 0x7f9865ffa740 (LWP 1875018) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  4    Thread 0x7f9866ffc740 (LWP 1875010) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  5    Thread 0x7f986effc740 (LWP 1874996) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  6    Thread 0x7f9862925740 (LWP 1875026) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  7    Thread 0x7f9861122740 (LWP 1875029) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  8    Thread 0x7f97d967f740 (LWP 1875115) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  9    Thread 0x7f986d7f9740 (LWP 1874999) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  10   Thread 0x7f9829ffb700 (LWP 1875106) 0x00007f9876063abf in poll () from /usr/lib/libc.so.6
  11   Thread 0x7f9867ffe740 (LWP 1875007) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  12   Thread 0x7f982b7fd740 (LWP 1875050) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  13   Thread 0x7f9864ff8740 (LWP 1875023) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  14   Thread 0x7f982a7fb740 (LWP 1875052) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  15   Thread 0x7f98667fb740 (LWP 1875014) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  16   Thread 0x7f98297fa700 (LWP 1875109) 0x00007f987606e70e in epoll_wait () from /usr/lib/libc.so.6
  17   Thread 0x7f97b9b16740 (LWP 1875125) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  18   Thread 0x7f987592c700 (LWP 1874990) 0x00007f98760362d1 in clock_nanosleep@GLIBC_2.2.5 () from /usr/lib/libc.so.6
  19   Thread 0x7f982affc740 (LWP 1875051) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  20   Thread 0x7f986cff8740 (LWP 1875000) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
...
  43   Thread 0x7f986dffa740 (LWP 1874998) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  44   Thread 0x7f986e7fb740 (LWP 1874997) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  45   Thread 0x7f9860921740 (LWP 1875030) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  46   Thread 0x7f97c829e740 (LWP 1875120) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
  47   Thread 0x7f97bab18740 (LWP 1875123) 0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
```

In this particular case, only 16 tasks are currently executing code from my
program, but is hard to determine which ones are they, rather than going thread
by thread and inspecting the complete backtrace. The `eagle` command shows only
the first frame that is not in a dynamic library.

```
(gdb) eagle
Thr  #   Function               Source
1    2   term_handler()         src/cpic.c:47
3    8   recv_plist_y()         src/comm_plasma.c:957
6    8   recv_plist_y()         src/comm_plasma.c:957
7    8   recv_plist_y()         src/comm_plasma.c:957
9    8   recv_plist_y()         src/comm_plasma.c:957
12   8   recv_plist_y()         src/comm_plasma.c:957
13   8   recv_plist_y()         src/comm_plasma.c:957
14   6   sim_pre_step()         src/sim.c:201
19   8   recv_plist_y()         src/comm_plasma.c:957
22   8   recv_plist_y()         src/comm_plasma.c:957
23   8   recv_plist_y()         src/comm_plasma.c:957
24   8   recv_plist_y()         src/comm_plasma.c:957
28   8   recv_plist_y()         src/comm_plasma.c:957
31   8   recv_plist_y()         src/comm_plasma.c:957
34   8   recv_plist_y()         src/comm_plasma.c:957
36   8   recv_plist_y()         src/comm_plasma.c:957
38   8   recv_plist_y()         src/comm_plasma.c:957
39   8   recv_plist_y()         src/comm_plasma.c:957
```

The 16 tasks can immediately seen being stuck in the `recv_plist_y` function,
which is in my program. It shows the thread number in the first column and the
frame number in the second. If we look into one:

```
(gdb) thread 3
[Switching to thread 3 (Thread 0x7f9865ffa740 (LWP 1875018))]
#0  0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
(gdb) bt
#0  0x00007f9876144cf5 in pthread_cond_wait@@GLIBC_2.3.2 () from /usr/lib/libpthread.so.0
#1  0x00007f9875e16ea1 in __gthread_cond_wait (__mutex=<optimized out>, __cond=<optimized out>)
    at /build/gcc/src/gcc-build/x86_64-pc-linux-gnu/libstdc++-v3/include/x86_64-pc-linux-gnu/bits/gthr-default.h:865
#2  std::condition_variable::wait (this=<optimized out>, __lock=...) at /build/gcc/src/gcc/libstdc++-v3/src/c++11/condition_variable.cc:53
#3  0x00007f9875a3befc in TaskBlocking::taskBlocks(WorkerThread*, Task*, ThreadManagerPolicy::thread_run_inline_policy_t) ()
   from /usr/lib/libnanos6-optimized-linear-regions-fragmented.so
#4  0x00007f9875a31774 in nanos6_block_current_task () from /usr/lib/libnanos6-optimized-linear-regions-fragmented.so
#5  0x00007f9876161b89 in nanos6_block_current_task (blocking_context=0x7f97f4206790) at loader/indirect-symbols/blocking.c:34
#6  0x00007f9876a344bb in ?? () from /usr/lib/libtampi-c.so.0
#7  0x00007f9876a39a53 in MPI_Recv () from /usr/lib/libtampi-c.so.0
#8  0x0000000000407ff2 in recv_plist_y (sim=0x7f97f416a8c0, l=0x7f97f4172dd0, src=3, ic=11) at src/comm_plasma.c:957
#9  0x000000000040792e in recv_pchunk_y (sim=0x7f97f416a8c0, c=0x7f97f416e080) at src/comm_plasma.c:1021
#10 0x0000000000408768 in nanos6_unpacked_task_region_exchange_plasma_y1 ()
#11 0x000000000040879c in nanos6_ol_task_region_exchange_plasma_y1 ()
#12 0x00007f9875a3e11e in ExecutionWorkflow::executeTask(Task*, ComputePlace*, MemoryPlace*) ()
   from /usr/lib/libnanos6-optimized-linear-regions-fragmented.so
#13 0x00007f9875a1b4b8 in WorkerThread::handleTask(CPU*) () from /usr/lib/libnanos6-optimized-linear-regions-fragmented.so
#14 0x00007f9875a1bc1b in WorkerThread::body() () from /usr/lib/libnanos6-optimized-linear-regions-fragmented.so
#15 0x00007f9875a11c91 in kernel_level_thread_body_wrapper(void*) () from /usr/lib/libnanos6-optimized-linear-regions-fragmented.so
#16 0x00007f987613e46f in start_thread () from /usr/lib/libpthread.so.0
#17 0x00007f987606e3d3 in clone () from /usr/lib/libc.so.6
```

We see the first 8 frames were skipped, as the `eagle` command only shows the
function of the program being executed which first appears in the stack.

## Debugging OmpSs-2 tasks with GDB

This script helps the user to debug troubles with tasks using GDB with Python
extensions. The only current command is `ompss2` which shows the threads created
by `nanos6`:

	1 Loader
	2 Leader 0x55555558de80
	3 Main
	  Task 0x555555594660 B "main" at Spawned Task
	4 Worker 0x555555590530 running task 0x7fffcb5d5958
	  Task 0x7fffcb5d5958 R "chunk_E" at src/particle.c:318:9
	5 Worker 0x555555593050 running task 0x7fffcb649f20
	  Task 0x7fffcb649f20 R "collect_particles_x" at src/comm.c:351:9
	6 Worker 0x555555590d00 running task 0x7fffcb5d6018
	  Task 0x7fffcb5d6018 R "chunk_E" at src/particle.c:318:9
	9 Worker 0x7fffe8015050 running task 0x7fffcb66a2d8
	  Task 0x7fffcb66a2d8 R "chunk_E" at src/particle.c:318:9

As it can be shown, each `Worker` is running one task. The main function is
being executed by a thread alone, and is currently blocked.

Note: Requires nanos6 to be compiled with debugging symbols enabled.
