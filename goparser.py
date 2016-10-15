# goparser.py# -*- coding: utf-8 -*-'''Proyecto 2:  Escribir un parser===============================En este proyecto, se escribe la estructura basica de una analizador parael lenguaje hoc. La forma BNF del lenguaje se describe a continuacion.Su tarea es escribir las reglas de análisis y construir el AST para estagramática usando PLY.program : statements        | emptystatements :  statements statement           |  statementstatement :  const_declaration          |  var_declaration          |  extern_declaration          |  assign_statement          |  print_statement          |  if_statementconst_declaration : CONST ID = expression SEMIvar_declaration : VAR ID typename SEMI                | VAR ID typename = expression SEMIextern_declaration : EXTERN func_prototype SEMIfunc_prototype : FUNC ID LPAREN parameters RPAREN typenameparameters : parameters , parm_declaration           | parm_declaration           | emptyparm_declaration : ID typenameassign_statement : location = expression SEMIprint_statement : PRINT expression SEMIexpression : + expression           | - expression           | expression + expression           | expression - expression           | expression * expression           | expression / expression           | ( expression )           | ID ( exprlist )           | location           | literalexprlist : exprlist , expression           | expression           | emptyliteral : INTEGER        | FLOAT        | STRINGlocation : IDtypename : IDempty    :Para hacer el proyecto, siga las instrucciones a continuación.'''# ----------------------------------------------------------------------# Los parsers son definidos usando el módulo yacc de PLY## Vea http://www.dabeaz.com/ply/ply.html#ply_nn23# ----------------------------------------------------------------------from ply import yacc# ----------------------------------------------------------------------# El siguiente import carga la funcion error(lineno, msg) que debe ser# usada para reportar todos los mensajes de error generados por su parser.# Las pruebas Unitarias y otras caracteristicas del compilador se basaran# en esta función.  vea el archivo errors.py para una mayor documentación# acerca del mecanismo de manejo de errores.from errors import error# ----------------------------------------------------------------------# Obtener la lista de token definidos en el módulo lexer.  Esto es# necesario con el fin de validar y construir la tabla de sintaxis.from golex import tokens# ----------------------------------------------------------------------# Obtener los nodos del AST.# Lea las instrucciones en hocast.pyfrom goast import *# ----------------------------------------------------------------------# Tabla de precedencia de operadores.  Los operadores deben de seguir# las mismas reglas de precedencia que Python.  Instrucciones que se# dan el el proyecto.# Vea http://www.dabeaz.com/ply/ply.html#ply_nn27precedence = (    ('left', 'LOR'),    ('left', 'LAND'),    ('nonassoc', 'LT', 'LE', 'EQ', 'GT', 'GE', 'NE'),    ('left', 'PLUS', "MINUS"),    ('right', 'UNARY'),  # operador ficticio para mantener la mas alta prioridad    ('left', "TIMES", "DIVIDE", "MODULE"),)# ----------------------------------------------------------------------# SU TAREA.  Traducir la forma BNF en la cadena de documentación mencionada# anteriormente dentro de una colección de funciones del parser.  Por# ejemplo, una regla tal como:##   program : statements## Se convierte en una función de Python de la forma:## def p_program(p):#      '''#      program : statements#      '''#      p[0] = Program(p[1])## Para los símbolos tales com '(' or '+', deberá reemplazarlos con el# nombre del correspondiente token tal como LPAREN o PLUS (si así lo# hizo en el lexer).## En el cuerpo de cada regla, cree un nodo apropiado del AST y asignelo# a p[0] como se muestró anteriormente.## Para el seguimiento del numero de linea, se debe asignar un numero de linea# para cada nodo del AST como corresponda.  Para ello, suguiero utilizar el# numero de línea del símbolo terminal mas cercano.  Por ejemplo:## def p_print_statement(p):#     '''#     print_statement: PRINT expr SEMI#     '''#     p[0] = PrintStatement(p[2],lineno=p.lineno(1))### EMPEZAR# =======# Las siguientes reglas gramaticales deben de darle una idea de como empezar.# Trate de correrlo con un archivo de prueba.# Se hizo uso de Program classdef p_program(p):    '''    program : statements        | empty    '''    p[0] = Program(p[1])def p_statements(p):    '''    statements :  statements statement    '''    p[0] = p[1]    p[0].append(p[2])def p_statements_1(p):    '''    statements :  statement    '''    p[0] = Statements([p[1]])# se agregó function declaration# se agregó return statement# se agregó function call statement# se agregó array_declaration statement# se agregó for_statement# se agregó short_var_declarationdef p_statement(p):    '''    statement :  const_declaration          |  var_declaration          |  short_var_declaration          |  array_declaration          |  extern_declaration          |  function_declaration          |  function_call_statement          |  assign_statement          |  print_statement          |  if_statement          |  while_statement          |  for_statement          |  return_statement    '''    p[0] = Statement(p[1])def p_const_declaration(p):    '''    const_declaration : CONST ID ASSIGN expression SEMI    '''    p[0] = ConstDeclaration(p[2],p[4])def p_var_declaration(p):    '''    var_declaration : VAR ID typename SEMI    '''    p[0] = VarDeclaration(p[2], p[3], None, lineno=p.lineno(2))def p_var_declaration_1(p):    '''    var_declaration : VAR ID typename ASSIGN expression SEMI    '''    p[0] = VarDeclaration(p[2], p[3], p[5])def p_extern_declaration(p):    '''    extern_declaration : EXTERN func_prototype SEMI    '''    p[0] = Extern(p[2])def p_func_prototype(p):    '''    func_prototype : FUNC ID LPAREN parameters RPAREN typename    '''    p[0] = FuncPrototype(p[2], p[4], p[6])def p_parameters(p):    '''    parameters : parameters COMMA parm_declaration    '''    p[0] = p[1]    p[0].append(p[3])def p_parameters_1(p):    '''    parameters : parm_declaration           | empty    '''    p[0] = Parameters([p[1]])def p_parm_declaration(p):    '''    parm_declaration : ID typename    '''    p[0] = ParamDecl(p[1], p[2])def p_assign_statement(p):    '''    assign_statement : location ASSIGN expression SEMI    '''    p[0] = AssignmentStatement(p[1], p[3])def p_print_statement(p):    '''    print_statement : PRINT expression SEMI    '''    p[0] = PrintStatement(p[2])def p_expression_unary(p):    '''    expression :  PLUS expression %prec UNARY           |  MINUS expression %prec UNARY           |  LNOT expression %prec UNARY    '''    p[0] = UnaryOp(p[1], p[2], lineno=p.lineno(1))def p_expression_binary(p):    '''    expression :  expression PLUS expression           | expression MINUS expression           | expression TIMES expression           | expression DIVIDE expression           | expression MODULE expression    '''    p[0] = BinaryOp(p[2], p[1], p[3])def p_expression_relation(p):    '''    expression : expression LE expression            | expression LT expression            | expression EQ expression            | expression NE expression            | expression GE expression            | expression GT expression            | expression LAND expression            | expression LOR expression    '''    p[0] = RelationalOp(p[2], p[1], p[3], lineno=p.lineno(2))def p_expression_group(p):    '''    expression : LPAREN expression RPAREN    '''    p[0] = Group(p[2])# Se renombró la regla 'expression_funcall' a 'function_call_statement'# SEMI token no estaba# El segundo parámetro [2] en FunCall fue cambiado a p[3]def p_function_call_statement(p):    '''    function_call_statement :  ID LPAREN exprlist RPAREN SEMI    '''    p[0] = FunCall(p[1], p[3])def p_if_statement(p):    '''    if_statement : IF expression LBRACE then_if RBRACE    '''    p[0] = IfStatement(p[2], p[4], None)def p_if_else_statement(p):    '''    if_statement : IF expression LBRACE then_if RBRACE ELSE LBRACE then_else RBRACE    '''    p[0] = IfStatement(p[2], p[4], p[8])def p_while_statement(p):    '''    while_statement : WHILE expression LBRACE body_statements RBRACE    '''    p[0] = WhileStatement(p[2], p[4])def p_expression_location(p):    '''    expression :  location    '''    p[0] = LoadLocation(p[1], lineno=p.lineno(1))# fue creada y usada la clase ExprLiteraldef p_expression_literal(p):    '''    expression :  literal    '''    p[0] = ExprLiteral(p[1])def p_exprlist(p):    '''    exprlist :  exprlist COMMA expression    '''    p[0] = p[1]    p[0].append(p[3])def p_exprlist_1(p):    '''    exprlist : expression           | empty    '''    p[0] = ExprList([p[1]])def p_literal(p):    '''    literal : INTEGER_VALUE            | FLOAT_VALUE            | STRING_VALUE            | BOOLEAN_VALUE    '''    p[0] = Literal(p[1],lineno=p.lineno(1))# fue creada y usada la clase Locationdef p_location(p):    '''    location : ID    '''    p[0] = Location(p[1])def p_typename(p):    '''    typename : ID    '''    p[0] = p[1]def p_empty(p):    '''    empty    :    '''# Usted debe implementar el resto de las reglas de la gramatica# a partir de aqui.def p_short_var_declaration(p):    '''    short_var_declaration : ID COLON ASSIGN expression SEMI    '''    p[0] = ShortVarDeclaration(p[1],p[4])def p_short_var_declaration_funcall(p):    '''    short_var_declaration : ID COLON ASSIGN function_call_statement    '''    p[0] = ShortVarDeclaration(p[1],p[4])def p_var_declaration_funcall(p):    '''    var_declaration : VAR ID typename ASSIGN function_call_statement    '''    p[0] = VarDeclaration(p[2], p[3], p[5])def p_return_statement(p):    '''    return_statement : RETURN expression SEMI    '''    p[0] = ReturnStatement(p[2])def p_return_statement_funcall(p):    '''    return_statement : RETURN function_call_statement    '''    p[0] = ReturnStatement(p[2])def p_function_declaration(p):    '''    function_declaration : func_prototype LBRACE body_statements RBRACE    '''    p[0] = Func_declaration(p[1],p[3])def p_func_prototype_1(p):    '''    func_prototype : FUNC ID LPAREN parameters RPAREN    '''    p[0] = FuncPrototype(p[2],p[4],None)def p_expression_array(p):    '''    expression : location LBRACKETS expression RBRACKETS    '''    p[0] = Expression_array(p[1],p[3])def p_parm_declaration_array(p):    '''    parm_declaration : ID typename LBRACKETS special_literal_array RBRACKETS    '''    p[0] = ParamDeclArray(p[1], p[2], p[4])def p_assign_statement_array_literal(p):    '''    assign_statement : location LBRACKETS special_literal_array RBRACKETS ASSIGN expression SEMI    '''    p[0] = AssignmentStatementArray(p[1], p[3], p[6])def p_assign_statement_array_location(p):    '''    assign_statement : location LBRACKETS location RBRACKETS ASSIGN expression SEMI    '''    p[0] = AssignmentStatementArray(p[1], p[3], p[6])def p_assign_statement_funcall(p):    '''    assign_statement : location ASSIGN function_call_statement    '''    p[0] = AssignmentStatement(p[1], p[3])def p_assign_statement_array_literal_funcall(p):    '''    assign_statement : location LBRACKETS special_literal_array RBRACKETS ASSIGN function_call_statement    '''    p[0] = AssignmentStatementArray(p[1], p[3], p[6])def p_assign_statement_array_location_funcall(p):    '''    assign_statement : location LBRACKETS location RBRACKETS ASSIGN function_call_statement    '''    p[0] = AssignmentStatementArray(p[1], p[3], p[6])def p_array_declaration(p):    '''    array_declaration : VAR ID typename LBRACKETS special_literal_array RBRACKETS SEMI    '''    p[0] = ArrayDeclaration(p[2],p[3],p[5])def p_print_statement_funcall(p):    '''    print_statement : PRINT function_call_statement    '''    p[0] = PrintStatement(p[2])def p_then_if(p):    '''    then_if : statements    '''    p[0] = ThenIf(p[1])def p_then_else(p):    '''    then_else : statements    '''    p[0] = ThenElse(p[1])def p_special_literal_array(p):    '''    special_literal_array : INTEGER_VALUE    '''    p[0] = SpecialLiteralArray(p[1])def p_for_statement(p):    '''    for_statement : FOR for_declaration SEMI for_expression SEMI for_assign_statement LBRACE body_statements RBRACE    '''    p[0] = ForStatement(p[2],p[4],p[6],p[8])def p_for_declaration(p):    '''    for_declaration : ID COLON ASSIGN expression    '''    p[0] = ForDeclaration(p[1], p[4])def p_for_expression_relation(p):    '''    for_expression : expression LE expression            | expression LT expression            | expression EQ expression            | expression NE expression            | expression GE expression            | expression GT expression            | expression LAND expression            | expression LOR expression    '''    p[0] = RelationalOp(p[2], p[1], p[3], lineno=p.lineno(2))def p_for_assign_statement(p):    '''    for_assign_statement : location ASSIGN expression                        | location PLUS ASSIGN expression                        | location MINUS ASSIGN expression                        | location TIMES ASSIGN expression                        | location DIVIDE ASSIGN expression                        | location PLUS PLUS                        | location MINUS MINUS    '''    if p[2] == '=':        p[0] = AssignmentStatement(p[1], p[3])    elif p[2] != '=' and p[3] == '=':        p[0] = AssignmentStatement(p[1], p[4])    else:        p[0] = AssignmentStatement(p[1], None)def p_body_statements(p):    '''    body_statements : statements    '''    p[0] = BodyStatements(p[1])# ----------------------------------------------------------------------# NO MODIFIQUE## capturar todos los errores.  La siguiente función es llamada si existe# una entrada mala. Vea http://www.dabeaz.com/ply/ply.html#ply_nn31def p_error(p):    if p:        error(p.lineno, "Error de sintaxis de entrada en token '%s'" % p.value)    else:        error("EOF","Error de sintaxis. No hay mas entrada.")# ----------------------------------------------------------------------#              NO MODIFIQUE NADA DE AQUI EN ADELANTE# ----------------------------------------------------------------------def make_parser():    parser = yacc.yacc()    return parserif __name__ == '__main__':    import golex    import sys    from errors import subscribe_errors    lexer = golex.make_lexer()    parser = make_parser()    with subscribe_errors(lambda msg: sys.stdout.write(msg+"\n")):        program = parser.parse(open(sys.argv[1]).read())    # Output the resulting parse tree structure    # for depth,node in flatten(program):    #     print("%s%s" % (" "*(4*depth),node))    dot = DotVisitor()    dot.visit(program)    print dot