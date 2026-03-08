addi a0,zero,4
addi t0,zero,0
addi t56,zero,1
addi sp,sp,-4
loop : add t0,t0,t1
addi t1,t1,1
slt t2,t1,a0
bne t2,zero,loop
jal ra,double
addi sp,sp,-4
sw t0,0(sp)
beq zero,zero,end
double: add t0,t0,t0
jalr zero,ra,0
data_check: addi sp,sp,-4
sw zero,0(sp)
lw t2,0(sp)
add t3,t2,zero
bne t3,zero,error
end: addi sp,sp,-4
sw t0,0(sp)
beq zero,zero,0
error: addi t4,zero,1
beq zero,zero,end
