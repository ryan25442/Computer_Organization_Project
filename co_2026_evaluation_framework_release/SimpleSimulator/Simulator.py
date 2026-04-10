import sys

# LOADER 
def loader(filename):
    instructions = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                instructions.append(line)
    return instructions


# FETCH 
def fetcher(instructions, pc):
    if pc % 4 != 0:
        raise Exception("PC not aligned")
    idx = pc // 4
    if idx < 0 or idx >= len(instructions):
        raise Exception("PC out of bounds")
    return instructions[idx]

def bin_to_int(b):
    if b[0] == '1':
        return int(b, 2) - (1 << len(b))
    return int(b, 2)

def to_signed(x):
    return x if x < 0x80000000 else x - 0x100000000

def to_bin32(x):
    return format(x & 0xFFFFFFFF, '032b')


# DECODE 
def decode(instr):
    if not all(c in "01" for c in instr):
        raise Exception("Invalid binary instruction")
    if len(instr) != 32:
        raise Exception("Instruction must be 32 bits")

    d = {}

    opcode = instr[25:32]
    funct3 = instr[17:20]
    funct7 = instr[0:7]

    rd  = int(instr[20:25], 2)
    rs1 = int(instr[12:17], 2)
    rs2 = int(instr[7:12], 2)

    d["opcode"] = opcode
    d["funct3"] = funct3
    d["funct7"] = funct7
    d["rd"] = rd
    d["rs1"] = rs1
    d["rs2"] = rs2

    if opcode == "0110011":
        d["type"] = "R"
        if funct3 == "000":
            if funct7 == "0000000":
                d["inst"] = "add"
            elif funct7 == "0100000":
                d["inst"] = "sub"
        elif funct3 == "001":
            d["inst"] = "sll"
        elif funct3 == "010":
            d["inst"] = "slt"
        elif funct3 == "011":
            d["inst"] = "sltu"
        elif funct3 == "100":
            d["inst"] = "xor"
        elif funct3 == "101":
            d["inst"] = "srl"
        elif funct3 == "110":
            d["inst"] = "or"
        elif funct3 == "111":
            d["inst"] = "and"
        if "inst" not in d:
            raise Exception("Invalid R-type")

    elif opcode in ["0010011", "0000011", "1100111"]:
        d["type"] = "I"
        d["imm"] = bin_to_int(instr[0:12])

        if opcode == "0010011":
            if funct3 == "000":
                d["inst"] = "addi"
            elif funct3 == "011":
                d["inst"] = "sltiu"
        elif opcode == "0000011":
            if funct3 == "010":
                d["inst"] = "lw"
        elif opcode == "1100111":
            d["inst"] = "jalr"

        if "inst" not in d:
            raise Exception("Invalid I-type")

    elif opcode == "0100011":
        d["type"] = "S"
        imm = instr[0:7] + instr[20:25]
        d["imm"] = bin_to_int(imm)
        if funct3 == "010":
            d["inst"] = "sw"
        else:
            raise Exception("Invalid S-type")

    elif opcode == "1100011":
        d["type"] = "B"
        imm = instr[0] + instr[24] + instr[1:7] + instr[20:24] + "0"
        d["imm"] = bin_to_int(imm)

        if funct3 == "000":
            d["inst"] = "beq"
        elif funct3 == "001":
            d["inst"] = "bne"
        elif funct3 == "100":
            d["inst"] = "blt"
        elif funct3 == "101":
            d["inst"] = "bge"
        elif funct3 == "110":
            d["inst"] = "bltu"
        elif funct3 == "111":
            d["inst"] = "bgeu"
        else:
            raise Exception("Invalid B-type")

    elif opcode in ["0110111", "0010111"]:
        d["type"] = "U"
        d["imm"] = int(instr[0:20], 2)
        d["inst"] = "lui" if opcode == "0110111" else "auipc"

    elif opcode == "1101111":
        d["type"] = "J"
        imm = instr[0] + instr[12:20] + instr[11] + instr[1:11] + "0"
        d["imm"] = bin_to_int(imm)
        d["inst"] = "jal"

    else:
        raise Exception("Invalid instruction")

    return d


DATA_BASE = 0x00010000
STACK_BASE = 0x00000100
STACK_TOP = 0x0000017F

data_mem = [0] * 1024
stack_mem = [0] * 32 


def load_word(addr):
    if DATA_BASE <= addr < DATA_BASE + 4096:
        return data_mem[(addr - DATA_BASE) // 4]
    elif STACK_BASE <= addr <= STACK_TOP:
        return stack_mem[(addr - STACK_BASE) // 4]
    else:
        raise Exception("Invalid memory access")


def store_word(addr, value):
    if DATA_BASE <= addr < DATA_BASE + 4096:
        data_mem[(addr - DATA_BASE) // 4] = value & 0xFFFFFFFF
    elif STACK_BASE <= addr <= STACK_TOP:
        stack_mem[(addr - STACK_BASE) // 4] = value & 0xFFFFFFFF
    else:
        raise Exception("Invalid memory access")


# EXECUTE 
def execute(d, reg, pc):
    inst = d["inst"]

    if d["type"] == "R":
        rs1, rs2, rd = d["rs1"], d["rs2"], d["rd"]

        if inst == "add":
            reg[rd] = reg[rs1] + reg[rs2]
        elif inst == "sub":
            reg[rd] = reg[rs1] - reg[rs2]
        elif inst == "and":
            reg[rd] = reg[rs1] & reg[rs2]
        elif inst == "or":
            reg[rd] = reg[rs1] | reg[rs2]
        elif inst == "xor":
            reg[rd] = reg[rs1] ^ reg[rs2]
        elif inst == "sll":
            reg[rd] = reg[rs1] << (reg[rs2] & 0x1F)
        elif inst == "slt":
            reg[rd] = int(to_signed(reg[rs1]) < to_signed(reg[rs2]))
        elif inst == "sltu":
            reg[rd] = int((reg[rs1] & 0xFFFFFFFF) < (reg[rs2] & 0xFFFFFFFF))
        elif inst == "srl":
            reg[rd] = (reg[rs1] & 0xFFFFFFFF) >> (reg[rs2] & 0x1F)

        reg[rd] &= 0xFFFFFFFF
        pc += 4

    elif d["type"] == "I":
        rs1, rd, imm = d["rs1"], d["rd"], d["imm"]

        if inst == "addi":
            reg[rd] = (reg[rs1] + imm) & 0xFFFFFFFF

        elif inst == "sltiu":
            reg[rd] = int((reg[rs1] & 0xFFFFFFFF) < (imm & 0xFFFFFFFF))
        elif inst == "lw":
            addr = (reg[rs1] + imm) & 0xFFFFFFFF
            reg[rd] = load_word(addr)

        elif inst == "jalr":
            temp = pc + 4
            pc = ((reg[rs1] + imm) & ~1) & 0xFFFFFFFF
            reg[rd] = temp & 0xFFFFFFFF
            reg[0] = 0
            return pc

        pc += 4

    elif d["type"] == "S":
        addr = (reg[d["rs1"]] + d["imm"]) & 0xFFFFFFFF
        store_word(addr, reg[d["rs2"]])
        pc += 4

    elif d["type"] == "B":
        rs1, rs2, imm = d["rs1"], d["rs2"], d["imm"]

        cond = False
        if d["inst"] == "beq":
            cond = reg[rs1] == reg[rs2]
        elif d["inst"] == "bne":
            cond = reg[rs1] != reg[rs2]
        elif d["inst"] == "blt":
            cond = to_signed(reg[rs1]) < to_signed(reg[rs2])
        elif d["inst"] == "bge":
            cond = to_signed(reg[rs1]) >= to_signed(reg[rs2])
        elif d["inst"] == "bltu":
            cond = (reg[rs1] & 0xFFFFFFFF) < (reg[rs2] & 0xFFFFFFFF)
        elif d["inst"] == "bgeu":
            cond = (reg[rs1] & 0xFFFFFFFF) >= (reg[rs2] & 0xFFFFFFFF)

        pc = pc + imm if cond else pc + 4

    elif d["type"] == "U":
        if d["inst"] == "lui":
            reg[d["rd"]] = (d["imm"] << 12) & 0xFFFFFFFF
        else:
            reg[d["rd"]] = (pc + (d["imm"] << 12)) & 0xFFFFFFFF
        pc += 4

    elif d["type"] == "J":
        reg[d["rd"]] = (pc + 4) & 0xFFFFFFFF
        pc += d["imm"]

    reg[0] = 0
    return pc


# HALT 
def check_halt(d):
    return d["opcode"] == "1100011" and d["rs1"] == 0 and d["rs2"] == 0 and d["imm"] == 0


# MAIN 
input_file = sys.argv[1]
output_file = sys.argv[2]

instructions = loader(input_file)
reg = [0] * 32
reg[2] = 0x0000017C  

pc = 0

with open(output_file, "w", newline='\n') as out:
    while True:
        instr = fetcher(instructions, pc)
        d = decode(instr)
        
        is_halt = check_halt(d)
        
        old_pc = pc

        if not is_halt:
            pc = execute(d, reg, pc)

        line = to_bin32(old_pc)
        for r in reg:
            line += " " + to_bin32(r)
        out.write(line + "\n")

        if is_halt:
            break

    addr = DATA_BASE
    for i in range(32):
        out.write(f"0x{addr:08x}:{to_bin32(data_mem[i])}\n")
        addr += 4
