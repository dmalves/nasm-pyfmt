global _start


section .text

   ;Starting point
_start:
mov rax,1 ;write(fd, buf, len)
mov rdi,1  ; fd
mov rsi, msg   ; buf
mov rdx,  msglen; len
  syscall

mov rax,60 ;exit(status)
mov rdi, 0
  syscall

section .data
msg    db "Hello world!",10
msglen equ $-msg
