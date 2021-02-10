# minic/typesys.py
'''
Sistema de tipo mpascal
=======================
Este archivo implementa características básicas del sistema de 
tipos MiniC. 
Ahi esta mucha flexibilidad es posible aquí, pero la mejor 
estrategia podría ser No reconsiderar el problema. Al menos 
no al principio. Aquí están los Requisitos básicos mínimos:

1. Los tipos tienen nombres (por ejemplo, 'int', 'float', 'string')
2. Los tipos deben ser comparables. (por ejemplo, int != float).
3. Los tipos admiten diferentes operadores (por ejemplo, +, -, *, /, etc.)

Para tratar todo esto inicialmente, recomiendo representar tipos
Como cuerdas simples. Hacer tablas que representen las capacidades.
de diferentes tipos. Hacer algunas funciones de utilidad que comprueban los operadores.
MANTENLO SIMPLE. REPETIR. SENCILLO.
'''

ARITHM_BIN_OPS = ["+", "-", "*", "/"]
ARITHM_UNARY_OPS = ["+", "-"]

REL_BIN_OPS = ["<", "<=", ">", ">=", "==", "!="]

BOOL_BIN_OPS = ["&&", "||", "==", "!="]
BOOL_UNARY_OPS = ["!"]

class Type():
	'''
	Clase Base para nuestros tipos del sistema
	'''
	
	@classmethod
	def binop_type(cls, op, right_type):
		"""
		Devuelve el tipo de aplicación del operador binario con el actual.
		tipo y el tipo del operando correcto, o devuelve Ninguno si el
		la operación no es válida"""
		return None
		
	@classmethod
	def unaryop_type(cls, op):
		"""
		Returns the type of applying the unary operator to the current type"""
		return None
		
	@classmethod
	def get_by_name(cls, type_name):
		for type_cls in cls.__subclasses__():
			if type_cls.name == type_name:
				return type_cls
				
		return None
		
class FloatType(Type):
	name = "float"
	
	@classmethod
	def binop_type(cls, op, right_type):
		if issubclass(right_type, FloatType):
			if op in ARITHM_BIN_OPS:
				return FloatType
			elif op in REL_BIN_OPS:
				return BoolType
				
		return None
		
	@classmethod
	def unaryop_type(cls, op):
		if op in ARITHM_UNARY_OPS:
			return FloatType
			
		return None
		
class IntType(Type):
	name = "int"
	
	@classmethod
	def binop_type(cls, op, right_type):
		if issubclass(right_type, IntType):
			if op in ARITHM_BIN_OPS:
				return IntType
			elif op in REL_BIN_OPS:
				return BoolType
				
		return None
		
	@classmethod
	def unaryop_type(cls, op):
		if op in ARITHM_UNARY_OPS:
			return IntType
			
		return None
		
class CharType(Type):
	name = "char"
	
	@classmethod
	def binop_type(cls, op, right_type):
		if issubclass(right_type, CharType):
			if op in REL_BIN_OPS:
				return BoolType
				
		return None
		
		
class BoolType(Type):
	name = "bool"
	
	@classmethod
	def binop_type(cls, op, right_type):
		if issubclass(right_type, BoolType) and op in BOOL_BIN_OPS:
			return BoolType
			
		return None
		
	@classmethod
	def unaryop_type(cls, op):
		if op in BOOL_UNARY_OPS:
			return BoolType
			
		return None

