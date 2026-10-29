   ; Start of the cycle
cycle:
        inc rcx ; Make it bigger
        jmp cycle ; Because why not?
                  ; Here's no cycle

one_style: test rax, rbx
another_style:
        test rax, rbx

one_style:
        db "Message"
another_style db "Message"
