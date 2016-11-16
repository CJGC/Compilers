# gocheck.py
# coding: utf-8

import sys, re, string, types
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
            #print "Error la variable ya habia sido definida"

        class SymbolConflictError(Exception):
            '''
            Exception disparada cuando en el código se intenta redifinir tipos de datos
            de variables, funciones ya definidas
            '''
            pass
            #print "Error no se puede redefinir tipos de datos de variables, constantes o funciones ya previamente definidas"

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
            if self.symtab.has_key(a): # si el símbolo ya fue agregado a la tabla (es una redeclaración)
                if self.symtab[a].type.get_string() != v.type.get_string():  # si hubo una redifinición de tipo de dato (ejemplo int x, float x)
                    raise SymbolTable.SymbolConflictError() # lanza error relacionado y para ejecución
                else: # si no es porque hubo un redifinición típica de variable (int x, int x)
                    raise SymbolTable.SymbolDefinedError() # lanzar error relacionado y para ejecución
            self.symtab[a] = v # agrega el símbolo a la tabla si no hubo errores

        def lookup(self, a): # a-> ID asociado a un nodo, que será usado para verificar si ya existe en la tabla de símbolos
            if self.symtab.has_key(a): # si existe el símbolo en la tabla de símbolos del statement actual que se está procesando
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

        def check_returns_invalid_statements(self,symtab):
            for child in symtab.children: # comprueba cada tabla de símbolos hijo que tenga una tabla de símbolos padre
                if child.id_statement == 'if': # si en la tabla hay uno con if
                    self.check_returns(child.returnsSet) # comprobar el posible conjunto de returns en if
                    self.check_returns_invalid_statements(child)
                if child.id_statement == 'while':
                    self.check_returns(child.returnsSet)
                    self.check_returns_invalid_statements(child)

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
                assert None, "Expresión booleana no válida en la declaración if, error en la línea %s" % node.lineno
            else:
                self.visit(node.then_b)
                if node.else_b:
                    self.visit(node.else_b)

        def visit_WhileStatement(self,node):
            self.visit(node.condition)
            if not node.condition.type == gotype.boolean_type:
                assert None, "Expresión boolena no válida en la declaración del while, error en la línea %s" % node.lineno
            else:
                self.make_Symtab_statements('while',node)

        def visit_UnaryOp(self, node):
            self.visit(node.left)
            assert node.left.type, "Los operadores unarios no deben ser valores nulos, error en la línea %s" % node.lineno
            # 1. Asegúrese que la operación es compatible con el tipo
            if not golex.operators[node.op] in node.left.type.un_ops:
                assert None, "Operación unaria no soportada con este tipo, error en la línea %s" % node.lineno
            # 2. Ajuste el tipo resultante al mismo del operando
            node.type = node.left.type

        def visit_BinaryOp(self, node):
            self.visit(node.left)
            self.visit(node.right)
            # 1. Asegúrese que los operandos left y right tienen el mismo tipo
            if not node.left.type == node.right.type:
                assert None, "Los operandos binarios no son del mismo tipo, error en la línea %s" % node.lineno
            elif node.left.type == None:
                assert None, "Los operadores binarios no deben ser valores nulos, error en la línea %s" % node.lineno
            # 2. Asegúrese que la operación está soportada
            elif not golex.operators[node.op] in node.left.type.bin_ops:
                assert None, "Operación no soportada con los tipos dados en la expresión, error en la línea %s" % node.lineno
            # 3. Asigne el tipo resultante
            node.type = node.left.type

        def visit_AssignmentStatement(self,node):
            # 1. Asegúrese que la localización de la asignación está definida
            sym = self.current.lookup(node.location.id) # se cambia symtab a current (busca en la tabla de símbolos si location ya habia sido declarada)
            assert sym, "'%s' no ha sido declarado antes, error en la línea '%s'" % (node.location.id,node.lineno)
            # 2. Revise que la asignación es permitida, pe. sym no es una constante
            assert not(isinstance(sym,ConstDeclaration)) , "'%s' es una constante, su valor no puede cambiar, error en la línea %s" % (node.location.id,node.lineno)
            # 3. Revise que los tipos coincidan.
            self.visit(node.value)
            assert node.value.type, "El valor del lado derecho de la asignación no debe ser nulo, error en la línea %s" % node.lineno
            assert sym.type == node.value.type, "El tipo de dato del valor del lado derecho de la asignación, no coincide con el tipo de dato del símbolo definido '%s', error en la línea %s" % (sym.typename.id,node.lineno)

        def visit_ConstDeclaration(self,node):
            # 1. Revise que el nombre de la constante no se ha definido
            if self.current.lookup(node.id):
                error(node.lineno, "Error, la constante '%s' ya habia sido definida antes" % node.id)
                #assert None, "El símbolo '%s' ya habia sido definida antes, error en la línea '%s'" % (node.id,node.lineno)
            # 2. Agrege una entrada a la tabla de símbolos
            else:
                self.current.add(node.id, node)
            #print node.value.type
            self.visit(node.value)
            #print node.value.type
            assert node.value.type, "Las constantes no pueden recibir valores nulos, error en la línea %s" % node.lineno
            node.type = node.value.type # crea un atributo type que almacena el tipo definido en el objeto Literal (ver visit_Literal)

        def visit_VarDeclaration(self,node):
            self.visit(node.typename)
            node.type = node.typename.type
            # 1. Revise que el nombre de la variable no se ha definido
            if self.current.lookup(node.id): # se cambió symtab como current (current contiene la tabla de símbolos de program, y mira si la variable ya está en la tabla)
                error(node.lineno, "Error, la variable '%s' ya habia sido definido antes" % node.id)
                #assert None, "El símbolo '%s' ya habia sido definido antes, error en la línea '%s'" % (node.id,node.lineno)
            # 2. Agrege la entrada a la tabla de símbolos
            else:
                self.current.add(node.id, node) # se cambió symtab por current (se agrega a la tabla de símbolos si no está)
            # 3. Revise que el tipo de la expresión (si lo hay) es el mismo
            if node.value:
                self.visit(node.value)
                assert node.value.type, "Las variables no pueden recibir valores nulos, error en la línea %s" % node.lineno
                assert(node.typename.id == node.value.type.name), "El valor del lado derecho de la asignación no es valor que concuerde con el tipo de dato '%s' definido en la variable, error en la línea %s" % (node.typename.id ,node.value.lineno)
            # 4. Si no hay expresión, establecer un valor inicial para el valor
            else:
                node.value = None

        def visit_Typename(self,node):
            # 1. Revisar que el nombre de tipo es válido que es actualmente un tipo
            # Es necesario crear el node.type de un nodo parar que sus padres vallan definiendo este tipo y así pueda comprobar si no hay discrepancias de este tipo 'var a int = 3.0'
            node.type = self.current.lookup(node.id) # para comprobar si el nombre del tipo de dato proporcionado de un símbolo declarada previamente, si corresponda a un tipo de dato incorporado válido de minigo
            assert(node.type), "El tipo de dato utilizado '%s' no es tipo de dato nativo de go, error en la línea %s" % (node.id, node.lineno) # si el tipo de dato incorporado de la variable definida es válido, lo deja pasar, en caso contrario manda error

        def visit_Location(self,node):
            # 1. Revisar que la localización es una variable válida o un valor constante
            sym = self.current.lookup(node.id)
            assert(sym), "El símbolo '%s' no ha sido declarado previamente, error en la línea %s" % (node.id,node.lineno)
            # 2. Asigne el tipo de la localización al nodo
            node.type = sym.type

        def visit_LoadLocation(self,node):
            # 1. Revisar que Load localización cargada es válida.
            self.visit(node.name)
            # 2. Asignar el tipo apropiado
            node.type = node.name.type

        def visit_Literal(self,node):
            # Adjunte un tipo apropiado a la constante
            if isinstance(node.value, types.BooleanType): # node.value es una instancia válida de python?
                node.type = self.current.lookup("bool") # se cambia symtab a current (crea el atributo type en el objeto Literal que almacena el objeto type nativo de go)
            elif isinstance(node.value, types.IntType):
                node.type = self.current.lookup("int") # se cambia symtab a current
            elif isinstance(node.value, types.FloatType):
                node.type = self.current.lookup("float") # se cambia symtab a current
            elif isinstance(node.value, types.StringTypes):
                node.type = self.current.lookup("string") # se cambia symtab a current

        def visit_PrintStatement(self, node):
            self.visit(node.expr)
            assert node.expr.type, "El dato que se está imprimiendo no existe, error en la línea %s" % node.lineno

        def visit_Extern(self, node):
            # registe el nombre de la función
            self.visit(node.func_prototype)
            # obtener el tipo retornado
            node.type = node.func_prototype.type

        def visit_FuncPrototype(self, node):
            if self.current.lookup(node.id):
                assert(None), "La función extern ya había sido declarada antes, error en la línea %s" % node.lineno
            else:
                self.current.add(node.id,node) # guardando el id de la función y el objeto
            self.visit(node.typename)
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
            self.visit(node.typename) # comprobar que el tipo fue escrito correctamente y es nativo de go
            node.type = node.typename.type # si no hubo problemas, definir el tipo nativo de go para el parámetro
            self.current.add(node.id,node) # finalmente registrar en la tabla de símbolos de la función el parámetro

        def visit_Group(self, node):
            self.visit(node.expression)
            node.type = node.expression.type

        def visit_RelationalOp(self, node):
            self.visit(node.left)
            self.visit(node.right)
            if not node.left.type == node.right.type:
                assert None, "Operandos de relación no son del mismo tipo, error en la línea %s" % node.lineno
            elif node.left.type == None:
                assert None, "En expresiones relacionales no deben haber valores nulos, error en la línea %s" % node.lineno
            elif not golex.operators[node.op] in node.left.type.bin_ops:
                assert None, "Los operandos de la relación no tienen soporte con el operando '%s', error en la línea %s" % (node.op, node.lineno)
            node.type = self.current.lookup('bool')

        def visit_FunCall(self, node):
            # 1. comprobar que la función fue declarada previamente
            sym = self.current.lookup(node.id)
            if isinstance(sym,FuncDeclaration) or isinstance(sym,FuncPrototype): pass
            else: assert None, "Función no previamente declarada, error en la línea %s"% node.lineno
            # 2. comprobar parámetros en la llamada
            node.type = sym.type # en llamada a función hay que saber el tipo que retorna esta función
            node.params.func = sym #dando el objeto función asociado a los parámetros en la llamada de la función
            node.params.lineno = node.lineno # dando el número de línea correspondiente
            self.visit(node.params)

        def visit_ExprList(self, node):
            assert len(node.expressions) == len(node.func.parameters.param_decls), "La cantidad de parámetros en la llamada no coincide con la cantidad definidos, error en la línea %s" % node.lineno
            for expr, param in zip(node.expressions,node.func.parameters.param_decls):
                self.visit(expr)
                if not isinstance(expr,Empty):
                    assert expr.type == param.type, "No concuerdan todos los tipos de los parámetros en llamada a la función, error en la línea %s " % node.lineno

        def visit_Empty(self, node):
                pass

# ------------------------------------------------------------------------------------------------
#                                               Anexos
# ------------------------------------------------------------------------------------------------

        def check_returns(self,_set):
            if len(_set) != 0:
                for return_ste in _set:
                    assert None, "El return debe ser usado únicamente dentro de funciones, error en la línea %s" % return_ste.lineno

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
            # 1. comprobar si el tipo que retorna (si existe) es nativo de go
            if not isinstance(node.typename,Empty):
                self.visit(node.typename)
                node.type = node.typename.type
            else:
                node.type = None

            # 2. comprobar que la función no esté definida antes
            if self.current.lookup(node.id):
                #error(node.lineno, "La función %s ya había sido declarada antes" % node.id)
                assert None, "La función '%s' ya había sido definido antes, error en la línea '%s'" % (node.id,node.lineno)
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
            if len(self.current.returnsSet) == 0 and node.type != None:
                assert None, "La función debería contener almenos 'EN SU CUERPO' un retorno del tipo en la que fue definida, error en la línea %s" % node.lineno
            self.check_returns_on_func(self.current.returnsSet,node)
            # comprobar los return de los statements con tabla de símbolos contenidas en la función
            self.check_returns_on_statements_on_func(self.current,node)

            # 7. entregar dominio a tabla de símbolos program
            self.pop_symbol()

        def check_returns_on_statements_on_func(self,symtab,node):
            for child in symtab.children:
                self.check_returns_on_func(child.returnsSet,node)
                self.check_returns_on_statements_on_func(child,node)

        def check_returns_on_func(self,_set,node):
            for return_ste in _set:
                assert node.type, "Se está definiendo un retorno sin que la función deba devolver algo, error en la línea %s" % return_ste.lineno
                assert return_ste.type == node.type, "El valor del retorno de la función debe coincidir con el tipo de dato con la que fue definida, error en la línea %s" % return_ste.lineno

        def visit_ReturnStatement(self,node):
            self.visit(node.expression) # visitand la expression para saber que tipo retorna
            node.type = node.expression.type # capturando el tipo que devuelve la expresión del return
            self.current.returnsSet.append(node) # concatenando el return al statement asociado

        def visit_Group(self,node):
            self.visit(node.expression)
            node.type = node.expression.type
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
