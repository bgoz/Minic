
import sly
from errores import error
from Lexe import Tokenizer

from cast import *

class Parser(sly.Parser):
	#debugfile = 'parser.txt'

	tokens = Tokenizer.tokens
	
	precedence = (
	    ('left', IF, ELSE),
		('right','='),
		('left',OR),
		('left',AND),
		('left',EQ,NE),
		('left',LE,'<',GE,'>'),
		('left','+','-'),
		('left','*','/','%'),
		('left','(',')','[',']','{','}','.',';'),
		('right', '!',',','UPLUS','UMINUS')
			

	)

	@_("decl_list")
	def program(self, p):
		return Program(p.decl_list)
		
	@_("decl_list decl")
	def decl_list(self,p):
		p.decl_list.append(p.decl)
		return (p.decl_list)

	@_("decl")
	def decl_list(self,p):
		return [p.decl]
		
	@_("var_decl")
	def decl(self,p):
		return (p.var_decl)
		
	@_("fun_decl")
	def decl(self,p):
		return (p.fun_decl)

	@_("const_decl")
	def decl(self,p):
		return (p[0])

	@_("CONST IDENT '=' expr ';' ")
	def const_decl(self,p):
		return ConstDeclaration(p.IDENT, p.expr, lineno=p.lineno)
		
	@_("type_spec IDENT ';' ")
	def var_decl(self,p):
		return VarDeclaration(p.IDENT, p.type_spec, None, lineno = p.lineno)

	@_("type_spec IDENT '=' expr ';' ")
	def var_decl(self,p):
		return VarDeclaration(p.IDENT, p.type_spec, p.expr, lineno=p.lineno)
		
	@_("type_spec IDENT '[' ']' ';' ")
	def var_decl(self,p):
		return ArrayDeclaration(p.IDENT, p.type_spec, lineno = p.lineno )
		
	@_("VOID")
	def type_spec(self,p):
		return SimpleType(p.VOID)
		
	@_("INT")
	def type_spec(self,p):
		return SimpleType(p.INT)
		
	@_("FLOAT")
	def type_spec(self,p):
		return SimpleType(p.FLOAT)
		
	@_("BOOL")
	def type_spec(self,p):
		return SimpleType(p.BOOL)

	@_("CHAR")
	def type_spec(self,p):
		return SimpleType(p.CHAR)
		
	@_("type_spec IDENT '(' params ')' compound_stmt")
	def fun_decl(self,p):
		return FuncDeclaration(p.IDENT, p.params, p.type_spec, p.compound_stmt, lineno = p.lineno)
		
	@_("param_list")
	def params(self,p):
		return (p.param_list)
	
	@_("VOID")
	def params(self,p):
		return [ ]
		
	@_("param_list ',' param")
	def param_list(self,p):
		p[0].append(p[2])
		return (p.param_list)
		
	@_("param")
	def param_list(self,p):
		return [p.param]
		
	@_("type_spec IDENT")
	def param(self,p):
		return FuncParameter(p.IDENT, p.type_spec, lineno=p.lineno)
	
	@_("type_spec IDENT '['  ']' ")
	def param(self,p):
		return FuncParameter(p.IDENT,p.type_spec, lineno=p.lineno)
		
	@_(" '{' local_decls stmt_list '}' ")
	def compound_stmt(self,p):
		return CompoundStatement(p.local_decls, p.stmt_list, lineno = p.lineno)
		
	@_("local_decls local_decl")
	def local_decls(self,p):
		p.local_decls.append(p.local_decl)
		return p.local_decls
		
	@_("empty")
	def local_decls(self,p):
		return []
		
	@_("type_spec IDENT ';' ")
	def local_decl(self,p):
		return LocalDeclaration(p[1], p[0], None, lineno = p.lineno)
		
	@_("type_spec IDENT '['  ']' ';' ")
	def local_decl(self,p):
		return ArrayLocalDeclaration(p[1], p[0], None, lineno = p.lineno)

	@_("type_spec IDENT '=' expr ';' ")
	def local_decl(self,p):
		return LocalDeclaration(p[1],p[0], p.expr, lineno = p.lineno)
		
	@_("stmt_list stmt")
	def stmt_list(self,p):
		p.stmt_list.append(p.stmt)
		return (p.stmt_list)
		
	@_("empty")
	def stmt_list(self,p):
		return [ ]
		
	@_("expr_stmt")
	def stmt(self,p):
		return (p.expr_stmt)
		
	@_("compound_stmt")
	def stmt(self,p):
		return (p.compound_stmt)
		
	@_("if_stmt")
	def stmt(self,p):
		return (p.if_stmt)
		
	@_("while_stmt")
	def stmt(self,p):
		return (p.while_stmt)
		
	@_("return_stmt")
	def stmt(self,p):
		return (p.return_stmt)
		
	@_("break_stmt")
	def stmt(self,p):
		return (p.break_stmt)
		
	@_("expr ';' ")
	def expr_stmt(self,p):
		return (p.expr)
	
	@_(";")
	def expr_stmt(self,p):
		return NullStatement(None)
		
	@_("WHILE '(' expr ')' compound_stmt ")
	def while_stmt(self,p):
		return WhileStatement(p.expr,p.compound_stmt, lineno= p.lineno)
		
	@_("IF '(' expr ')' stmt")
	def if_stmt(self,p):
		return IfStatement(p.expr, p.stmt, None, lineno= p.lineno)
		
	@_("IF '(' expr ')' stmt ELSE stmt")
	def if_stmt(self,p):
		return IfStatement(p.expr, p.stmt0, p.stmt1, lineno = p.lineno)
		
	@_("RETURN ';' ")
	def return_stmt(self,p):
		return ReturnStatement(None, lineno = p.lineno)
		
	@_("RETURN expr ';' ")
	def return_stmt(self,p):
		return ReturnStatement(p.expr, lineno = p.lineno)
		
	@_("BREAK")
	def break_stmt(self,p):
		return BreakStatement(None, lineno = p.lineno)
		
	@_("IDENT ")
	def location(self,p):
		return SimpleLocation(p[0], lineno = p.lineno)
		
	@_(" IDENT '[' expr ']' " )
	def location(self,p):
		return ArraySimpleLocation(p[0], p.expr, lineno= p.lineno)

	@_("location '=' expr")
	def expr(self,p):
		return WriteLocation(p[0],p[2], lineno = p.lineno)
		
	@_("expr OR expr")
	def expr(self,p):
		return BinOp(p[1], p.expr0,p.expr1, lineno = p.lineno)
		
	@_("expr AND expr")
	def expr(self,p):
		return BinOp(p[1], p.expr0, p.expr1, lineno = p.lineno)
		
	@_("expr EQ expr")
	def expr(self,p):
		return BinOp(p[1], p.expr0, p.expr1, lineno = p.lineno)
		
	@_("expr NE expr")
	def expr(self,p):
		return BinOp(p[1], p.expr0, p.expr1, lineno = p.lineno)
		
	@_("expr LE expr")
	def expr(self,p):
		return BinOp(p[1], p.expr0, p.expr1, lineno = p.lineno)
		
	@_("expr '<' expr")
	def expr(self,p):
		return BinOp(p[1] , p.expr0, p.expr1, lineno = p.lineno)
		
	@_("expr GE expr")
	def expr(self,p):
		return BinOp(p[1], p.expr0, p.expr1, lineno = p.lineno)
		
	@_("expr '>' expr")
	def expr(self,p):
		return BinOp(p[1], p.expr0, p.expr1, lineno = p.lineno)
		
	@_("expr '+' expr")
	def expr(slef,p):
		return BinOp(p[1], p.expr0, p.expr1, lineno = p.lineno)
		
	@_("expr '-' expr")
	def expr(self,p):
		return BinOp(p[1], p.expr0, p.expr1, lineno = p.lineno)
		
	@_("expr '*' expr")
	def expr(self,p):
		return BinOp(p[1], p.expr0, p.expr1, lineno = p.lineno)
		
	@_("expr '/' expr")
	def expr(self,p):
		return BinOp(p[1], p.expr0, p.expr1, lineno = p.lineno )
		
	@_("expr '%' expr")
	def expr(self,p):
		return BinOp(p[1], p.expr0, p.expr1, lineno = p.lineno)
		
	@_(" '!' expr")
	def expr(self,p):
		return UnaryOp(p[0], p.expr, lineno = p.lineno)
		
	@_(" '(' expr ')' ")
	def expr(self,p):
		return (p.expr)

	@_("location")
	def expr(self,p):
		return ReadLocation(p[0])

	@_("CONST")
	def expr(self,p):
		return ConstLiteral(p[0])
		
		
	@_("IDENT '(' args ')' ")
	def expr(self,p):
		return FuncCall(p.IDENT, p.args, lineno = p.lineno)
		
	@_("IDENT '.' SIZE")
	def expr(self,p):
		pass
		#return (p.IDENT, p[1], p.SIZE)
		
	@_ ("BOOL_LIT")
	def expr(sel,p):
		return BoolLiteral(p.BOOL_LIT)
		
	@_("INT_LIT")
	def expr(slef,p):
		return IntegerLiteral(p.INT_LIT)
		
	@_("FLOAT_LIT")
	def expr(self,p):
		return FloatLiteral(p.FLOAT_LIT)
		
	@_("CHAR_LIT")
	def expr(self,p):
		return CharLiteral(p.CHAR_LIT)

	@_("NEW type_spec '[' expr ']' ")
	def expr(self,p):
		return NewArrayExpression(p.type_spec, p.expr, lineno=p.lineno)

	@_(' "+" expr %prec UPLUS')
	def expr(self,p):
		return UnaryOp(p[0], p.expr)

	@_(' "-" expr %prec UMINUS')
	def expr(self,p):
		return UnaryOp(p[0], p.expr)
		


	@_("arg_list ',' expr")
	def arg_list(self,p):
		p.arg_list.append(p.expr)
		return (p.arg_list)
		
	@_("expr")
	def arg_list(self,p):
		return [p.expr]
		
	@_("arg_list")
	def args(self,p):
		return (p.arg_list)
		
	@_("empty")
	def args(self,p):
		return [ ]
	
	@_(" ")
	def empty(self,p):
		return NullStatement(None)
	
	
	# ----------------------------------------------------------------------
	# NO MODIFIQUE
	#
	# manejo de errores catch-all. Se llama a la siguiente función en 
	# cualquier entrada incorrecta. p es el token ofensivo o None si 
	# el final de archivo (EOF).
	def error(self, p):
		if p:
			error(p.lineno, "Error de sintaxis en la entrada en el token '%s'" % p.value)
		else:
			error('EOF','Error de sintaxis. No mas entrada.')
			
# ----------------------------------------------------------------------
#                  NO MODIFIQUE NADA A CONTINUACIÓN
# ----------------------------------------------------------------------

def parse(source):
	'''
	Parser el código fuente en un AST. Devuelve la parte superior del árbol AST.
	'''
	lexer  = Tokenizer()
	parser = Parser()
	ast = parser.parse(lexer.tokenize(source))
	return ast
	
def main():
	'''
	Programa principal. Usado para probar.
	'''
	import sys
	
	if len(sys.argv) != 2:
		sys.stderr.write('Uso: python -m minic.parser filename\n')
		raise SystemExit(1)

	# Parse y crea el AST
	ast = parse(open(sys.argv[1]).read())

	# Genera el árbol de análisis sintáctico resultante
	for depth, node in flatten(ast):
		print('%s: %s%s' % (getattr(node, 'lineno', None), ' '*(4*depth), node))
		
		
		dot = DotVisitor()
		dot.visit(ast)
		print(dot)
		
if __name__ == '__main__':
	main()
