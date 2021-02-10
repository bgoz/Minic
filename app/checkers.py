
from collections import ChainMap
from errores import error
from cast import *
from typesys import Type, FloatType, IntType, BoolType, CharType


class CheckProgramVisitor(NodeVisitor):
	'''
	Programa de comprobación de clase.  Esta clase usa el patrón
	visitor como se describe en cast.py.  Debe definir los métodos 
	del formulario visit_NodeName() para cada tipo de nodo AST que 
	desee procesar.  Usted puede necesitar ajustar los nombres de 
	los métodos aquí si has elegido diferentes nombres de nodo AST.
	'''
	def __init__(self):
		# Inicializa la tabla de simbolos
		self.symbols = { }
		
		# Tabla de símbolos temporal para guardar los símbolos globales 
		# al verificar una definición de función
		self.temp_symbols = { }
		
		# Aquí guardamos el tipo de retorno esperado al verificar una función
		self.expected_ret_type = None
		
		# Aquí guardamos el tipo de retorno observado al verificar una función
		self.current_ret_type = None
		
		# Una tabla de definicion de funciones
		self.functions = { }
		
		self.breakban = False
		self.voidfunc = False

		# Ponga los nombres de tipo incorporados en la tabla de símbolos
		# self.symbols.update(builtin_types)
		self.keywords = {t.name for t in Type.__subclasses__()}


	def visit_ArrayDeclaration(self, node):
		# Here we must update the symbols table with the new symbol
		node.type = None
		
		# Before anything, if we are declaring a variable with a name that is
		# a typename, then we must fail
		if node.name in self.keywords:
			error(node.lineno, f"Nombre '{node.name}' no es legal para declaracion de variable")
			return
			
		if node.name not in self.symbols:
			# First check that the datatype node is correct
			self.visit(node.datatype)
			
			if node.datatype.type:
				node.type = node.datatype.type
				self.symbols[node.name]= node


			else:
				error(node.lineno, f"Tipo desconocido  '{node.datatype.name}'")
		else:
			prev_lineno = self.symbols[node.name].lineno
			error(node.lineno, f"Nombre '{node.name}' ya ha sido definido en linea {prev_lineno}")

	def visit_ArrayLocalDeclaration(self,node):
		# Here we must update the symbols table with the new symbol
		node.type = None
		
		# Before anything, if we are declaring a variable with a name that is
		# a typename, then we must fail
		if node.name in self.keywords:
			error(node.lineno, f"Nombre '{node.name}' no es legal para declaracion de variable")
			return
			
		if node.name not in self.symbols:
			# First check that the datatype node is correct
			self.visit(node.datatype)
			
			if node.datatype.type:
				node.type = node.datatype.type
				self.symbols[node.name]= node


			else:
				error(node.lineno, f"Tipo desconocido  '{node.datatype.name}'")
		else:
			prev_lineno = self.symbols[node.name].lineno
			error(node.lineno, f"Nombre '{node.name}' ya ha sido definido en linea {prev_lineno}")

		
	def visit_VarDeclaration(self, node):
		# Here we must update the symbols table with the new symbol
		node.type = None
		
		# Before anything, if we are declaring a variable with a name that is
		# a typename, then we must fail
		if node.name in self.keywords:
			error(node.lineno, f"Nombre '{node.name}' no es legal para declaracion de variable")
			return
			
		if node.name not in self.symbols:
			# First check that the datatype node is correct
			self.visit(node.datatype)
			
			if node.datatype.type:
				# Before finishing, this var declaration may have an expression
				# to initialize it. If so, we must visit the node, and check
				# type errors
				if node.value:
					self.visit(node.value)
					
					if node.value.type: # If value has no type, then there was a previous error
						if node.value.type == node.datatype.type:
							# Great, the value type matches the variable type
							# declaration
							node.type = node.datatype.type
							self.symbols[node.name] = node
						else:
							error(node.lineno,
							f"Declarando variable '{node.name}' de tipo '{node.datatype.type.name}' pero asignada a expresion de tipo '{node.value.type.name}'")
				else:
					# There is no initialization, so we have everything needed
					# to save it into our symbols table
					node.type = node.datatype.type
					self.symbols[node.name] = node
			else:
				error(node.lineno, f"Tipo desconocido  '{node.datatype.name}'")
		else:
			prev_lineno = self.symbols[node.name].lineno
			error(node.lineno, f"Nombre '{node.name}' ya ha sido definido en linea {prev_lineno}")

	def visit_LocalDeclaration(self, node):
		# Here we must update the symbols table with the new symbol
		node.type = None
		
		# Before anything, if we are declaring a variable with a name that is
		# a typename, then we must fail
		if node.name in self.keywords:
			error(node.lineno, f"Nombre '{node.name}' no es legal para declaraciones locales")
			return
			
		if node.name not in self.symbols:
			# First check that the datatype node is correct
			self.visit(node.datatype)
			
			if node.datatype.type:
				# Before finishing, this var declaration may have an expression
				# to initialize it. If so, we must visit the node, and check
				# type errors
				if node.value:
					self.visit(node.value)
					
					if node.value.type: # If value has no type, then there was a previous error
						if node.value.type == node.datatype.type:
							# Great, the value type matches the variable type
							# declaration
							node.type = node.datatype.type
							self.symbols[node.name] = node
						else:
							error(node.lineno,
							f"Declarando variable local '{node.name}' de tipo '{node.datatype.type.name}' pero asignada a expresion de tipo '{node.value.type.name}'")
				else:
					# There is no initialization, so we have everything needed
					# to save it into our symbols table
					node.type = node.datatype.type
					self.symbols[node.name] = node
			else:
				error(node.lineno, f"Tipo desconocido  '{node.datatype.name}'")
		else:
			prev_lineno = self.symbols[node.name].lineno
			error(node.lineno, f"Nombre '{node.name}' ya ha sido definido en linea {prev_lineno}")
			
	def visit_ConstDeclaration(self, node):
		# For a declaration, you'll need to check that it isn't already defined.
		# You'll put the declaration into the symbol table so that it can be looked up later
		if node.name not in self.symbols:
			# First visit value node to extract its type
			self.visit(node.value)
			node.type = node.value.type
			self.symbols[node.name] = node
		else:
			prev_lineno = self.symbols[node.name].lineno
			error(node.lineno, f"Nombre '{node.name}' ha sido defino en linea {prev_lineno}")

	def visit_NewArrayExpression(self,node):
		self.visit(node.datatype)
		self.visit(node.expr)
		if node.datatype.name != node.expr.type.name:
			error(node.lineno, f"Tipo de dato no coincide.")





			
	def visit_IntegerLiteral(self, node):
		# For literals, you'll need to assign a type to the node and allow it to
		# propagate.  This type will work it's way through various operators
		node.type = IntType
		
	def visit_FloatLiteral(self, node):
		node.type = FloatType
		
	def visit_CharLiteral(self, node):
		node.type = CharType
		
	def visit_BoolLiteral(self, node):
		node.type = BoolType
		
	def visit_IfStatement(self, node):
		self.visit(node.condition)
		
		cond_type = node.condition.type
		if cond_type:
			if issubclass(node.condition.type, BoolType):
				self.visit(node.true_block)
				self.visit(node.false_block)
			else:
				error(node.lineno, f"'Condicion debe de ser de tipo 'bool' pero tiene tipo '{cond_type.name}'")
				
	def visit_WhileStatement(self, node):
		self.visit(node.condition)
		self.breakban = True 
		
		cond_type = node.condition.type
		if cond_type:
			if issubclass(node.condition.type, BoolType):
				self.visit(node.body)
				self.breakban = False
			else:
				error(node.lineno, f"'Condicion debe de ser de tipo 'bool' pero es de tipo '{cond_type.name}'")
				
	def visit_BinOp(self, node):
		# For operators, you need to visit each operand separately.  You'll
		# then need to make sure the types and operator are all compatible.
		self.visit(node.left)
		self.visit(node.right)
		
		node.type = None
		# Perform various checks here
		if node.left.type and node.right.type:
			op_type = node.left.type.binop_type(node.op, node.right.type)
			if not op_type:
				left_tname = node.left.type.name
				right_tname = node.right.type.name
				error(node.lineno, f"Operacion binaria '{left_tname} {node.op} {right_tname}' no soportada")
				
			node.type = op_type
			
	def visit_UnaryOp(self, node):
		# Check and propagate the type of the only operand
		self.visit(node.right)
		
		node.type = None
		if node.right.type:
			op_type = node.right.type.unaryop_type(node.op)
			if not op_type:
				right_tname = node.right.type.name
				error(node.lineno, f"Operacion unaria  '{node.op} {right_tname}' no soportada")
				
			node.type = op_type
			
	def visit_WriteLocation(self, node):
		# First visit the location definition to check that it is a valid
		# location
		self.visit(node.location)
		# Visit the value, to also get type information
		self.visit(node.value)
		
		node.type = None
		if hasattr(node.location, 'type') and hasattr(node.value, 'type'):
			loc_name = node.location.name
			if loc_name in self.symbols:
				if isinstance(self.symbols[loc_name], ArrayDeclaration):
					if node.location.size.value >= self.symbols[node.location.name].size or node.location.size.value < 0:
						error(node.lineno, f"'{loc_name}'  Fuera de rango de arreglo.")
				if isinstance(self.symbols[loc_name], ConstDeclaration):
				# Basically, if we are writting a to a location that was
				# declared as a constant, then this is an error
					error(node.lineno, f"No puedo escribir a una constante '{loc_name}'")
					return
			else:
				if isinstance(self.temp_symbols[loc_name], ArrayLocalDecl):
					if node.location.size.value >= self.temp_symbols[node.location.name].size or node.location.size.value < 0:
						error(node.lineno, f"'{loc_name}'  Fuera de rango de arreglo.")


			# If both have type information, then the type checking worked on
			# both branches
			if node.location.type == node.value.type:
				# Propagate the type
				node.type = node.value.type
			else:
				error(node.lineno,
				f"No puedo asignar tipo  '{node.value.type.name}' a variable  '{node.location.name}' de tipo '{node.location.type.name}'")
		else:
			''''''
			if hasattr(node.location.type,'name'):
				if node.location.type.name != node.value.datatype.name:
					error(node.lineno, f"No coincide el tipo de dato.")
				elif node.location.name in self.temp_symbols:
					self.temp_symbols[node.location.name].size=node.value.expr.value
				'''nodee=
				nodee.lista.append("df")
				print(nodee)'''
	def visit_BreakStatement(self,node):
		if self.breakban == False:
			error(node.lineno, f"El break esta fuera de un ciclo.")


	def visit_ReadLocation(self, node):
		# Associate a type name such as "int" with a Type object
		self.visit(node.location)
		loc_name = node.location.name

		if loc_name in self.symbols:
			if isinstance(self.symbols[loc_name], ArrayDeclaration):
				if node.location.size.value >= self.symbols[node.location.name].size.value or node.location.size.value < 0:
					error(node.lineno, f" '{loc_name}' Fuera de rango del arreglo.")

		if loc_name in self.temp_symbols:
			if isinstance(self.temp_symbols[loc_name], ArrayLocalDeclaration):
				if node.location.size.value >= self.temp_symbols[node.location.name].size.value or node.location.size.value < 0:
					error(node.lineno, f" '{loc_name}'Fuera del rango del arreglo. ")
	

		node.type = node.location.type
		
	def visit_SimpleLocation(self, node):
		if node.name in self.symbols:
			node.type = self.symbols[node.name].type
			
		elif node.name in self.temp_symbols:
			node.type = self.temp_symbols[node.name].type
		else:
			node.type = None
			error(node.lineno, f"Nombre '{node.name}' no fue definido")

	def visit_ArraySimpleLocation(self,node):
		if node.name not in self.symbols:
			node.type = None
			error(node.lineno, f" Nombre '{node.name}' no fue definido ")
		else:
			node.type = self.symbols[node.name].type
			
	def visit_SimpleType(self, node):
		# Associate a type name such as "int" with a Type object
		node.type = Type.get_by_name(node.name)
		if node.name == 'void':
			self.voidfunc = True;
		if node.type is None and self.voidfunc == False:
			error(node.lineno, f"Tipo invalido '{node.name}'")
			
	def visit_FuncParameter(self, node):
		self.visit(node.datatype)
		node.type = node.datatype.type
		
	def visit_ReturnStatement(self, node):
		self.visit(node.value)
		# Propagate return value type as a special property ret_type, only
		# to be checked at function declaration checking
		if self.expected_ret_type or self.voidfunc == True:
			if (node.value):
				if self.voidfunc == True:
					error(node.lineno, f'Return de funcion void debe ser un void')
				else:
					self.current_ret_type = node.value.type
					if node.value.type and node.value.type != self.expected_ret_type:
						error(node.lineno,f"Return de funcion '{self.expected_ret_type.name}'debe retornar una sentencia de valor de tipo'{self.expected_ret_type.name}'")
		else:
			error(node.lineno, "Instruccion return debe de estar dentro de una funcion")
			
	def visit_FuncDeclaration(self, node):
		if node.name in self.functions:
			prev_def = self.functions[node.name].lineno
			error(node.lineno, f"Funcion '{node.name}' ya definida en linea {prev_def}")
			
		self.visit(node.params)
		
		param_types_ok = all((param.type is not None for param in node.params))
		param_names = [param.name for param in node.params]
		param_names_ok = len(param_names) == len(set(param_names))
		if not param_names_ok:
			error(node.lineno, "Nombre de parametro duplicado en la definicion de funcion")
			
		self.visit(node.datatype)
		ret_type_ok = node.datatype.type is not None
		
		# Before visiting the function, body, we must change the symbol table
		# to a new one
		if self.temp_symbols:
			error(node.lineno, f"Declaracion de funcion anidada ilegal '{node.name}'")
		else:
			self.temp_symbols = self.symbols
			self.symbols = ChainMap(
			{param.name: param for param in node.params},
			self.temp_symbols
			)
			# Set the expected return value to observe
			self.expected_ret_type = node.datatype.type
			
			self.visit(node.body)
			
			if not self.current_ret_type:
				error(node.lineno, f"Funcion '{node.name}' no tiene fumcion de return")
			elif self.current_ret_type == self.expected_ret_type:
				# We must add the function declaration as available for
				# future calls
				self.functions[node.name] = node
				
			self.symbols = self.temp_symbols
			self.temp_symbols = { }
			self.expected_ret_type = None
			self.current_ret_type = None
			
	def visit_FuncCall(self, node):
		if node.name not in self.functions:
			error(node.lineno, f"Funcion '{node.name}' no esta declarada")
		else:
			# We must check that the argument list matches the function
			# parameters definition
			self.visit(node.arguments)
			
			arg_types = tuple([arg.type.name for arg in node.arguments])
			func = self.functions[node.name]
			expected_types = tuple([param.type.name for param in func.params])
			if arg_types != expected_types:
				error(node.lineno, f"Funcion '{node.name}' espera {expected_types}, pero fue llamada con {arg_types}")
				
			# The type of the function call is the return type of the function
			node.type = func.datatype.type		
# ----------------------------------------------------------------------
#                       NO MODIFIQUE NADA
# ----------------------------------------------------------------------

def check_program(ast):
	'''
	Revisa el programa proporcionado (en forma de un AST)
	'''
	checker = CheckProgramVisitor()
	checker.visit(ast)
	
def main():
	'''
	Programa principal. Usado para pruebas
	'''
	import sys
	from cparse import parse
	
	if len(sys.argv) < 2:
		sys.stderr.write('Usage: python3 -m minic.checkers filename\n')
		raise SystemExit(1)
		
	ast = parse(open(sys.argv[1]).read())
	check_program(ast)
	if '--show-types' in sys.argv:
		for depth, node in flatten(ast):
			print('%s: %s%s type: %s' % (getattr(node, 'lineno', None), ' '*(4*depth), node,
			getattr(node, 'type', None)))
			
if __name__ == '__main__':
	main()
