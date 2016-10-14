# golex.py
# -*- coding: utf-8 -*-
'''
Programadores: Christhian Julián Gómez Castaño, Steven Valencia Zapata
Asignatura: Compiladores
Periodo académico: 2 semestre del 2016
Año: 2016
Tema: Analizador léxico para un miniGO
'''
# Errores que debe detectar el analizador
    #  lineno: Caracter ilegal 'c'
    #  lineno: Cadena sin terminar
    #  lineno: Comentario sin terminar
    #  lineno: Cadena de código de escape malo '\..'

# ----------------------------------------------------------------------
# El siguiente import carga una función error(lineno,msg) que se debe
# utilizar para informar de todos los mensajes de error emitidos por su
# lexer. Las pruebas unitarias y otras caracteristicas del compilador
# confiarán en esta función. Ver el archivo errors.py para más documentación
# acerca del mecanismo de manejo de errores.
from errors import error
# ----------------------------------------------------------------------
# Los lexers son definidos usando la librería ply.lex
from ply.lex import lex
# ----------------------------------------------------------------------
# Diccionario de stataments
reserved = {
    'if' : 'IF',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'print' : 'PRINT',
    'var' : 'VAR',
    'func' : 'FUNC',
    'const' : 'CONST',
    'extern' : 'EXTERN',
    'return' : 'RETURN',
    #'write' : 'WRITE',
    #'read' : 'READ',
}

# Lista de tipos
statament_reserved = [
    #'begin',
    #'and',
    #'not',
    #'or',
    #'int',
    #'float',
    #'bool',
    #'then',
    #'skip',
    #'end',
    #'break',
    #'do',
    #'for',
]

# Lista de tokens. Esta lista identifica la lista completa de nombres de
# token que deben ser reconocidos por su lexer.  No cambie ninguno de
# estos nombres. Si lo hace, se dañaran las pruebas unitarias.
#'COLON' -> must be on tokens
tokens = [
    # keyword
    'ID',

    # Operatores y delimitadores
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULE',
    'ASSIGN', 'SEMI', 'LPAREN', 'RPAREN', 'COMMA', 'LBRACKETS', 'RBRACKETS',
    'LBRACE', 'RBRACE',

    # Operadores lógicos
    'LT', 'LE', 'GT', 'GE', 'LAND', 'LOR', 'LNOT',
    'EQ', 'NE',

    # Literales
    'FLOAT_VALUE','INTEGER_VALUE', 'STRING_VALUE', 'BOOLEAN_VALUE',

] + list(reserved.values()) #statament_reserved
# ----------------------------------------------------------------------
# Ignora caracteres (whitespace)
t_ignore = ' \t\r'
# ----------------------------------------------------------------------
# Tokens operadores y delimitadores
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_MODULE    = r'\%'
t_ASSIGN    = r'='
#t_COLON     = r':'
t_SEMI      = r';'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACKETS = r'\['
t_RBRACKETS = r'\]'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_COMMA     = r','
# Tokens operadores lógicos
t_LT        = r'<'
t_LE        = r'<='
t_GT        = r'>'
t_GE        = r'>='
t_LAND      = r'&&'
t_LOR       = r'\|\|'
t_LNOT      = r'!'
t_EQ        = r'=='
t_NE        = r'!='
# ----------------------------------------------------------------------
# Tokens para literales, INTEGER, FLOAT, STRING.
#
#           Expresión regular para flotantes
# 1.23, 1.23e1, 1.23e+1, 1.23e-1, 123., .123, 1e1, 0.
def t_FLOAT_VALUE(t):
    r'\d*\.\d*([eE][\+-]?\d+)?|\d+[eE][\+-]?\d+'
    t.value = float(t.value)
    return t

#           Expresión regular para enteros
# 1234 (decimal), 01234 (octal), 0x1234 or 0X1234 (hex)
def t_INTEGER_VALUE(t):
    r'0[xX][a-fA-F0-9]+|0[0-7]+|\d+'
    t.value = int(t.value,0)
    return t

#           Expresión regular para strings
escapes_not_b = r'nrt\"'
def _replace_escape_codes(t):
    hex_codes = {'a':'a','b':'b','c':'c','d':'d','e':'e','f':'f','A':'A','B':'B','C':'C','D':'D','E':'E','F':'F','0':'0','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8','9':'9'}
    Not_b_codes = {'n':'\\n','r':'\\r','t':'\\t','\\':'\\\\','"':'\\"'}
    overflow,aux_string,index = False,"",0 # Cadena auxiliar e índice para recorrer la cadena vieja. overflow es una bandera que se activa en caso de desbordamiento.
    while index < len(t.value): # Mientras índice de cadena sea menor que el tamaño completo de la cadena.
        if t.value[index] == '\\': # Si detecta un \ en la cadena.
            forward_position = index+1  # Se adelanta una posición más allá del \.
            if forward_position < len(t.value): # Si esa posición a la qué se adelanta no desborda el tamaño máximo de la cadena.
                if t.value[forward_position] == 'b': # Si esa posición a la qué se adelanta es un código byte de caracter hh.
                    first_h, second_h = forward_position+1, forward_position+2 # asumo las dos posiciones hh
                    if first_h >= len(t.value) or second_h >= len(t.value): # Si almenos una de estas posiciones desborda el tamaño de cadena.
                        error(t.lexer.lineno,"BAD ESCAPE CHARACTER!")
                        overflow = True # Activa la bandera desbordamiento para suspención del while.
                    if overflow: break # Si hubo desbordamiento entonces detiene el análisis.
                    if t.value[first_h] == hex_codes.get(t.value[first_h],'') and t.value[second_h] == hex_codes.get(t.value[second_h],''): pass #Si ámbos caracteres h están en los hex, concatena sin error
                    else:  error(t.lexer.lineno,"BAD ESCAPE CHARACTER!")
                    aux_string+=t.value[first_h] # Concateno el primer caracter h.
                    aux_string+=t.value[second_h] # Concateno el segundo caracter h.
                    index = second_h # Actualizo el índice a la posición del segundo caracter h.
                else: # Si en la posición a la qué se adelanta no es código escape b, entonces podría ser uno de escape no b.
                    for C1 in escapes_not_b: # Recorre todos los códigos de escape no b.
                        if C1 == t.value[forward_position]: # Si coincide con el código de escape no b dado.
                            aux_string+=Not_b_codes.get(C1,'') # Concatene el código de caracter primitivo.
                            break   # Finalice el for.
                        elif C1 == '"': # Si no coincidió con ningun símbolo no b, entonces es un código de escape malo.
                            error(t.lexer.lineno,"BAD ESCAPE CHARACTER!")
                    index = forward_position # Actualiza índice a la posición del caracter de escape.
            else: error(t.lexer.lineno,"BAD ESCAPE CHARACTER!")
        else: aux_string+=t.value[index] # Si no se detectó un símbolo \ entonces concatenelo normalmente.
        index+=1 #Independiente de todos los casos índice aumenta uno.
    t.value = aux_string #Finalmente actualiza el contenido de t.value con lo códigos de caracter sustituidos.

def t_STRING_VALUE(t):
    r'".*"'
    # Convierte t.value dentro de una cadena con códigos de escape reemplazados por valores actuales.
    t.value = t.value[1:-1]
    _replace_escape_codes(t)    # Debe implementarse antes
    return t

def t_STRING_UNTERM(t):
    r'".*'
    error(t.lexer.lineno,"STRING UNTERM!")
    t.lexer.skip(1)

#           Expresión regular para Booleanos
def t_BOOLEAN_VALUE(t):
    r'true|false'
    return t
# ----------------------------------------------------------------------
# Identificadores y keywords.
# Coincida con un identificador primario. Los identificadores siguen las
# mismas reglas de Python.  Esto es, ellos inician con una letra o
# subrayado (_) y puede contener un numero arbitario de letras, digitos
# o subrayado desde de ella.
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    #r'[\w_][\w\d_]*'
    #print t.value
    t.type = reserved.get(t.value,'ID')
    #if t.value in statament_reserved:   t.type = str(t.value)
    #else:   t.type = reserved.get(t.type,'ID')
    return t

operators = {
    r'\+'  : "PLUS",
    r'-'  : "MINUS",
    r'\*'  : "TIMES",
    r'/'  : "DIVIDE",
    r'='  : "ASSIGN",
    r';'  : "SEMI",
    r'('  : "LPAREN",
    r')'  : "RPAREN",
    r','  : "COMMA",
    r'<'  : "LT",
    r'<=' : "LE",
    r'==' : "EQ",
    r'>=' : "GE",
    r'>'  : "GT",
    r'!=' : "NE",
    r'&&' : "LAND",
    r'\|\|' : "LOR",
    r'!'  : "LNOT"
}

# ----------------------------------------------------------------------
# Saltos de línea, Comentarios tipo C y C++, y error de comentario
# de tipo lenguaje C sin cerrar /* ...
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Comentarios estilo-C (/* ... */)
def t_COMMENT(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')

# Comentarios no cerrados estilo-C ERROR
def t_COMMENT_UNTERM(t):
    r'/\*(.|\n)*'
    error(t.lexer.lineno,"COMMENT UNTERM!")
    t.lexer.skip(1)

# Comentarios estilo-C++ (//...)
def t_CPPCOMMENT(t):
    r'//.*\n'
    t.lexer.lineno += 1

# ----------------------------------------------------------------------
# Caracteres ilegales (Manejador generico de errores)
def t_error(t):
    error(t.lexer.lineno,"ILLEGAL CHARACTER! %r" % t.value[0])
    t.lexer.skip(1)
# ----------------------------------------------------------------------
#                   NO CAMBIE NADA A PARTIR DE AQUI
# ----------------------------------------------------------------------
def make_lexer():
    '''
    Función de utilidad para crear el objeto lexer
    '''
    return lex()

if __name__ == '__main__':
    import sys
    from errors import subscribe_errors

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: %s filename\n" % sys.argv[0])
        raise SystemExit(1)


    lexer = make_lexer()
    with subscribe_errors(lambda msg: sys.stderr.write(msg+"\n")):
        lexer.input(open(sys.argv[1]).read())
        for tok in iter(lexer.token,None):
            sys.stdout.write("%s\n" % tok)
