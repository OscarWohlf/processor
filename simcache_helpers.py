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
