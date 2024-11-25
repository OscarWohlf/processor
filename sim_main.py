#!/usr/bin/python3

"""
CS-UY 2214
Adapted from Jeff Epstein
Starter code for E20 simulator
sim.py
"""

from collections import namedtuple
import re
import argparse
import math
from sim_helpers import *
from sim_instruction import *
# Some helpful constant values that we'll be using.
Constants = namedtuple("Constants",["NUM_REGS", "MEM_SIZE", "REG_SIZE"])
constants = Constants(NUM_REGS = 8,
                      MEM_SIZE = 2**13,
                      REG_SIZE = 2**16)

def load_machine_code(machine_code, mem):
    """
    Loads an E20 machine code file into the list
    provided by mem. We assume that mem is
    large enough to hold the values in the machine
    code file.
    sig: list(str) -> list(int) -> NoneType
    """
    machine_code_re = re.compile("^ram\[(\d+)\] = 16'b(\d+);.*$")
    expectedaddr = 0
    for line in machine_code:
        match = machine_code_re.match(line)
        if not match:
            raise ValueError("Can't parse line: %s" % line)
        addr, instr = match.groups()
        addr = int(addr,10)
        instr = int(instr,2)
        if addr != expectedaddr:
            raise ValueError("Memory addresses encountered out of sequence: %s" % addr)
        if addr >= len(mem):
            raise ValueError("Program too big for memory")
        expectedaddr += 1
        mem[addr] = instr

def print_state(pc, regs, memory, memquantity):
    """
    Prints the current state of the simulator, including
    the current program counter, the current register values,
    and the first memquantity elements of memory.
    sig: int -> list(int) -> list(int) - int -> NoneType
    """
    print("Final state:")
    print("\tpc="+format(pc,"5d"))
    for reg, regval in enumerate(regs):
        print(("\t$%s=" % reg)+format(regval,"5d"))
    line = ""
    for count in range(memquantity):
        line += format(memory[count], "04x")+ " "
        if count % 8 == 7:
            print(line)
            line = ""
    if line != "":
        print(line)

def exec_two_reg_instr(instr, mem_array, reg_array, pc):
    """
    Executes instructins with two registers. 
    Stores the result in either the memory array or register array given, 
    depending on the instruction executed. Returns the value of the program counter.
    sig: str -> list(int) -> list(int) -> int -> int
    """
    curr_instruction = ""
    prog_rg1 = 0
    prog_rg2 = 0
    imm = ""
    curr_instruction, prog_rg1, prog_rg2, imm = determine_two_reg_instruction(instr)
    next_pc = pc
    
    if curr_instruction == "addi":
        return addi(prog_rg1,prog_rg2,imm,next_pc,mem_array,reg_array)
    elif curr_instruction == "jeq":
        return jeq(prog_rg1,prog_rg2,imm,next_pc,mem_array,reg_array)
    elif curr_instruction == "sw":
        return sw(prog_rg1,prog_rg2,imm,next_pc,mem_array,reg_array)
    elif curr_instruction == "lw":
        return lw(prog_rg1,prog_rg2,imm,next_pc,mem_array,reg_array)
    elif curr_instruction == "slti":
        return slti(prog_rg1,prog_rg2,imm,next_pc,mem_array,reg_array)
    elif curr_instruction == "undefined":
        next_pc += 1
        return next_pc

def exec_three_reg_instr(instr,mem_array,reg_array,pc):
    """
    Executes instructins with three registers. 
    Stores the result in either the memory array or register array given, 
    depending on the instruction executed. Returns the value of the program counter.
    sig: str -> list(int) -> list(int) -> int -> int
    """
    curr_instr = ""
    prog_rg1 = 0
    prog_rg2 = 0
    prog_rg3 = 0
    curr_instr, prog_rg1, prog_rg2, prog_rg3 = determine_three_reg_instruction(instr)
    next_pc = pc

    if curr_instr == "add":
        return add(prog_rg1,prog_rg2,prog_rg3,next_pc,mem_array,reg_array)
    elif curr_instr == "sub":
        return sub(prog_rg1,prog_rg2,prog_rg3,next_pc,mem_array,reg_array)
    elif curr_instr == "or":
        return orInstr(prog_rg1,prog_rg2,prog_rg3,next_pc,mem_array,reg_array)
    elif curr_instr == "and":
        return andInstr(prog_rg1,prog_rg2,prog_rg3,next_pc,mem_array,reg_array)
    elif curr_instr == "slt":
        return slt(prog_rg1,prog_rg2,prog_rg3,next_pc,mem_array,reg_array)
    elif curr_instr == "jr":
        return jr(prog_rg1,prog_rg2,prog_rg3,next_pc,mem_array,reg_array)
    elif curr_instr == "undefined":
        next_pc += 1
        return next_pc

def exec_zero_reg_instr(instr,mem_array,reg_array,pc):
    """
    Executes instructins with zero registers. 
    Stores the result in either the memory array or register array given, 
    depending on the instruction executed. Returns the value of the program counter.
    sig: str -> list(int) -> list(int) -> int -> int
    """
    curr_instr = ""
    imm = 0
    next_pc = pc
    curr_instr, imm = determine_zero_reg_instruction(instr)
    if curr_instr == "j":
        return j(imm,next_pc)
    elif curr_instr == "jal":
        return jal(imm,next_pc,reg_array)
    elif curr_instr == "undefined":
        next_pc += 1
        return next_pc

def execute_instr(instr,mem_array,reg_array,pc):
    """
    Handles which type of instruction we are executing 
    and passes on the arguments to the correct function. 
    Returns the value of the program counter after the instruction.
    sig: str -> list(int) -> list(int) -> int -> int
    """
    instr_type = determine_reg_amount(instr)
    next_pc = pc
    if instr_type == 3:
        return exec_three_reg_instr(instr,mem_array,reg_array,next_pc)
    elif instr_type == 2:
        return exec_two_reg_instr(instr,mem_array,reg_array,next_pc)
    else:
        return exec_zero_reg_instr(instr,mem_array,reg_array,next_pc)

def main():
    parser = argparse.ArgumentParser(description='Simulate E20 machine')
    parser.add_argument('filename', help='The file containing machine code, typically with .bin suffix')
    cmdline = parser.parse_args()
    mem_array = [0]*8192
    reg_array = [0]*8
    pc = 0

    with open(cmdline.filename) as file:
        machine_code = file.readlines()
        memory = load_machine_code(machine_code,mem_array) 

    while True:
        bit13_pc = bit16_to_bit13(pc)
        curr_instr = bin_to_instruction(decimal_to_binary(mem_array[bit13_pc]))

        if check_halt(curr_instr,bit13_pc):
            break

        pc = execute_instr(curr_instr,mem_array,reg_array,pc)

        if pc > 65535:
            pc = pc - 65536

    print_state(pc,reg_array,mem_array,128)
if __name__ == "__main__":
    main()
#ra0Eequ6ucie6Jei0koh6phishohm9