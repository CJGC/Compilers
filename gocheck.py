# gocheck.py
# coding: utf-8

import sys, re, string
from errors import error
from goast import *
import gotype
import golex

class SymbolTable(object):
        '''
        Clase que representa una tabla de símbolos.  Debe proporcionar
        funcionabilidad para agregar y buscar nodos asociados con
        identificadores.
        '''

        class SymbolDefinedError(Exception):
            '''
            Exception disparada cuando el codigo trara de agragar un símbolo
            a la tabla de símbolos, y este ya esta definido
            '''
            pass

        class SymbolConflictError(Exception):
            '''
            Exception disparada cuando en el código se intenta redifinir tipos de datos
            de variables, funciones ya definidas
            '''
            pass

        # se agregó nameStatementAsociated como atributo
        def __init__(self, id_statement, parent=None):
            '''
            Crea una tabla de símbolos vacia con la tabla padre dada
            '''
            self.symtab = {} # tabla de símbolos para ese statement en cuestión
            self.parent = parent # si padre es != None, entonces es porque este statement en cuestión tiene padre y lo debe tener en cuenta
            if self.parent != None: # si ese statement es hijo (program, if, else, while -> statements que pueden contener otros statements con hijos, ejemplo if anidados)
                self.parent.children.append(self) # métalo como hijo, en la lista children de su padre
            self.children = [] # lista children que contendra los hijos de un statement si los llega a tener
            self.returnsSet = [] # conjunto de posibles returns que podría tener un statement en cuestión
            self.id_statement = id_statement

        def add(self, a, v): # a -> ID asociado al nodo, v -> Nodo
            '''
            Agrega un símbolo con el valor dado a la tabla de símbolos

            func foo(x:int, y:int)
            x:float;
            '''
            if a in self.symtab: # si el símbolo ya fue agregado a la tabla (es una redeclaración)
                if self.symtab[a].type.get_string() != v.type.get_string():  # si hubo una redifinición de tipo de dato (ejemplo int x, float x)
                    raise SymbolTable.SymbolConflictError() # lanza error relacionado
                else: # si no es, es porque hubo redifinición de variable (int x, float x)
                    raise SymbolTable.SymbolDefinedError() # lanzar error relacionado
            self.symtab[a] = v # agrega el símbolo a la tabla si no hubo errores

        def lookup(self, a): # a-> ID asociado a un nodo, que será usado para verificar si ya existe en la tabla de símbolos
            if a in self.symtab: # si existe el símbolo en la tabla de símbolos del statement actual que se está procesando
                return self.symtab[a] # retornelo
            else: # en caso contrario, mire si este statement actual, tiene padre.
                if self.parent != None: # si tiene padre, busque entonces en la tabla de símbolos del padre
                    return self.parent.lookup(a) # si está el símbolo en el padre retornelo
                else:
                    return None # si no está en el statement actual o en sus padres, entonces no ha sido declarado esa variable, constante o función (símbolo)

class CheckProgramVisitor(NodeVisitor):
        '''
        Clase de Revisión de programa.  Esta clase usa el patrón visitor
        como está descrito en goast.py.  Es necesario definir métodos de
        la forma visit_NodeName() para cada tipo de nodo del AST que se
        desee procesar.
        '''
        def __init__(self):
            # Inicializa la tabla de símbolos
            self.current = None # Atributo current que es la tabla de símbolos actual (None porque no ha sido creada aún para 'Program')

        def push_symtab(self,id_statement,node):
            self.current = SymbolTable(id_statement,self.current) # crea una tabla de símbolos y la asigna como actual
            node.symtab = self.current # guarda ésta tabla de símbolos en el nodo asociado (ver goast.py AST attributes)

        def pop_symbol(self):
            self.current = self.current.parent # actualiza como tabla de símbolos actual, la tabla del padre asociado del nodo actual, (por ejemplo if's anidados)

        def visit_Program(self,node):
            self.push_symtab('program',node) # el segundo parámetro es el nombre del nodo con el que se asociará la tabla de símbolos
            # Agrega nombre de tipos incorporados ((int, float, string) a la  tabla de símbolos
            node.symtab.add("int",gotype.int_type)
            node.symtab.add("float",gotype.float_type)
            node.symtab.add("string",gotype.string_type)
            node.symtab.add("bool",gotype.boolean_type)

            # 1. Visita todas las declaraciones (statements)
            # 2. Registra la tabla de símbolos asociada
            self.visit(node.program)
            # presentar posibles mensajes de error por returns en program
            self.check_returns(node.symtab.returnsSet)
            # presentar posibles mensajes de error por returns en statements inválidos
            self.check_returns_invalid_statements(node.symtab)

        def visit_IfStatement(self, node):
            self.visit(node.condition)
            if not node.condition.type == gotype.boolean_type:
                error(node.lineno,"Error, expresión booleana no válida")
            self.visit(node.then_b)
            if node.else_b:
                self.visit(node.else_b)

        def visit_WhileStatement(self,node):
            self.visit(node.condition)
            if not node.condition.type == gotype.boolean_type:
                error(node.lineno,"Error, expresión booleana no válida")
            self.visit(node.body)

        def visit_UnaryOp(self, node):
            node.type = None # tipo None por defecto
            self.visit(node.left)
            if not node.left.type:
                error(node.lineno,"Error, expresión unaria no debe ser nula")
            # 1. Asegúrese que la operación es compatible con el tipo
            elif not golex.operators[node.op] in node.left.type.un_ops:
                error(node.lineno,"Error, expresión no soporta el operador unario '%s'" % node.op)
            # 2. Ajuste el tipo resultante al mismo del operando
            else: node.type = node.left.type

        def visit_BinaryOp(self, node):
            self.visit(node.left)
            self.visit(node.right)
            node.type = None # tipo None por defecto
            # 1. Asegúrese que los operandos left y right tienen el mismo tipo
            if not node.left.type == node.right.type:
                error(node.lineno,"Error, las expresiones del operador deben ser del mismo tipo")
            elif node.left.type == None:
                error(node.lineno,"Error, las expresiones del operador no deben ser valores nulos")
            # 2. Asegúrese que la operación está soportada
            elif not golex.operators[node.op] in node.left.type.bin_ops:
                error(node.lineno,"Error, operación '%s' no soportada con los tipos de las expresiones" % node.op)
            # 3. Asigne el tipo resultante
            else: node.type = node.left.type

        def visit_AssignmentStatement(self,node):
            # 1. Asegúrese que la localización de la asignación está definida
            sym = self.current.lookup(node.location.id) # se cambia symtab a current (busca en la tabla de símbolos si location ya habia sido declarada)
            if sym == None:
                error(node.lineno,"Error, el símbolo '%s' no ha sido declarado"%node.location.id)
            # 2. Revise que la asignación es permitida, pe. sym no es una constante
            if isinstance(sym,ConstDeclaration):
                error(node.lineno,"Error, el símbolo '%s' es constante, su valor no se puede cambiar"%node.location.id)
            # 3. Revise que los tipos coincidan.
            if sym != None and not isinstance(sym,ConstDeclaration): # si está declaro y no es constante
                if isinstance(node.value, RelationalOp):
                    error(node.lineno,"Error, no debe haber operador relacional en una asignación")
                    return
                self.visit(node.value)
                if not node.value.type: # si el valor no tiene tipo
                    error(node.lineno,"Error, no se puede asignar un valor nulo")
                elif sym.type != node.value.type: # si difiere el tipo del valor del símbolo
                    error(node.lineno,"Error, la asignación no concuerda con el tipo del símbolo '%s'"%sym.typename.id)

        def visit_ConstDeclaration(self,node):
            # 1. Revise que el nombre de la constante no se ha definido
            if self.current.lookup(node.id):
                error(node.lineno, "Error, el símbolo '%s' ya se ha declarado" % node.id)
            # 2. Agrege una entrada a la tabla de símbolos
            else:
                if isinstance(node.value,RelationalOp):
                    error(node.lineno,"Error, no debe haber operador relacional en la declaración de una constante")
                    return
                self.visit(node.value)
                if not node.value.type:
                    error(node.lineno, "Error, el símbolo '%s' no puede recibir un valor nulo" % node.id)
                else:
                    node.type = node.value.type # crea un atributo type que almacena el tipo definido en el objeto Literal (ver visit_Literal)
                    self.current.add(node.id, node)

        def visit_VarDeclaration(self,node):
            self.visit(node.typename) # comprobar que el tipo de dato fue escrito correctamente
            if not node.typename.type: return # si el tipo de la variable no está correctamente definido, no compruebe nada más
            # 1. Revise que el nombre de la variable no se ha definido
            if self.current.lookup(node.id): # se cambió symtab como current (current contiene la tabla de símbolos de program, y mira si la variable ya está en la tabla)
                error(node.lineno, "Error, el símbolo '%s' ya se ha declarado" % node.id)
            # 2. Agrege la entrada a la tabla de símbolos
            else:
            # 3. Revise que el tipo de la expresión (si lo hay) es el mismo
                if node.value != None: # si en la decaración hay una asignación
                    if isinstance(node.value,RelationalOp):
                        error(node.lineno,"Error, no debe haber operador relacional en declaración de variable")
                        return
                    self.visit(node.value)
                    if node.value.type == None: # si el valor de la derecha es de tipo nulo
                        error(node.lineno,"Error, el símbolo '%s' no puede recibir un valor nulo" % node.id)
                    elif node.typename.id != node.value.type.name: # si el tipo de la derecha no concuerda con el de la variable
                        error(node.lineno,"Error, el valor no concuerda con el tipo del símbolo '%s'" % node.typename.id)
                    else: # si el valor concuerda con el tipo de la variable, regístrela
                        node.type = node.value.type
                        self.current.add(node.id, node) # se cambió symtab por current (se agrega a la tabla de símbolos si no está)

                else: # si no hay asignación, entonces sólo guardela
                    node.type = node.typename.type
                    self.current.add(node.id,node)

        def visit_Typename(self,node):
            # 1. Revisar que el nombre de tipo es válido que es actualmente un tipo
            # Es necesario crear el node.type de un nodo parar que sus padres vallan definiendo este tipo y así pueda comprobar si no hay discrepancias de este tipo 'var a int = 3.0'
            node.type = self.current.lookup(node.id) # para comprobar si el nombre del tipo de dato proporcionado de un símbolo declarada previamente, si corresponda a un tipo de dato incorporado válido de minigo
            if not node.type:
                error(node.lineno,"Error, tipo '%s' no definido correctamente" % node.id)

        def visit_Location(self,node):
            # 1. Revisar que la localización es una variable válida o un valor constante
            sym = self.current.lookup(node.id)
            if sym == None:
                error(node.lineno,"Error, el símbolo '%s' no ha sido declarado" % node.id)
                node.type = sym
            # 2. Asigne el tipo de la localización al nodo
            if sym != None: node.type = sym.type # si sym fue declarado entonces deme su tipo

        def visit_LoadLocation(self,node):
            # 1. Revisar que Load localización cargada es válida.
            self.visit(node.name)
            # 2. Asignar el tipo apropiado
            node.type = node.name.type

        def visit_Literal(self,node):
            # Adjunte un tipo apropiado a la constante
            if isinstance(node.value,bool): # node.value es una instancia válida de python?
                node.type = self.current.lookup("bool") # se cambia symtab a current (crea el atributo type en el objeto Literal que almacena el objeto type nativo de go)
            elif isinstance(node.value,int):
                node.type = self.current.lookup("int") # se cambia symtab a current
            elif isinstance(node.value, float):
                node.type = self.current.lookup("float") # se cambia symtab a current
            elif isinstance(node.value, str):
                node.type = self.current.lookup("string") # se cambia symtab a current

        def visit_PrintStatement(self, node):
            self.visit(node.expr)
            if node.expr.type == None:
                error(node.lineno,"Error, la expresión que se intenta imprimir no puede ser nula")

        def visit_Extern(self, node):
            # registe el nombre de la función
            self.visit(node.func_prototype)
            # obtener el tipo retornado
            node.type = node.func_prototype.type

        def visit_FuncPrototype(self, node):
            node.type = None # tipo None por defecto
            if self.current.lookup(node.id):
                error(node.lineno,"Error, la función '%s' extern ya se ha declarado" % node.id)
            else:
                self.visit(node.typename)
                if node.typename.type != None:
                    self.current.add(node.id,node) # guardando el id de la función y el objeto
                    node.type = node.typename.type

                    # creando tabla de símbolos para extern función
                    self.push_symtab('extern',node)
                    node.symtab.add("int",gotype.int_type)
                    node.symtab.add("float",gotype.float_type)
                    node.symtab.add("string",gotype.string_type)
                    node.symtab.add("bool",gotype.boolean_type)

                    # registar parámetros en tabla de símbolos de la función extern
                    self.visit(node.parameters)

                    # entregar dominio
                    self.pop_symbol()

        def visit_Parameters(self, node):
            for p in node.param_decls:
                self.visit(p)

        def visit_ParamDecl(self, node):
            if not node.id in self.current.symtab: # consultar primero que un parámetro todavía no está en la tabla de símbolos
                self.visit(node.typename) # comprobar que el tipo fue escrito correctamente y es nativo de go
                node.type = node.typename.type # si no hubo problemas, definir el tipo nativo de go para el parámetro
                self.current.add(node.id,node) # finalmente registrar en la tabla de símbolos de la función el parámetro
            else:
                error(node.lineno,"Error, el parámetro ya fue declarado")

        def visit_Group(self, node):
            self.visit(node.expression)
            node.type = node.expression.type

        def visit_RelationalOp(self, node):
            self.visit(node.left)
            self.visit(node.right)
            node.type = None # tipo None por defecto
            if not node.left.type == node.right.type:
                error(node.lineno,"Error, expresiones de relación no son del mismo tipo")
            elif node.left.type == None:
                error(node.lineno,"Error, expresiones de relación no deben ser nulos")
            elif not golex.operators[node.op] in node.left.type.bin_ops:
                error(node.lineno,"Error, expresiones de relación no tienen soporte con el operador '%s'"%node.op)
            else: node.type = self.current.lookup('bool')

        def visit_FunCall(self, node):
            node.type = None # tipo None por defecto
            # 1. comprobar que la función fue declarada previamente
            sym = self.current.lookup(node.id)
            # 2. comprobar parámetros en la llamada si sym es instancia válida de alguna función
            if isinstance(sym,FuncDeclaration) or isinstance(sym,FuncPrototype):
                node.type = sym.type # en llamada a función hay que saber el tipo que retorna esta función
                node.params.func = sym #dando el objeto función asociado a los parámetros en la llamada de la función
                node.params.lineno = node.lineno # dando el número de línea correspondiente
                self.visit(node.params)
            else: error(node.lineno,"Error, llamada a función '%s' no declarada" % node.id)

        def visit_ExprList(self, node):
            if len(node.expressions) != len(node.func.parameters.param_decls):
                error(node.lineno,"Error, la cantidad de parámetros que se están pasando en llamada a función, no concuerda con la cantidad con la que fue definida")
            else:
                for expr, param in zip(node.expressions,node.func.parameters.param_decls):
                    self.visit(expr)
                    #if not isinstance(expr,Empty):
                    if expr.type != param.type:
                        error(node.lineno,"Error, no concuerdan todos los tipos de los parámetros en llamada a la función")

        def visit_Empty(self, node):
            node.type = None

# ------------------------------------------------------------------------------------------------
#                                               Anexos
# ------------------------------------------------------------------------------------------------

        def check_returns_invalid_statements(self,symtab):
            for child in symtab.children: # comprueba cada tabla de símbolos hijo que tenga una tabla de símbolos padre
                if child.id_statement == 'if': # si en la tabla hay uno con if
                    self.check_returns(child.returnsSet) # comprobar el posible conjunto de returns en if
                    self.check_returns_invalid_statements(child)
                if child.id_statement == 'while':
                    self.check_returns(child.returnsSet)
                    self.check_returns_invalid_statements(child)

        def check_returns(self,_set):
            if len(_set) != 0:
                for return_ste in _set:
                    error(return_ste.lineno,"Error, el return debe estar dentro del cuerpo de una función")

        def make_Symtab_statements(self,id_statement,node):
            self.push_symtab(id_statement,node) # crear la tabla de símbolos para statements y configurar current con esa tabla
            # establecer los tipos nativos de go en la nueva tabla de símbolos
            node.symtab.add("int",gotype.int_type)
            node.symtab.add("float",gotype.float_type)
            node.symtab.add("string",gotype.string_type)
            node.symtab.add("bool",gotype.boolean_type)
            self.visit(node.statements) # visitar cada uno de los statements internos
            self.pop_symbol() # finalmente una vez que haya sido visitado los statements, actualize a la tabla de símbolos de program

        def visit_ThenIf(self, node):
            self.make_Symtab_statements('if',node)

        def visit_ThenElse(self,node):
            self.make_Symtab_statements('else',node)

        def visit_FuncDeclaration(self,node):
            node.type = None # tipo None por defecto
            # 1. comprobar si el tipo que retorna (si existe) es nativo de go
            if not isinstance(node.typename,Empty):
                self.visit(node.typename)
                node.type = node.typename.type

            # 2. comprobar que la función no esté definida antes
            if self.current.lookup(node.id):
                error(node.lineno, "La función %s ya se ha declarado antes" % node.id)
            else:
                self.current.add(node.id,node) # guardando el id de la función y el objeto en la tabla de su padre

            # 3. crear tabla de símbolos para el cuerpo de la función
                self.push_symtab('function',node)
                node.symtab.add("int",gotype.int_type)
                node.symtab.add("float",gotype.float_type)
                node.symtab.add("string",gotype.string_type)
                node.symtab.add("bool",gotype.boolean_type)

            # 4. comprobar parámetros de función y anexarlos a la tabla de símbolos
                self.visit(node.parameters)

            # 5. comprobar cuerpo de la función
                self.visit(node.statements)

            # 6. comprobar returns asociados
                # comprobar los return propios del cuerpo de la función
                self.check_returns_on_func(self.current.returnsSet,node)
                # comprobar los return dentro de los statements con tabla de símbolos
                self.check_returns_on_statements_on_func(self.current,node)

            # 7. entregar dominio a tabla de símbolos program
                self.pop_symbol()

        def check_returns_on_statements_on_func(self,symtab,node):
            for child in symtab.children:
                self.check_returns_on_func(child.returnsSet,node)
                self.check_returns_on_statements_on_func(child,node)

        def check_returns_on_func(self,_set,node):
            for return_ste in _set:
                if not node.type: # Si la función no tiene un tipo definido
                    error(return_ste.lineno,"Error, se está estableciendo un return dentro de una función que no devuelve nada")
                elif return_ste.type != node.type: # si el tipo que retorna no concuerda con el definido en la función
                    error(return_ste.lineno,"Error, el tipo del return no concuerda con el tipo definido de la función")

        def visit_ReturnStatement(self,node):
            self.visit(node.expression) # visitand la expression para saber que tipo retorna
            node.type = node.expression.type # capturando el tipo que devuelve la expresión del return
            self.current.returnsSet.append(node) # concatenando el return al statement asociado

        def visit_Group(self,node):
            self.visit(node.expression)
            node.type = node.expression.type

        def visit_WhileBody(self,node):
            self.make_Symtab_statements('while',node)

        def visit_FuncBody(self,node):
            if not isinstance(node.statements,Empty):
                self.visit(node.statements)

# ----------------------------------------------------------------------
#                       NO MODIFICAR NADA DE LO DE ABAJO
# ----------------------------------------------------------------------

def check_program(node):
    '''
    Comprueba el programa suministrado (en forma de un AST)
    '''
    checker = CheckProgramVisitor()
    checker.visit(node)

def main():
    import goparser
    import sys
    from errors import subscribe_errors
    lexer = golex.make_lexer()
    parser = goparser.make_parser()
    with subscribe_errors(lambda msg: sys.stdout.write(msg+"\n")):
            program = parser.parse(open(sys.argv[1]).read())
            # Revisa el programa
            check_program(program)

if __name__ == '__main__':
        main()
