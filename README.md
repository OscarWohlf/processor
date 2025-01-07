Project for simulating the execution of assembly code instruction on a simple processor. The sim_main.py file has a script for simulating the execution of assembly code. The simcache.py file has code for simulating the cache of this execution for different cache configurations. Test cases are included both for the cache simulator and the execution simulator. 

The main simulator can be used by the command python3 sim_main.py "filename", where filename is the name of the file. For example, python3 sim_main.py array-sum.bin
The output will show the content of the program counter, the 8 registers, as well as the first 128 memory cells in hexadecimal.

The cache simulator can be used by the command python3 simcache.py "filename" --cache followed by either 3 or 6 integers specifying thecache information. If there are  numbers there will only be one cache if there are 6 numbers there will be two caches. The first 3 numbers specify the size, associativity and blocksize of the L! cache and the next 3 do the same for L2 cache. 
The output will show information about the caches as well as cache information for the execution of each instruction. The infgormation will be wether the instruction results in a cache hit or miss, the program counter number and information about where in the cache the number will be stored. 
