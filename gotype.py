# gotype.py
# coding: utf-8
class GoType(object):
        '''
        Clase que representa un tipo en el lemguaje mini go.  Los tipos
        son declarados como instancias singleton de este tipo.
        '''
        def __init__(self, name, bin_ops=set(), un_ops=set()):
                '''
                Deberá ser implementada por usted y averiguar que almacenar
                '''
                self.name = name
                self.bin_ops = bin_ops
                self.un_ops = un_ops

int_type = GoType("int",
        set(('PLUS', 'MINUS', 'TIMES', 'DIVIDE','LE', 'LT', 'EQ', 'NE', 'GT', 'GE')),
        set(('PLUS', 'MINUS')),
        )
float_type = GoType("float",
        set(('PLUS', 'MINUS', 'TIMES', 'DIVIDE','LE', 'LT', 'EQ', 'NE', 'GT', 'GE')),
        set(('PLUS', 'MINUS')),
        )
string_type = GoType("string",
        set(('PLUS',)),
        set(),
        )
boolean_type = GoType("bool",
        set(('LAND', 'LOR', 'EQ', 'NE')),
        set(('LNOT',))
        )
