
from errores import error
from sly import Lexer

class Tokenizer(Lexer):

        keywords = {
                'int', 'if', 'while', "else", "return","break","size","void","bool",
                "new", "float", "true","false","const","char"

        }

        tokens = {
                # keywords
                * { kw.upper() for kw in keywords },

                # Identificador
                IDENT,LE,GE,EQ,NE,OR,AND,INT_LIT,FLOAT_LIT,BOOL_LIT,CHAR_LIT

        }
        literals = {
                '+', '-', '*', '/',")","(","{","}",";",",","%","<",">","=","!","[","]"
        }

        ignore = ' \t\r'
        
        ERRO= r'[\/\*]+.+[\/\*]+.+[\*\/]+.+[\*\/]+'
        @_(r'[\/\*]+.+[\/\*]+.+[\*\/]+.+[\*\/]+')
        def ERRO(self, t):
        	error(self.lineno,'Comentario anidado')
        	self.index+= 1

        @_(r'/\*[\w\W]*?\*/')
        def ignore_comment(t):
                t.lineno += t.value.count('\n')


        @_(r'\n+')
        def ignore_newline(self, t):
                self.lineno += len(t.value)


        LE  = r'<='
        GE  = r'>='
        EQ  = r'=='
        NE  = r'!='
        OR  = r'\|\|'
        AND = r'&&'
        CHAR_LIT = r'["][\w\W]["]' 
        BOOL_LIT=r'True|False'
        IDENT = r'[a-zA-Z_][a-zA-Z_0-9]*'
        NUMBER_EX = r'0x[0-9a-fA-F]+'
        NUMBER_OCT = r'0o[0-7]+'
        BINARIO = r'0b[0-1]+'
        FLOAT_LIT = r'([0-9]+\.[0-9]+)|(\.[0-9]+)|([0-9]+\.)'
        INT_LIT = r'[0-9]+'



        @_(r'[a-zA-Z_][a-zA-Z0-9_]*')
        def IDENT(self, t):
            if t.value in self.keywords:
                t.type = t.value.upper()
            return t 
            
        @_(r'["][\w\W]["]')
        def CHAR_LIT(self,p):
            t.value = (t.value[1])
            return t

        @_(r'True|False')
        def BOOL_LIT(self,p):
            return t 



        @_(r'0x[0-9a-fA-F]+')
        def NUMBER_EX(self,t):
        	if t.value.startswith('0x'):
        		t.value = int(t.value[2:], 16)
        		return t

            
        @_(r'0o[0-7]+')
        def NUMBER_OCT(self,t):
        	if t.value.startswith('0o'):
        		t.value = int(t.value[2:], 8)
        		return t
        	
        @_(r'0b[0-1]+')
        def BINARIO(self,t):
        	if t.value.startswith('0b'):
        		t.value = int(t.value[2:], 2)
        		return t

        @_(r'([0-9]+\.[0-9]+)|(\.[0-9]+)|([0-9]+\.)')
        def FLOAT_LIT(self,t):
        	t.value = float(t.value)
        	return t

        @_(r'[0-9]+')
        def INT_LIT(self,t):
            t.value = int(t.value)
            return t 



        # ----------------------------------------------------------------------
        # Manejo de errores de caracteres incorrectos
        def error(self, t):
                error(self.lineno, 'Caracter Ilegal %r' % t.value[0])
                self.index += 1


def main():
        '''
        main. Para propósitos de depuracion
        '''
        import sys

        if len(sys.argv) != 2:
                sys.stderr.write('Uso: python3 -m minic.tokenizer filename\n')
                raise SystemExit(1)

        lexer = Tokenizer()
        text = open(sys.argv[1]).read()
        for tok in lexer.tokenize(text):
                print(tok)

if __name__ == '__main__':
        main()

