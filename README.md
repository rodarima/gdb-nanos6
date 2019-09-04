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
