REGISTERS = {
    "zero": "00000","ra": "00001","sp": "00010","gp": "00011","tp": "00100",
    "t0": "00101","t1": "00110","t2": "00111",
    "s0": "01000","fp": "01000","s1": "01001",
    "a0": "01010","a1": "01011","a2": "01100","a3": "01101",
    "a4": "01110","a5": "01111","a6": "10000","a7": "10001",
    "s2": "10010","s3": "10011","s4": "10100","s5": "10101",
    "s6": "10110","s7": "10111","s8": "11000","s9": "11001",
    "s10": "11010","s11": "11011",
    "t3": "11100","t4": "11101","t5": "11110","t6": "11111"
}
INSTRUCTIONS = {

    # R TYPE
    "add":  ["0110011","000","0000000"],
    "sub":  ["0110011","000","0100000"],
    "sll":  ["0110011","001","0000000"],
    "slt":  ["0110011","010","0000000"],
    "sltu": ["0110011","011","0000000"],
    "xor":  ["0110011","100","0000000"],
    "srl":  ["0110011","101","0000000"],
    "or":   ["0110011","110","0000000"],
    "and":  ["0110011","111","0000000"],

    # I TYPE
    "lw":   ["0000011","010"],
    "addi": ["0010011","000"],
    "sltiu":["0010011","011"],
    "jalr": ["1100111","000"],

    # S TYPE
    "sw":   ["0100011","010"],

    # B TYPE
    "beq":  ["1100011","000"],
    "bne":  ["1100011","001"],
    "blt":  ["1100011","100"],
    "bge":  ["1100011","101"],
    "bltu": ["1100011","110"],
    "bgeu": ["1100011","111"],

    # U TYPE
    "lui":   ["0110111"],
    "auipc": ["0010111"],

    # J TYPE
    "jal": ["1101111"]
}

# INSTRUCTION TYPE MAP

TYPE_MAP = {

    "add":"R","sub":"R","sll":"R","slt":"R","sltu":"R",
    "xor":"R","srl":"R","or":"R","and":"R",

    "lw":"I","addi":"I","sltiu":"I","jalr":"I",

    "sw":"S",

    "beq":"B","bne":"B","blt":"B","bge":"B","bltu":"B","bgeu":"B",

    "lui":"U","auipc":"U",

    "jal":"J"
}

# IMMEDIATE → BINARY

def to_binary(value, bits):

    value = int(value)

    if value < 0:
        value = (1 << bits) + value

    return format(value, f'0{bits}b')

def check_register(reg):
    if reg not in REGISTERS:
        raise Exception(f"Invalid register {reg}")

# R TYPE ENCODER

def encode_R(op, rd, rs1, rs2):

    check_register(rd)
    check_register(rs1)
    check_register(rs2)

    opcode, funct3, funct7 = INSTRUCTIONS[op]

    return (
        funct7 + REGISTERS[rs2] + REGISTERS[rs1] + funct3 + REGISTERS[rd] + opcode
    )

# I TYPE ENCODER

def encode_I(op, rd, rs1, imm):

    check_register(rd)
    check_register(rs1)

    opcode, funct3 = INSTRUCTIONS[op]

    imm_bin = to_binary(imm,12)

    return (
        imm_bin + REGISTERS[rs1] + funct3 + REGISTERS[rd] + opcode
    )


# S TYPE ENCODER

def encode_S(op, rs2, rs1, imm):

    check_register(rs1)
    check_register(rs2)

    opcode, funct3 = INSTRUCTIONS[op]

    imm_bin = to_binary(imm,12)

    imm_11_5 = imm_bin[:7]
    imm_4_0 = imm_bin[7:]

    return (
        imm_11_5 + REGISTERS[rs2] + REGISTERS[rs1] + funct3 + imm_4_0 + opcode
    )

# B TYPE ENCODER

def encode_B(op, rs1, rs2, imm):

    check_register(rs1)
    check_register(rs2)

    opcode, funct3 = INSTRUCTIONS[op]

    imm_bin = to_binary(imm,13)

    imm12 = imm_bin[0]
    imm10_5 = imm_bin[2:8]
    imm4_1 = imm_bin[8:12]
    imm11 = imm_bin[1]

    return (
        imm12 + imm10_5 + REGISTERS[rs2] + REGISTERS[rs1] +
        funct3 + imm4_1 + imm11 + opcode
    )
# U TYPE ENCODER

def encode_U(op, rd, imm):

    check_register(rd)

    opcode = INSTRUCTIONS[op][0]

    imm_bin = to_binary(imm,20)

    return (
        imm_bin + REGISTERS[rd] + opcode
    )

# J TYPE ENCODER

def encode_J(op, rd, imm):

    check_register(rd)

    opcode = INSTRUCTIONS[op][0]

    imm_bin = to_binary(imm,21)

    imm20 = imm_bin[0]
    imm19_12 = imm_bin[1:9]
    imm11 = imm_bin[9]
    imm10_1 = imm_bin[10:20]

    return (
        imm20 + imm10_1 + imm11 + imm19_12 + REGISTERS[rd] + opcode
    )

# MAIN ENCODER DISPATCH

def encode_instruction(inst):

    op = inst[0]
    inst_type = TYPE_MAP[op]

    if inst_type == "R":
        return encode_R(op, inst[1], inst[2], inst[3])

    elif inst_type == "I":

        if op == "jalr":
            return encode_I(op, inst[1], inst[3], inst[2])

        return encode_I(op, inst[1], inst[2], inst[3])

    elif inst_type == "S":
        return encode_S(op, inst[1], inst[2], inst[3])

    elif inst_type == "B":
        return encode_B(op, inst[1], inst[2], inst[3])

    elif inst_type == "U":
        return encode_U(op, inst[1], inst[2])

    elif inst_type == "J":
        return encode_J(op, inst[1], inst[2])

    else:
        raise Exception("Unknown instruction")

def parse_R(temp_lines):
    return [temp_lines[0], temp_lines[1], temp_lines[2], temp_lines[3]]

def parse_I(temp_lines):
    return [temp_lines[0], temp_lines[1], temp_lines[2], temp_lines[3]]

def parse_S(temp_lines):
    return [temp_lines[0], temp_lines[1], temp_lines[2], temp_lines[3]]

def parse_B(temp_lines):
    return [temp_lines[0], temp_lines[1], temp_lines[2], temp_lines[3]]

def parse_U(temp_lines):
    return [temp_lines[0], temp_lines[1], temp_lines[2]]

def parse_J(temp_lines):
    return [temp_lines[0], temp_lines[1], temp_lines[2]]


def reader_parser(file):
    temp_lines = [] 

    with open(file) as f: 
        for line in f:
            line = line.split('#')[0].strip()

            if line == "": 
                continue

            if ':' in line:
                parts = line.split(':', 1)
                label = parts[0].strip() + ':'
                temp_lines.append([label]) 
                line = parts[1].strip()    
                if line == "": 
                    continue

            line = line.replace(",", " ")
            line = line.replace("(", " ")
            line = line.replace(")", " ")

            parsed_parts = line.split()

            if not parsed_parts:
                continue

            if parsed_parts[0] in ["lw", "sw"] and len(parsed_parts) == 4:
                parsed_parts = [parsed_parts[0], parsed_parts[1], parsed_parts[3], parsed_parts[2]]

            if parsed_parts[0] == "jalr" and len(parsed_parts) == 4:
                parsed_parts = [parsed_parts[0], parsed_parts[1], parsed_parts[3], parsed_parts[2]]

            temp_lines.append(parsed_parts)
    
            
    parsed_program = []

    for line in temp_lines:
            
        opcode = line[0]
        
        if opcode.endswith(":"):
            parsed_program.append(line)
            continue    
        
        inst_type = TYPE_MAP.get(opcode)

        if inst_type is None:
            raise Exception(f"Invalid instruction: {opcode}")

        if TYPE_MAP[opcode] == "R":
            parsed_program.append(parse_R(line))

        elif TYPE_MAP[opcode] == "I":
            parsed_program.append(parse_I(line))

        elif TYPE_MAP[opcode] == "S":
            parsed_program.append(parse_S(line))

        elif TYPE_MAP[opcode] == "B":
            parsed_program.append(parse_B(line))

        elif TYPE_MAP[opcode] == "U":
            parsed_program.append(parse_U(line))

        elif TYPE_MAP[opcode] == "J":
            parsed_program.append(parse_J(line))

        else:
            raise Exception("Invalid instruction")

    return parsed_program



def two_pass_assembler(parsed_lines):
    table = {}
    pc = 0
    inst_only = []


    for line in parsed_lines:
        if len(line) == 1 and line[0].endswith(':'):
            label_name = line[0][:-1] 
            table[label_name] = pc
        else:
            inst_only.append(line)
            pc += 4


    resolved_instructions = []
    pc = 0

    for inst in inst_only:
        op = inst[0]
        inst_type = TYPE_MAP.get(op)

        
        resolved_inst = list(inst)

        if inst_type == "B":
            
            tgt = resolved_inst[3]
            
            if tgt.lstrip('-').isdigit() == False:
                if tgt in table:
                    offset = table[tgt] - pc
                    resolved_inst[3] = str(offset)
                else:
                    raise Exception(f"error: label '{tgt}' not found.")

        elif inst_type == "J":
             
            
            tgt = resolved_inst[2]
            if tgt.lstrip('-').isdigit() == False:
                if tgt in table:
                    offset = table[tgt] - pc
                    resolved_inst[2] = str(offset)
                else:
                    raise Exception(f"error: label '{tgt}' not found.")

        resolved_instructions.append(resolved_inst)
        pc += 4

    return resolved_instructions


def check_virtual_halt(resolved_instructions):
    if len(resolved_instructions) == 0:
        raise Exception("Empty program")


    halt= 0
    for inst in resolved_instructions:
        if inst==["beq", "zero", "zero", "0"]:
            halt+= 1
    if halt==0:
        raise Exception("Missing Virtual Halt instruction")
    if resolved_instructions[-1]!=["beq", "zero", "zero", "0"]:
        raise Exception("Virtual Halt not being used as the last instruction")


def assemble(input_file, output_file):

    try:
        #parse assembly file
        parsed_lines=reader_parser(input_file)
    except Exception as e:
        print(f"Error during parsing:{e}")
        return

    try:
        #two-pass assembler
        resolved_instructions = two_pass_assembler(parsed_lines)
    except Exception as e:
        print(f"Error during label resolution:{e}")
        return

    try:
        # encoding instructions and writing binary output
        with open(output_file,'w') as out_file:
            for inst in resolved_instructions:
                try:
                    binary_str = encode_instruction(inst)
                    out_file.write(binary_str +'\n')
                except Exception as e:
                    print(f"Error encoding instruction {inst}:{e}")
                    return
    except Exception as e:
        print(f"Error while writing output: {e}")

import sys

input_file = sys.argv[1]
output_file = sys.argv[2]


assemble(input_file, output_file)


