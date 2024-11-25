## Functions to execute the different instructions of the E20 processot
from sim_helpers import *

def addi(prog_rg1,prog_rg2,imm,next_pc,mem_array,reg_array):
    """ 
    Executes the addi instruction as described in the E20 manual.
    Returns the program counter after execution
    sig: int -> int -> str -> int -> list(int) -> list(int) -> int 
    """
    signed_imm = sign_extend(bin_to_dec((imm)))
    if prog_rg2 == 0:
        reg_array[prog_rg2] = 0
    else:
        storeval = reg_array[prog_rg1] + signed_imm
        if storeval > 65535:
            storeval = storeval - 65536
        reg_array[prog_rg2] = storeval
    next_pc += 1
    return next_pc

def jeq(prog_rg1,prog_rg2,imm,next_pc,mem_array,reg_array):
    """ 
    Executes the jeq instruction as described in the E20 manual.
    Returns the program counter after execution
    sig: int -> int -> str -> int -> list(int) -> list(int) -> int 
    """
    signed_imm = bin_to_dec(imm)
    if reg_array[prog_rg1] == reg_array[prog_rg2]:
        next_pc = next_pc + 1 + sign_extend(signed_imm)
    else:
        next_pc += 1
    return next_pc

def sw(prog_rg1,prog_rg2,imm,next_pc,mem_array,reg_array):
    """ 
    Executes the sw instruction as described in the E20 manual.
    Returns the program counter after execution
    sig: int -> int -> str -> int -> list(int) -> list(int) -> int 
    """
    mem_num = mem_addr(reg_array[prog_rg1],imm)
    mem_array[mem_num] = reg_array[prog_rg2]
    next_pc += 1
    return next_pc

def lw(prog_rg1,prog_rg2,imm,next_pc,mem_array,reg_array):
    """ 
    Executes the lw instruction as described in the E20 manual.
    Returns the program counter after execution
    sig: int -> int -> str -> int -> list(int) -> list(int) -> int 
    """
    mem_num = mem_addr(reg_array[prog_rg1],imm)
    if prog_rg2 == 0:
        reg_array[prog_rg2] = 0
    else:
        reg_array[prog_rg2] = mem_array[mem_num]
    next_pc += 1
    return next_pc

def slti(prog_rg1,prog_rg2,imm,next_pc,mem_array,reg_array):
    """ 
    Executes the slti instruction as described in the E20 manual.
    Returns the program counter after execution
    sig: int -> int -> str -> int -> list(int) -> list(int) -> int 
    """   
    unsigned_imm = sign_extend(bin_to_dec(imm))
    if reg_array[prog_rg1] < unsigned_imm:
        if prog_rg2 != 0:
            reg_array[prog_rg2] = 1
    else:
        reg_array[prog_rg2] = 0
    next_pc += 1
    return next_pc

def add(prog_rg1,prog_rg2,prog_rg3,next_pc,mem_array,reg_array):
    """ 
    Executes the add instruction as described in the E20 manual.
    Returns the program counter after execution
    sig: int -> int -> int -> int -> list(int) -> list(int) -> int 
    """
    store_val = 0
    if reg_array[prog_rg1] + reg_array[prog_rg2] > 65535:
        store_val = reg_array[prog_rg1] + reg_array[prog_rg2] - 65536
    else:
        store_val = reg_array[prog_rg1] + reg_array[prog_rg2]
    if prog_rg3 == 0:
        reg_array[prog_rg3] = 0
    else:
        reg_array[prog_rg3] = store_val
    next_pc += 1
    return next_pc

def sub(prog_rg1,prog_rg2,prog_rg3,next_pc,mem_array,reg_array):
    """ 
    Executes the sub instruction as described in the E20 manual.
    Returns the program counter after execution
    sig: int -> int -> int -> int -> list(int) -> list(int) -> int 
    """
    store_val = 0
    if reg_array[prog_rg1] - reg_array[prog_rg2] < 0:
        store_val = 65536 + (reg_array[prog_rg1] - reg_array[prog_rg2])
    else:
        store_val = reg_array[prog_rg1] - reg_array[prog_rg2]
    if prog_rg3 == 0:
        reg_array[prog_rg3] = 0
    else:
        reg_array[prog_rg3] = store_val
    next_pc += 1
    return next_pc

def orInstr(prog_rg1,prog_rg2,prog_rg3,next_pc,mem_array,reg_array):
    """ 
    Executes the or instruction as described in the E20 manual.
    Returns the program counter after execution
    sig: int -> int -> int -> int -> list(int) -> list(int) -> int 
    """
    if prog_rg3 == 0:
        reg_array[prog_rg3] = 0
    else:
        reg_array[prog_rg3] = reg_array[prog_rg1] | reg_array[prog_rg2]
    next_pc += 1
    return next_pc

def andInstr(prog_rg1,prog_rg2,prog_rg3,next_pc,mem_array,reg_array):
    """ 
    Executes the and instruction as described in the E20 manual.
    Returns the program counter after execution
    sig: int -> int -> int -> int -> list(int) -> list(int) -> int 
    """
    if prog_rg3 == 0:
        reg_array[prog_rg3] = 0
    else:
        reg_array[prog_rg3] = reg_array[prog_rg1] & reg_array[prog_rg2]
    next_pc += 1
    return next_pc

def slt(prog_rg1,prog_rg2,prog_rg3,next_pc,mem_array,reg_array):
    """ 
    Executes the slt instruction as described in the E20 manual.
    Returns the program counter after execution
    sig: int -> int -> int -> int -> list(int) -> list(int) -> int 
    """
    if reg_array[prog_rg1] < reg_array[prog_rg2]:
        if prog_rg3 != 0:
            reg_array[prog_rg3] = 1
    else:
        reg_array[prog_rg3] = 0
    next_pc += 1
    return next_pc

def jr(prog_rg1,prog_rg2,prog_rg3,next_pc,mem_array,reg_array):
    """ 
    Executes the jr instruction as described in the E20 manual.
    Returns the program counter after execution
    sig: int -> int -> int -> int -> list(int) -> list(int) -> int 
    """
    next_pc = reg_array[prog_rg1]
    return next_pc

def j(imm,next_pc):
    """ 
    Executes the j instruction as described in the E20 manual.
    Returns the program counter after execution
    sig: int -> int -> int
    """
    next_pc = imm
    return next_pc

def jal(imm,next_pc,reg_array):
    """ 
    Executes the jal instruction as described in the E20 manual.
    Returns the program counter after execution
    sig: int -> int -> list(int) -> int
    """
    store = next_pc + 1
    if store > 65535:
        store = store - 65536
    reg_array[7] = store
    next_pc = imm
    return next_pc