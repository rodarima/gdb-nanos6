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

class Eagle(gdb.Command):
	def __init__(self):
		super(Eagle, self).__init__("eagle", gdb.COMMAND_DATA)

	def get_symtab(self, pc):
		progspace = gdb.current_progspace()
		return progspace.find_pc_line(pc).symtab

	def get_objname(self, symtab):
		return symtab.objfile.filename

	def get_maps(self):
		lines = gdb.execute('info proc mappings', to_string=True).split('\n')
		for i,line in enumerate(lines):
			print(i, line)


	def print_best_frame(self, tid):
		frame = gdb.newest_frame()
		i = 0

		while not frame is None:
			pc = frame.pc()
			solib = gdb.solib_name(pc)
			#if pc >= 0x400000 and pc <= 0x42b000:
			if solib is None:
				sal = frame.find_sal()
				symtab = sal.symtab
				func = frame.function()
				print("{: <4} {:<3} {:<30} {}:{}".format(
					tid, i,
					color(COL_YELLOW, func) + "()",
					symtab.filename,
					color(COL_GREEN, sal.line),
				))
				break
			frame = frame.older()
			i+=1

	def invoke(self, arg, from_tty):
		print("Thr  #   Function               Source")
		sel = gdb.selected_thread()
		inferiors = gdb.inferiors()
		for inferior in inferiors:
			threads = list(inferior.threads())
			threads.reverse()
			for thread in threads:
				thread.switch()
				self.print_best_frame(thread.num)
		# Restore thread
		sel.switch()

Eagle()
