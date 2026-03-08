addi sp, zero, 380
addi s0, zero, 1
srl s0, s0, s0
addi s0, s0, 1
addi t6, zero, 16
addi t5, zero, 0
shift_loop: add s0, s0, s0
addi t5, t5, 1
bne t5, t6, shift_loop
addi s1, zero, 7
addi s2, zero, 1
addi s3, zero, 1
addi s4, zero, 2
addi t0, zero, 0
sw s2, 0(s0)
addi t0, t0, 4
sw s3, 0(s0)
addi t0, t0, 4
loop: beq s4,s1,exit
add t1, s2, s3
add t2, s0, t0
sw t1, 0(t2)
addi t0, t0, 4
add s2, s3, zero
add s3, t1, zero
addi s4, s4, 1
beq zero,zero,loop
exit: beq zero,zero,0