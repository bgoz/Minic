
from collections import ChainMap
import cast

IR_TYPE_MAPPING = {
	'int': 'I',
	'float': 'F',
	'char': 'B',
	'bool': 'I'
}

OP_CODES = ChainMap({
	'mov': 'MOV',
	'+': 'ADD',
	'-': 'SUB',
	'*': 'MUL',
	'/': 'DIV',
	'&&': 'AND',
	'||': 'OR',
	'print': 'PRINT',
	'store': 'STORE',
	'var': 'VAR',
	'alloc': 'ALLOC', # Local allocation (inside functions)
	'load': 'LOAD',
	'label': 'LABEL',
	'cbranch': 'CBRANCH', # Conditional branch
	'branch': 'BRANCH',   # Unconditional branch,
	'call': 'CALL',
	'ret': 'RET'},
	dict.fromkeys(['<', '>', '<=', '>=', '==', '!='], "CMP")
)

def get_op_code(operation, type_name=None):
	op_code = OP_CODES[operation]
	suffix = "" if not type_name else IR_TYPE_MAPPING[type_name]
	
	return f"{op_code}{suffix}"
	
	
class Function():
	'''
	Representa una function con su lista de instrucciones IR
	'''
	
	def __init__(self, func_name, parameters, return_type):
		self.name = func_name
		self.parameters = parameters
		self.return_type = return_type
		
		self.code = []
		
	def append(self, ir_instruction):
		self.code.append(ir_instruction)
		
	def __iter__(self):
		return self.code.__iter__()
		
	def __repr__(self):
		params = [f"{pname}:{ptype}" for pname, ptype in self.parameters]
		return f"{self.name}({params}) -> {self.return_type}"
		
		
class GenerateCode(cast.NodeVisitor):
	'''
	Clase visitante de nodo que crea secuencias de instrucciones 
	codificadas de 3 direcciones.
	'''
	
	def __init__(self):
		# contador de registros
		self.register_count = 0
		
		# contador rotulos de bloque
		self.label_count = 0
		
		# Función especial para recoger todas las declaraciones globales.
		init_function = Function("__minic_init", [], IR_TYPE_MAPPING['int'])
		
		self.functions = [ init_function ]
		
		# El código generado (lista de tuplas)
		self.code = init_function.code
		
		# Esta bandera indica si el código actual que se está visitando 
		# está en alcance global, o no
		self.global_scope = True
		
	def new_register(self):
		'''
		Crea un nuevo registro temporal
		'''
		self.register_count += 1
		return f'R{self.register_count}'
		
	def new_label(self):
		self.label_count += 1
		return f"L{self.label_count}"
	
	# Debe implementar los métodos visit_Nodename para todos los demás
	# Nodos AST.  En tu código, necesitarás hacer instrucciones.
	# y adjúntalos a la lista de self-code.
	#
	# Algunos métodos de muestra siguen.  Puede que tenga que ajustar 
	# dependiendo de los nombres y la estructura de sus nodos AST.

	def visit_IntegerLiteral(self, node):
		target = self.new_register()
		op_code = get_op_code('mov', 'int')
		self.code.append((op_code, node.value, target))
		# Guarde el nombre del registro donde se colocó el valor.
		node.register = target

	def visit_FloatLiteral(self, node):
		target = self.new_register()
		op_code = get_op_code('mov', 'float')
		self.code.append((op_code, node.value, target))
		# Guarde el nombre del registro donde se colocó el valor.
		node.register = target
		
	def visit_BoolLiteral(self, node):
		target = self.new_register()
		op_code = get_op_code('mov', 'bool')
		self.code.append((op_code, node.value, target))
		# Guarde el nombre del registro donde se colocó el valor.
		node.register = target

	def visit_CharLiteral(self, node):
		target = self.new_register()
		op_code = get_op_code('mov', 'char')
		self.code.append((op_code, node.value, target))
		# Guarde el nombre del registro donde se colocó el valor.
		node.register = target

	def visit_StringLiteral(self, node):
		target = self.new_register()
		op_code = get_op_code('mov', 'str')
		self.code.append((op_code, node.value, target))
		# Guarde el nombre del registro donde se colocó el valor.
		node.register = target
		
	def visit_BinOp(self, node):
		self.visit(node.left)
		self.visit(node.right)
		operator = node.op
		
		op_code = get_op_code(operator, node.left.type.name)
		
		target = self.new_register()
		if op_code.startswith('CMP'):
			inst = (op_code, operator, node.left.register, node.right.register, target)
		else:
			inst = (op_code, node.left.register, node.right.register, target)
			
		self.code.append(inst)
		node.register = target
		
	def visit_UnaryOp(self, node):
		self.visit(node.right)
		operator = node.op
		
		if operator == "-":
			sub_op_code = get_op_code(operator, node.type.name)
			mov_op_code = get_op_code('mov', node.type.name)
			
			# Para tener en cuenta el hecho de que el código de máquina no 
			# admite operaciones unarias, primero debemos cargar un 0 en un 
			# nuevo registro.
			zero_target = self.new_register()
			zero_inst = (mov_op_code, 0, zero_target)
			self.code.append(zero_inst)
			
			target = self.new_register()
			inst = (sub_op_code, zero_target, node.right.register, target)
			self.code.append(inst)
			node.register = target
		elif operator == "!":
			# Este es el operador boolean NOT
			mov_op_code = get_op_code('mov', node.type.name)
			one_target = self.new_register()
			one_inst = (mov_op_code, 1, one_target)
			self.code.append(one_inst)
			
			target = self.new_register()
			inst = ('XOR', one_target, node.right.register, target)
			self.code.append(inst)
			node.register = target
		else:
			# El operador unario + no produce codigo extra
			node.register = node.right.register			
		
	def visit_ReadLocation(self, node):
		op_code = get_op_code('load', node.location.type.name)
		register = self.new_register()
		inst = (op_code, node.location.name, register)
		self.code.append(inst)
		node.register = register
		
	def visit_WriteLocation(self, node):
		self.visit(node.value)
		if hasattr(node.value,'expr'):
			pass
		else:
			if hasattr(node.location,'size'):
				op_code = get_op_code('store', node.location.type.name)
				inst = (op_code, node.value.register, node.location.name + '[' + str(node.location.size.value) + ']')
				self.code.append(inst)
			else:
				op_code = get_op_code('store', node.location.type.name)
				inst = (op_code, node.value.register, node.location.name)
				self.code.append(inst)

	def visit_NewArrayExpression(self,node):
		self.visit(node.datatype)
		#self.visit(node.expr)
		
	def visit_VarDeclaration(self, node):
		self.visit(node.datatype)
		
		# La declaracion de variable depende del alcance
		op_code = get_op_code('var' if self.global_scope else 'alloc', node.type.name)
		def_inst = (op_code, node.name)
		
		if node.value:
			self.visit(node.value)
			self.code.append(def_inst)
			op_code = get_op_code('store', node.type.name)
			inst = (op_code, node.value.register, node.name)
			self.code.append(inst)
		else:
			self.code.append(def_inst)

	def visit_LocalDeclaration(self,node):
		self.visit(node.datatype)
		
		# La declaracion de variable depende del alcance
		op_code = get_op_code('var' if self.global_scope else 'alloc', node.type.name)
		def_inst = (op_code, node.name)
		
		if node.value:
			self.visit(node.value)
			self.code.append(def_inst)
			op_code = get_op_code('store', node.type.name)
			inst = (op_code, node.value.register, node.name)
			self.code.append(inst)
		else:
			self.code.append(def_inst)
			
	def visit_IfStatement(self, node):
		self.visit(node.condition)
		
		# Genera etiquetas para ambas ramas 
		f_label = self.new_label()
		t_label = self.new_label()
		merge_label = self.new_label()
		lbl_op_code = get_op_code('label')
		
		# Inserta la instruccion CBRANCH
		cbranch_op_code = get_op_code('cbranch')
		self.code.append((cbranch_op_code, node.condition.register, t_label, f_label))
		
		# Ahora, el codigo para la rama true
		self.code.append((lbl_op_code, t_label))
		self.visit(node.true_block)
		# Y debemos mezclar la etiqueta
		branch_op_code = get_op_code('branch')
		self.code.append((branch_op_code, merge_label))
		
		# Genera etiqueta para bloque flase
		self.code.append((lbl_op_code, f_label))
		self.visit(node.false_block)
		self.code.append((branch_op_code, merge_label))
		
		# Ahora insertamos la etiqueta mezclada
		self.code.append((lbl_op_code, merge_label))

	def visit_WhileStatement(self,node):
		self.visit(node.condition)

		# Genera etiquetas para ambas ramas 
		f_label = self.new_label()
		t_label = self.new_label()
		merge_label = self.new_label()
		lbl_op_code = get_op_code('label')
		
		# Inserta la instruccion CBRANCH
		cbranch_op_code = get_op_code('cbranch')
		self.code.append((cbranch_op_code, node.condition.register, t_label, f_label))
		
		# Ahora, el codigo para la rama true
		self.code.append((lbl_op_code, t_label))
		self.visit(node.body)
		# Y debemos mezclar la etiqueta
		branch_op_code = get_op_code('branch')
		self.code.append((branch_op_code, merge_label))

		# Ahora insertamos la etiqueta mezclada
		self.code.append((lbl_op_code, merge_label))

		
	def visit_FuncDeclaration(self, node):
		# Genera un nuevo objeto function para colocar el codigo
		func = Function(node.name,
			[(p.name, IR_TYPE_MAPPING[p.datatype.type.name]) for p in node.params],
			IR_TYPE_MAPPING[node.datatype.type.name])
		self.functions.append(func)
		
		if func.name == "main":
			func.name = "__minic_main"
			
		# Y cambiar la función actual a la nueva.
		old_code = self.code
		self.code = func.code
		
		# Ahora, genera el nuevo código de función.
		self.global_scope = False # Turn off global scope
		self.visit(node.body)
		self.global_scope = True # Turn back on global scope
		
		# Y, finalmente, volver a la función original en la que estábamos
		self.code = old_code
		
	def visit_FuncCall(self, node):
		self.visit(node.arguments)
		target = self.new_register()
		op_code = get_op_code('call')
		registers = [arg.register for arg in node.arguments]
		self.code.append((op_code, node.name, *registers, target))
		node.register = target
		
	def visit_ReturnStatement(self, node):
		self.visit(node.value)
		op_code = get_op_code('ret')
		if hasattr(node.value, 'register'):
			self.code.append((op_code, node.value.register))
			node.register = node.value.register

	def visit_ArrayDeclaration(self, node):
		self.visit(node.datatype)

		# La declaracion de variable depende del alcance
		op_code = get_op_code('var' if self.global_scope else 'alloc', node.type.name)
		def_inst = (op_code, node.name+'[]')
		self.code.append(def_inst)

	def visit_ArrayLocalDeclaration(self, node):
		self.visit(node.datatype)

		# La declaracion de variable depende del alcance
		op_code = get_op_code('var' if self.global_scope else 'alloc', node.type.name)
		def_inst = (op_code, node.name+'[]')
		self.code.append(def_inst)
		
# ----------------------------------------------------------------------
#                       PRUEBAS/PROGRAMA PRINCIPAL
#
# Nota: Algunos cambios serán necesarios en proyectos posteriores.
# ----------------------------------------------------------------------

def compile_ircode(source):
	'''
	Genera codigo intermedio desde el fuente.
	'''
	from cparse import parse
	from checkers import check_program
	from errores import errors_reported
	
	cast = parse(source)
	check_program(cast)
	
	# Si no ocurrio error, genere codigo
	if not errors_reported():
		gen = GenerateCode()
		gen.visit(cast)
		return gen.functions
	else:
		return []
		
def main():
	import sys
	
	if len(sys.argv) != 2:
		sys.stderr.write("Usage: python3 -m minic.ircode filename\n")
		raise SystemExit(1)
		
	source = open(sys.argv[1]).read()
	code = compile_ircode(source)
	
	for f in code :
		print(f'{"::"*5} {f} {"::"*5}')
		for instruction in f.code:
			print(instruction)
		print("*"*30)
		
if __name__ == '__main__':
	main()

