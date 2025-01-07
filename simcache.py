#!/usr/bin/python3

"""
CS-UY 2214
Adapted from Jeff Epstein
Starter code for E20 cache simulator
simcache.py
"""
from collections import namedtuple
import re
import argparse
from sim_helpers import *
from sim_instruction import *
from sim_main import *
class CacheUnit:
    """
    Represents a unit in a cache, containing a block and its associated tag.
    
    Attributes:
        block (int): The memory block stored in this cache unit.
        tag (int): The tag used for identifying the cache block.
    """
    def __init__(self,block,tag):
        self.block = block
        self.tag = tag
    
    def get_tag(self):
        return self.tag
    
    def get_block(self):
        return self.block
    
    def __str__(self):
        return str(self.block) + "," + str(self.tag)
    
    def __repr__(self):
        return str(self.block) + "," + str(self.tag)

def print_cache_config(cache_name, size, assoc, blocksize, num_rows):
    """
    Prints out the correctly-formatted configuration of a cache.

    cache_name -- The name of the cache. "L1" or "L2"

    size -- The total size of the cache, measured in memory cells.
        Excludes metadata

    assoc -- The associativity of the cache. One of [1,2,4,8,16]

    blocksize -- The blocksize of the cache. One of [1,2,4,8,16,32,64])

    num_rows -- The number of rows in the given cache.

    sig: str, int, int, int, int -> NoneType
    """

    summary = "Cache %s has size %s, associativity %s, " \
        "blocksize %s, rows %s" % (cache_name,
        size, assoc, blocksize, num_rows)
    print(summary)

def print_log_entry(cache_name, status, pc, addr, row):
    """
    Prints out a correctly-formatted log entry.

    cache_name -- The name of the cache where the event
        occurred. "L1" or "L2"

    status -- The kind of cache event. "SW", "HIT", or
        "MISS"

    pc -- The program counter of the memory
        access instruction

    addr -- The memory address being accessed.

    row -- The cache row or set number where the data
        is stored.

    sig: str, str, int, int, int -> NoneType
    """
    log_entry = "{event:8s} pc:{pc:5d}\taddr:{addr:5d}\t" \
        "row:{row:4d}".format(row=row, pc=pc, addr=addr,
            event = cache_name + " " + status)
    print(log_entry)

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
        return exec_zero_reg_instr(instr,reg_array,next_pc)

def num_rows(size,assoc,bsize):
    """
    Caclulates the number of rows in the cache
    sig: int -> int -> int -> int
    """
    return int(size / (assoc*bsize))

def direct_cache_lw(name,cache,blockid,tag,row,pc,address):
    """
    Takes info about the cache and calculates the result of a lw operation on a direct cache
    Returns the result and prints the wanted cache update
    sig: str -> list(list(CacheUnit)) -> int -> int -> int -> int -> int -> str -> NoneType
    """
    result = ""
    unit = CacheUnit(blockid,tag)
    if cache[row] == [0]: #Miss if row is empty     
        cache[row] = unit
        result = "MISS"
    elif cache[row].get_block() == blockid: #Hit if correct block in row
        result = "HIT"
    elif cache[row].get_block() != blockid: #Miss and update if wrong block in row
        result = "MISS"
        cache[row] = unit
    print_log_entry(name,result,pc,address,row)
    return result

def find_blocks_in_row(cache,row):
    """
    Helper function to find the different blocks that are stored in a cache row
    sig: list(list(CacheUnit)) -> int -> list(int)
    """
    blocks = []
    for cell in cache[row]: #Iterates through the row and adds the different blocks to a list
        if cell == 0:
            continue
        else:
            blocks.append(cell.get_block())
    return blocks

def insert_nonfull_assoc_cache(cache,row,unit):
    """
    Helper function to add to a non-full cache with associativity greater than 1.
    The new CacheUnit is added to the first open spot
    sig: list(list(CacheUnit)) -> int -> CacheUnit -> NoneType
    """
    for idx, cell in enumerate(cache[row]):
        if cell == 0:
            cache[row][idx] = unit
            break

def insert_full_assoc_cache(cache,row,unit,lru):
    """
    Inserts into a cache with associativity graeter than 1, when the row is full. 
    Uses and updated the LRU
    sig: list(list(CacheUnit)) -> int -> CacheUnit -> dict[int,int] -> NoneType
    """
    max_val  = 0
    max_cell_idx = 0
    for idx, cell in enumerate(cache[row]): #Loop to find the cell in the row to evict using te LRU
        cell_lru = lru[cell.get_block()]
        if cell_lru > max_val:
            max_val = cell_lru
            max_cell_idx = idx 
    del lru[cache[row][max_cell_idx].get_block()] #Deletes the block that is no longer in the cache fro the LRU
    cache[row][max_cell_idx] = unit #Adds the new CacheUnit to the cache where the previous block was evected from

def update_lru(lru,blockid):
    """
    Updates the lru after a cache operation
    sig: dict[int,int] -> int -> NoneType
    """
    for block in lru: #Increments the value of all blocks by 1
        lru[block] += 1
    lru[blockid] = 0 #Sets the lru value of the block currently used to 0 

def associative_lw(name,cache,blockid,tag,row,pc,address,lru):
    """
    Takes info about the cache and calculates the result of a lw operation on an associative cache
    Returns the result and prints the wanted cache update
    sig: str -> list(list(CacheUnit)) -> int -> int -> int -> int -> int -> dict[int,int] ->  str
    """
    result = ""
    unit = CacheUnit(blockid,tag)
    blocks = find_blocks_in_row(cache,row)
    if blockid in blocks: #HIT if the current block is in the row
        result = "HIT"
        update_lru(lru,blockid)
    else:
        result = "MISS"
        if 0 in cache[row]: #Space left in row so add to non-full row 
            insert_nonfull_assoc_cache(cache,row,unit)
        else: #Full row, so evict and add to row 
            insert_full_assoc_cache(cache,row,unit,lru)
        update_lru(lru,blockid)
    print_log_entry(name,result,pc,address,row)
    return result

def direct_sw(name,cache,row,blockid,tag,pc,address):
    """
    Updates the cache when a sw operation is performed on a direct cache
    Prints the wanted cache update
    sig: str -> list(list(CacheUnit)) -> int -> int -> int -> int -> int -> NoneType
    """
    print_log_entry(name,"SW",pc,address,row)
    unit = CacheUnit(blockid,tag)
    cache[row] = unit

def associative_sw(name,cache,blockid,tag,pc,row,lru,address):
    """
    Updates the cache when a sw operation is performed on a associative cach
    Prints the wanted cache update
    Mostly passes on the data to other helper functions
    sig: str -> list(list(CacheUnit)) -> int -> int -> int -> int -> dict[int,int] -> int -> NoneType
    """
    print_log_entry(name,"SW",pc,address,row)
    unit = CacheUnit(blockid,tag)
    if 0 in cache[row]: #Space left in row so add to non-full row
        insert_nonfull_assoc_cache(cache,row,unit)
    else: #Full row so we have to evict according to LRU and then add
        insert_full_assoc_cache(cache,row,unit,lru)
    update_lru(lru,blockid)

def cache_sw(name,cache,row,blockid,tag,pc,address,lru,assoc):
    """
    Passes on cache data to the correct function when doing a sw
    depending on if the cache is direct or associative
    sig: str -> list(list(CacheUnit)) -> int -> int -> int -> int -> int -> dict[int,int] -> int -> NoneType
    """
    if assoc == 1:
        direct_sw(name,cache,row,blockid,tag,pc,address)
    else: 
        associative_sw(name,cache,blockid,tag,pc,row,lru,address)

def cache_lw(name,cache,blockid,tag,row,pc,address,lru,assoc):
    """
    Passes on cache data to the correct function when doing a lw
    depending on if the cache is direct or associative
    Returns the result
    sig: str -> list(list(CacheUnit)) -> int -> int -> int -> int -> int -> dict[int,int] -> int -> str
    """
    result = ""
    if assoc == 1:
        result = direct_cache_lw(name,cache,blockid,tag,row,pc,address)
    else:
        result = associative_lw(name,cache,blockid,tag,row,pc,address,lru)
    return result

def cache_execution(name, cache, instr, pc, address, row, tag, blockid, assoc, lru):
    """
    Determines what kind of cache instruction we are dealing wth an passes on the data 
    sig: str -> list(list(CacheUnit)) -> str -> int -> int -> int -> int -> int -> int -> dict[int,int] -> NoneType
    """
    type = instr[0:3] #Determine if we are dealing with lw or sw 
    if type == "100": #LW
        cache_lw(name,cache,blockid,tag,row,pc,address,lru,assoc)
    elif type == "101": #SW
        cache_sw(name,cache,row,blockid,tag,pc,address,lru,assoc)

def multi_cache_execution(instr,L1info,L2info,pc,lru1,lru2,address):
    """
    Determines what kind of cache instruction we are dealing wth an passes on the data when we have multiple caches
    sig: str -> tuple[list[list[CacheUnit]], int, int, int, int] -> tuple[list[list[CacheUnit]], int, int, int, int] -> int -> dict[int, int] -> dict[int, int] -> int -> NoneType
    """
    type = instr[0:3] #Determine if we are dealing with lw or sw 
    L1cache,L1blockid,L1row,L1tag,L1assoc = L1info #Extract cache info
    L2cache,L2blockid,L2row,L2tag,L2assoc = L2info #Extract cache info
    if type == "100": #LW
        result = ""
        result = cache_lw("L1",L1cache,L1blockid,L1tag,L1row,pc,address,lru1,L1assoc)
        if result == "MISS": #Continue to L2 cache if MISS in L1 cache
            cache_lw("L2",L2cache,L2blockid,L2tag,L2row,pc,address,lru2,L2assoc)
    elif type == "101": #SW
        cache_sw("L1",L1cache,L1row,L1blockid,L1tag,pc,address,lru1,L1assoc)
        cache_sw("L2",L2cache,L2row,L2blockid,L2tag,pc,address,lru2,L2assoc)

def check_cache_instr(instr):
    """
    Determines if our program is currently executing an instruction that has an effect on the cache
    sig: str -> bool 
    """
    type = instr[0:3]
    if type == "100" or type == "101":
        return True
    return False

def address(instr,reg):
    """
    Determines the address we want to get or insert into cache
    sig: str -> list(int) -> int
    """
    prog_reg1 = bin_to_dec(instr[3:6])
    imm = instr[9:]
    addr = mem_addr(reg[prog_reg1],imm)
    return addr

def main():
    parser = argparse.ArgumentParser(description='Simulate E20 cache')
    parser.add_argument('filename', help=
        'The file containing machine code, typically with .bin suffix')
    parser.add_argument('--cache', help=
        'Cache configuration: size,associativity,blocksize (for one cache) '
        'or size,associativity,blocksize,size,associativity,blocksize (for two caches)')
    cmdline = parser.parse_args()
    mem_array = [0]*8192
    reg_array = [0]*8
    pc = 0

    with open(cmdline.filename) as file:
        machine_code = file.readlines()
        load_machine_code(machine_code,mem_array) 

    if cmdline.cache is not None:
        parts = cmdline.cache.split(",")
        if len(parts) == 3:
            [L1size, L1assoc, L1blocksize] = [int(x) for x in parts]
            rows = num_rows(L1size,L1assoc,L1blocksize)
            L1cache = [[0] * L1assoc for _ in range(rows)] #Initialize L1 cache
            lru = {} #Initialize lru
            print_cache_config("L1", L1size, L1assoc, L1blocksize,rows)

            while True:
                bit13_pc = bit16_to_bit13(pc)
                curr_instr = bin_to_instruction(decimal_to_binary(mem_array[bit13_pc]))
                
                if check_halt(curr_instr,bit13_pc):
                    break
                    
                if check_cache_instr(curr_instr):
                    addr = address(curr_instr,reg_array)
                    blockid = addr // L1blocksize
                    row = blockid % rows
                    tag = blockid // rows
                    cache_execution("L1",L1cache,curr_instr,pc,addr,row,tag,blockid,L1assoc,lru)
                    
                pc = execute_instr(curr_instr,mem_array,reg_array,pc)

                if pc > 65535:
                    pc = pc - 65536
            
        elif len(parts) == 6:
            [L1size, L1assoc, L1blocksize, L2size, L2assoc, L2blocksize] = \
                [int(x) for x in parts]
            L1rows = num_rows(L1size,L1assoc,L1blocksize)
            L2rows = num_rows(L2size,L2assoc,L2blocksize)

            L1cache = [[0] * L1assoc for _ in range(L1rows)] #Initialize L1 cache
            L2cache = [[0] * L2assoc for _ in range(L2rows)] #Initialize L2 cache
            lru_L1 = {} #Initialize lru 1
            lru_L2 = {} #Initialize lru 2

            print_cache_config("L1", L1size, L1assoc, L1blocksize,L1rows)
            print_cache_config("L2", L2size, L2assoc, L2blocksize,L2rows)

            while True:
                bit13_pc = bit16_to_bit13(pc)
                curr_instr = bin_to_instruction(decimal_to_binary(mem_array[bit13_pc]))

                if check_halt(curr_instr,bit13_pc):
                    break
                
                if check_cache_instr(curr_instr):
                    addr = address(curr_instr,reg_array)
                    L1blockid = addr // L1blocksize
                    L2blockid = addr // L2blocksize
                    L1row = L1blockid % L1rows
                    L1tag = L1blockid // L1rows
                    L2row = L2blockid % L2rows
                    L2tag = L2blockid // L2rows
                    L1info = [L1cache,L1blockid,L1row,L1tag,L1assoc]
                    L2info = [L2cache,L2blockid,L2row,L2tag,L2assoc]
                    multi_cache_execution(curr_instr,L1info,L2info,pc,lru_L1,lru_L2,addr)
                    

                pc = execute_instr(curr_instr,mem_array,reg_array,pc)

                if pc > 65535:
                    pc = pc - 65536
        else:
            raise Exception("Invalid cache config")

if __name__ == "__main__":
    main()
#ra0Eequ6ucie6Jei0koh6phishohm9
