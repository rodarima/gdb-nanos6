import gdb
import re

def str_addr(val):
	 return "0x{:x}".format(int(val))

def string(val):
	try:
		str_label = val.string()
	except:
		str_label = "(null)"
	return str_label

COL_RED='\033[31m'
COL_GREEN='\033[32m'
COL_YELLOW='\033[33m'
COL_BLUE='\033[34m'
COL_RESET='\033[m' # reset to the defaults

def color(col, v):
	return "{}{}{}".format(col, v, COL_RESET)

class InfoWorkers(gdb.Command):
	def __init__(self):
		super(InfoWorkers, self).__init__("ompss2", gdb.COMMAND_DATA)

	def task_info(self, addr):
		label = string(gdb.parse_and_eval(
			"((nanos6_task_info_t *) %s)->implementations[0].task_label" %
			addr))

		source = string(gdb.parse_and_eval(
			"((nanos6_task_info_t *) %s)->implementations[0].declaration_source"
			% addr))


		#print('Task "%s" at %s' % (label, source))
		return {'label':label, 'source':source}

	def task(self, addr):
		task_info = gdb.parse_and_eval("((Task *) %s)->_taskInfo" % addr)
		#gdb.execute("p (Task *) %s" % addr)

		task_info_addr = str_addr(task_info)

		compute_place = gdb.parse_and_eval("((Task *) %s)->_thread->_M_b->_M_p" % addr)

		#print("Task info addr %s" % task_info_addr)
		d = self.task_info(task_info_addr)
		d['info'] = task_info_addr
		d['task'] = addr

		#print(compute_place)
		#print(int(compute_place))

		if int(compute_place) == 0:
			d['state'] = 'N'
		else:
			d['state'] = 'R'

		if d['state'] == 'R':
			st = color(COL_GREEN, 'R')
		else:
			st = color(COL_GREEN, 'N')

		#print('  {} {} {} "{}" at {}'.format(
		#	color(COL_YELLOW, 'Task'),
		#	color(COL_BLUE, d['task']),
		#	st,
		#	d['label'],
		#	d['source']))
		return d

	def worker_thread(self, addr, ptid):

		#print("Worker address {}".format(addr))
		#gdb.execute("p *(WorkerThread *) %s" % addr)
		task = gdb.parse_and_eval("((WorkerThread *) %s)->_task" % addr)
		task_addr = str_addr(task)
		#print('Task addr %s' % task_addr)
		#d = self.task(task_addr)
		#d['task'] = task_addr

		print('{} {} {} running task {}'.format(
			ptid,
			color(COL_GREEN, 'Worker'),
			color(COL_BLUE, addr),
			color(COL_BLUE, task_addr)))

	def leader_thread(self, addr, ptid):

		print('{} {}Leader{} {}{}{}'.format(
			ptid,
			COL_GREEN, COL_RESET,
			COL_BLUE, addr, COL_RESET))

	def loader_thread(self, ptid):
		print('{} {}Loader{}'.format(
			ptid,
			COL_GREEN, COL_RESET))

	def main_thread(self, ptid):
		print('{} {}Main{}'.format(
			ptid,
			COL_GREEN, COL_RESET))

	def backtrace(self, th, bt_str):
		# Sort backtrace by time
		bt = bt_str.split('\n')
		bt.reverse()
		#print('\n'.join(bt))

		tid = th.ptid[1]
		tid = th.num

		thread = None
		tasks = {}
		tasks_addr = []

		# Search for each task body
		for line in bt:
			if 'WorkerThread::body' in line:
				matchs = re.search("this=(0x[0-9a-f]*)", line, flags=0)
				addr = matchs.group(1)
				self.worker_thread(addr, tid)
			elif 'Task::body' in line:
				matchs = re.search("this=(0x[0-9a-f]*)", line, flags=0)
				addr = matchs.group(1)
				tasks[addr] = self.task(addr)
				tasks_addr.append(addr)
			elif ' in main ' in line:
				self.main_thread(tid)
			elif 'TaskBlocking::taskBlocks' in line:
				#print('blocks')

				# If this is the main thread, we cannot get access to the
				# current task, so we add the blocked task directly by matching
				# the currentTask parameter.

				matchs = re.search("currentTask=(0x[0-9a-f]*)", line, flags=0)
				addr = matchs.group(1)

				if not addr in tasks:
					task = self.task(addr)
					tasks[addr] = task
					tasks_addr.append(addr)

				tasks[addr]['state'] = 'B'

			elif 'LeaderThread::body' in line:
				matchs = re.search("this=(0x[0-9a-f]*)", line, flags=0)
				addr = matchs.group(1)
				self.leader_thread(addr, tid)
			elif '_nanos6_loader_main' in line:
				self.loader_thread(tid)

		# Only the last task must be running (kevin)

		for addr in tasks_addr:
			d = tasks[addr]
			if d['state'] == 'R':
				st = color(COL_GREEN, 'R')
			else:
				st = color(COL_RED, 'B')

			print('  {} {} {} "{}" at {}'.format(
				color(COL_YELLOW, 'Task'),
				color(COL_BLUE, d['task']),
				st,
				d['label'],
				d['source']))


		#print()

	def invoke(self, arg, from_tty):
		# An inferior is the 'currently running applications'. In this case we only
		# have one.
		inferiors = gdb.inferiors()
		for inferior in inferiors:
			threads = list(inferior.threads())
			threads.reverse()
			for thread in threads:
				thread.switch()
				bt = gdb.execute('bt', to_string=True)
				self.backtrace(thread, bt)
				#return

InfoWorkers()
