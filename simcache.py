#!/usr/bin/python3

from collections import namedtuple
import re
import argparse
from sim_helpers import *
from sim_instruction import * 
from sim_main import * 
from simcache_helpers import * 

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
