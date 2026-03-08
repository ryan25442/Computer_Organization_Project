# Runs automated tests for assembler and simulator

import sys
import os
from colors import bcolors
from AsmGrader import AsmGrader
from SimGrader import SimGrader
from Results import Results


VERBOSE = False
GRADE_ASSEMBLER = True
GRADE_SIMULATOR = True
CLEAR_RESIDUE = False

def printHelp():
	print('----Please enter in correct format----')
	print("--verbose for verbose output")
	print("--no-asm to not grade assembler")
	print("--no-sim to not grade simulator")
	print("--clear-residue to delete generated outputs before grading")
	print("--linux for Linux operating system")
	print("--windows for windows operating system")
	print("Example_linux: $python3 src/main.py --linux --no-sim")
	print("Example_windows: >python3 src\main.py --windows --no-sim")

def setupArgs():
	global VERBOSE
	global GRADE_ASSEMBLER
	global GRADE_SIMULATOR
	global CLEAR_RESIDUE
	global OPERATING_SYSTEM

	if len(sys.argv) < 3:
		printHelp()
		exit()

	for arg in sys.argv[1:]:
		if arg == "--verbose":
			VERBOSE = True
		elif arg == "--no-asm":
			GRADE_ASSEMBLER = False
		elif arg == "--no-sim":
			GRADE_SIMULATOR = False
		elif arg == "--clear-residue":
			CLEAR_RESIDUE = True
		elif ((arg == "--linux") | (arg == "--windows")):
			OPERATING_SYSTEM = arg[2:]
		else:
			printHelp()
			exit()
			# break

def _clear_residue(operating_system):
	removed = []
	if operating_system == 'linux':
		dirs = [
			"tests/assembly/user_bin_s",
			"tests/assembly/user_bin_h",
			"tests/user_traces/simple",
			"tests/user_traces/hard",
		]
	elif operating_system == 'windows':
		dirs = [
			"tests\\assembly\\user_bin_s",
			"tests\\assembly\\user_bin_h",
			"tests\\user_traces\\simple",
			"tests\\user_traces\\hard",
		]
	else:
		return

	for d in dirs:
		if not os.path.isdir(d):
			continue
		for name in os.listdir(d):
			path = os.path.join(d, name)
			if os.path.isfile(path):
				os.remove(path)
				removed.append(path)
	return removed

def main():
	setupArgs()

	if CLEAR_RESIDUE:
		removed = _clear_residue(OPERATING_SYSTEM)
		if removed:
			print("Deleted files:")
			for path in removed:
				print(path)
		else:
			print("No residue files found to delete.")
		return

	asmGrader = AsmGrader(VERBOSE, GRADE_ASSEMBLER,OPERATING_SYSTEM)
	simGrader = SimGrader(VERBOSE, GRADE_SIMULATOR,OPERATING_SYSTEM)

	asmRes = asmGrader.grade()
	simRes = simGrader.grade()	

	res = Results(VERBOSE, asmRes, simRes)
	res.declare()
	

if __name__ == '__main__':
	main()
