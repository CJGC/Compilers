# -*- coding: utf-8 -*-
chain = r'hello\nmaster\n\t\"how\\are\nyou?\a'
escapes_not_b = r'nrt\"'
native_codes_not_b = {'n':'\n','r':'\r','t':'\t','\\':'\\','"':'"'}
pass_character,aux_string,index = False,"",0
# for index in range(0,len(chain)):
#     if pass_character:
#         pass_character = False
#         continue
#     if chain[index] == '\\':
#         if index+1 <= len(chain):
#             for C1 in escapes_not_b:
#                 if C1 == chain[index+1]:
#                     aux_string += native_codes_not_b.get(C1,'')
#                     pass_character = True
#                     break
#                 elif C1 == '"':
#                     print "Invalid character!"
#         else: print "Invalid character!"
#     else: aux_string+=chain[index]

hexadecimal_codes = {'a':'a','b':'b','c':'c','d':'d','e':'e','f':'f','A':'A','B':'B','C':'C','D':'D','E':'E','F':'F',
                    '0':'0','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8','9':'9'}
chain = r'hello\nmaster\n\t\"how\\are\nyou?\bap\n\bzz'
print "\bz0"
while index < len(chain):
    if chain[index] == '\\':
        forward_position = index+1
        if forward_position < len(chain):
            if chain[forward_position] == 'b':
                h_index = forward_position+1
                if hexadecimal_codes.get(chain[h_index],'') != '':
                    aux_string += chain[h_index]
                    h_index += 1
                    if hexadecimal_codes.get(chain[h_index],'') != '':
                        aux_string += chain[h_index]
                        index = h_index
                    else:
                        index+=1
                        print "HEXADECIMAL NOT FOUND! 2"
                else:
                    index+=1
                    print "HEXADECIMAL NOT FOUND! 1"
            else:
                for C1 in escapes_not_b:
                    if C1 == chain[forward_position]:
                        aux_string += native_codes_not_b.get(C1,'')
                        break
                    elif C1 == '"':
                        print "INVALID CHARACTER!"
                index = forward_position
        else: print "INVALID CHARACTER!"
    else: aux_string+=chain[index]
    index+=1

    # native_codes_not_b = {'n':'\n','r':'\r','t':'\t','\\':'\\','"':'"'}
    # index,aux_string = 0,""
    # while index < len(t.value):
    #     if t.value[index] == '\\':
    #         forward_position = index+1
    #         if forward_position < len(t.value):
    #             for C1 in escapes_not_b:
    #                 if C1 == t.value[forward_position]:
    #                     aux_string += native_codes_not_b.get(C1,'')
    #                     break
    #                 elif C1 == '"':
    #                     error(t.lexer.lineno,"BAD ESCAPE CODE!")
    #             index = forward_position
    #         else: error(t.lexer.lineno,"BAD ESCAPE CODE!")
    #     else: aux_string+=t.value[index]
    #     index+=1
    # t.value = aux_string

print aux_string
