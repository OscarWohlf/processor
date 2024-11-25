## Helper Functions
def decimal_to_binary(dec_num):
    """
    Converts a decimal number to a binary number
    sig: int -> int
    """
    bin_num = ""
    if dec_num == 0:
        bin_num = "0"
    while dec_num != 0:
        rem = dec_num%2
        if rem == 1:
            bin_num = "1"+bin_num
        else:
            bin_num = "0"+bin_num
        dec_num = dec_num//2
    return int(bin_num)

def bin_to_dec(num):
    """
    Converts a binary number string to a decimal number
    sig: str -> int
    """
    dec_num = 0
    for i in range(len(num)):
        dec_num += 2**i * int(num[len(num)-1-i])
    return dec_num

def bin_to_instruction(bin_num):
    """ 
    Converts a binary string to a valid instruction
    sig: str -> str
    """
    bin = str(bin_num)
    instruction = ""
    if len(bin) < 16:
        for i in range(16-len(bin)):
            bin = "0"+bin
    return bin

def bit16_to_bit13(num):
    """
    Extracts the last 13 bit of a binary number
    sig: int -> int
    """
    bin = bin_to_instruction(decimal_to_binary(num))
    bin2 = bin[3:]
    return bin_to_dec(bin2)

def check_halt(curr_instr,pc):
    """ 
    Checks if the given instructions ia the halt instruction
    sig: str -> int -> bool
    """ 
    curr_addr = bin_to_instruction(decimal_to_binary(pc))[3:]
    halt_instr = "010" + curr_addr
    if curr_instr == halt_instr:
        return True

def sign_extend(num):
    """ 
    Extends the sign of a 7-bit instruction to a 16-bit instruction
    sig: int -> int
    """
    if num > 63:
        num += 65408
    return num

def mem_addr(regnum,imm):
    """ 
    Calculates the appropriate memory address for the sw and lw instructions
    sig: int -> int -> int
    """
    num = regnum + sign_extend(bin_to_dec(imm))
    if num > 65535:
        num = num - 65536
    return bit16_to_bit13(num)

def determine_reg_amount(instruction):
    """ 
    Determines the amount of registers the instructions has
    sig: str -> int
    """
    opcode = instruction[0:3]
    if opcode == "000":
        return 3
    elif opcode == "010":
        return 0
    elif opcode == "011":
        return 0 
    else:
        return 2

def determine_three_reg_instruction(instruction):
    """ 
    Determines which 3 register instuction that is being executed and extracts registers
    sig: str -> str -> int -> int -> int
    """
    opcode = instruction[0:3]
    instr_reg1 = bin_to_dec(instruction[3:6])
    instr_reg2 = bin_to_dec(instruction[6:9])
    instr_reg3 = bin_to_dec(instruction[9:12])
    backcode = instruction[12:]
    instr = ""
    match backcode:
        case "0000":
            instr = "add"
        case "0001":
            instr = "sub"
        case "0010":
            instr = "or"
        case "0011":
            instr = "and"
        case "0100":
            instr = "slt"
        case "1000":
            instr = "jr"
        case _:
            instr = "undefined"

    return instr, instr_reg1,instr_reg2, instr_reg3

def determine_two_reg_instruction(instruction):
    """ 
    Determines which 2 register instuction that is being executed and extracts registers adn imm value
    sig: str -> str -> int -> int -> int
    """
    opcode = instruction[0:3]
    instr_reg1 = bin_to_dec(instruction[3:6])
    instr_reg2 = bin_to_dec(instruction[6:9])
    imm_val = instruction[9:16]
    instr = ""
    match opcode:
        case "001":
            instr = "addi"
        case "110":
            instr = "jeq"
        case "101":
            instr = "sw"
        case "100":
            instr = "lw"
        case "111":
            instr = "slti"
        case _:
            instr = "undefined"

    return instr, instr_reg1,instr_reg2, imm_val

def determine_zero_reg_instruction(instruction):
    """ 
    Determines which 0 register instuction that is being executed and extracts imm value
    sig: str -> str -> int
    """
    opcode = instruction[0:3]
    imm = bin_to_dec(instruction[3:])
    instr = ""
    match opcode:
        case "010":
            instr = "j"
        case "011":
            instr = "jal"
        case _:
            instr = "undefined"
    return instr, imm