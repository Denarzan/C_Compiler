.386

.model flat, stdcall

option casemap:none

include D://masm32/include/windows.inc
include D://masm32/include/kernel32.inc
include D://masm32/include/user32.inc
include D://masm32/include/masm32.inc
include D://masm32/include/masm32rt.inc 

includelib D://masm32/lib/kernel32.lib
includelib D://masm32/lib/masm32.lib
includelib D://masm32/lib/user32.lib

main PROTO

.data

.code

start:
    invoke main
    fn MessageBox,0,str$(eax), "Lab6" ,MB_OK
    invoke ExitProcess, 0

geom_progression PROC
push ebp
mov ebp, esp

mov eax, 0
push eax
_1:
mov eax, [ebp + -4]
push eax
mov eax, [ebp + 8]
pop ebx
.if ebx < eax
    mov eax, 1
.else
    mov eax, 0
.endif
.if eax ==0
jmp _2
.else
mov eax, [ebp + 12]
push eax
mov eax, [ebp + 16]
pop ebx
mul ebx
mov [ebp + 16], eax

mov eax, [ebp + -4]
inc dword ptr[ebp + -4]

jmp _1
.endif
_2:

mov eax, [ebp + 16]
mov esp, ebp
pop ebp
ret
mov esp, ebp
pop ebp
ret
geom_progression ENDP
sum_geom_progression PROC
push ebp
mov ebp, esp
mov eax, [ebp + 16]
push eax

mov eax, 0
push eax
_3:
mov eax, [ebp + -8]
push eax
mov eax, [ebp + 8]
pop ebx
.if ebx < eax
    mov eax, 1
.else
    mov eax, 0
.endif
.if eax ==0
jmp _4
.else
mov eax, [ebp + 12]
push eax
mov eax, [ebp + 16]
pop ebx
mul ebx
mov [ebp + 16], eax
mov eax, [ebp + -4]
push eax
mov eax, [ebp + 16]
pop ebx
add eax,ebx
mov [ebp + -4], eax

mov eax, [ebp + -8]
inc dword ptr[ebp + -8]

jmp _3
.endif
_4:

mov eax, [ebp + -4]
mov esp, ebp
pop ebp
ret
mov esp, ebp
pop ebp
ret
sum_geom_progression ENDP
main PROC
push ebp
mov ebp, esp
mov eax, 2
push eax
mov eax, 2
push eax
mov eax, 2
push eax
call sum_geom_progression
add esp, 12

push eax
mov eax, [ebp + -4]
mov esp, ebp
pop ebp
ret
mov esp, ebp
pop ebp
ret
main ENDP

END start