import string 
import sys
import argparse

def custom_excepthook(exc_type, exc_value, exc_traceback):
    print(f"Error: {exc_value}")

sys.excepthook = custom_excepthook
#######################################
# CONSTANTS
#######################################

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

#######################################
# ERRORS
#######################################

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class RTError(Error):
	def __init__(self, pos_start, pos_end, details, context):
		super().__init__(pos_start, pos_end, 'Runtime Error', details)
		self.context = context

	def as_string(self):
		result  = self.generate_traceback()
		result += f'{self.error_name}: {self.details}'
		#result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
		return result

	def generate_traceback(self):
		result = ''
		pos = self.pos_start
		ctx = self.context

		while ctx:
			result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
			pos = ctx.parent_entry_pos
			ctx = ctx.parent

		return 'Traceback (most recent call last):\n' + result        

#######################################
# POSITION
#######################################

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#######################################
# TOKENS
#######################################

INT_C = 'INT_CONST'
DEC_C = 'DEC_CONST'
INT_T='int'
DEC_T='dec'
PLUS = 'PLUS'
MIN = 'MIN'
DIV = 'DIV'
MUL = 'MUL'
MOD='MOD'
DOT='DOT'
LPAREN   = 'LPAREN'
RPAREN   = 'RPAREN'
ASSIGN='ASSIGN'
SEMI='SEMI'
COMP_E='EQUAL TO'
COMP_GT='GREATER THAN'
COMP_LT='LESS THAN'
AND='and'
NOT='not'
OR='or'
COMP_NE='NOT EQUAL'
COMP_LTE				= 'LESS THAN EQUAL'
COMP_GTE				= 'GREATER THAN EQUAL'
COMMA='COMMA'
ID='IDENTIFIER'
KEYWORD='KEYWORD'
IF='if'
ELIF='elif'
ELSE='else'
WHILE='while'
FOR='for'
LBRACES='LBRACES'
RBRACES='RBRACES'
SLBRACES='SBRACES'
SRBRACES='SRBRACES'
WORD='word_const'
WORD_T='word'
GIVE='give'
TAKE='take'
CHAR='char'

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

########################################
#RESERVED KEYWORDS# 
####################################

Keywords=[


    'int',
    'dec',
    'if',
    'elif',
    'else',
    'while',
    'for',
    'or',
    'and',
    'not',
    'word',
    'give',
    'take',
    'char'
]

#######################################
# LEXER
#######################################

class Lexer:
    def __init__(self, text):
        fn = "testfile"
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []
        
        while self.current_char != None:
            if self.current_char in ' \t\n':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())    
            elif self.current_char == '+':
                tokens.append(Token(PLUS))
                self.advance()
            elif self.current_char == ',':
                self.advance()
                tokens.append(Token(COMMA, ','))   
            elif self.current_char == '-':
                tokens.append(Token(MIN))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(DIV))
                self.advance()
            elif self.current_char == '%':
                tokens.append(Token(MOD))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(RPAREN))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(LBRACES))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(RBRACES))
                self.advance()    
            elif self.current_char == '[':
                tokens.append(Token(SLBRACES))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(SRBRACES))
                self.advance()     
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '!':
                tokens.append(self.make_not_equals())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())  
            elif self.current_char == '<':
                tokens.append(self.make_less_than()) 
            elif self.current_char == '"':
                tokens.append(self.make_string())          
            elif self.current_char == ';':
                tokens.append(Token(SEMI))
                self.advance()
            elif self.current_char == '.':
                tokens.append(Token(DOT)) 
                self.advance()           
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        return tokens, None
    
    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def make_string(self):
        id_str = ""
        self.advance()
        while self.current_char != '"' :
                id_str += self.current_char
                self.advance()   
        self.advance()  
        return Token(WORD,id_str)
        
    def make_identifier(self):
            id_str = ''
           # pos_start = self.pos.copy()

            while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
                id_str += self.current_char
                self.advance()

            tok_type = id_str if id_str in Keywords else ID
            tok_value = None if id_str in Keywords else id_str
            return Token(tok_type,tok_value)        
    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(INT_C, int(num_str))
        else:
            return Token(DEC_C, float(num_str))
        
    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(COMP_NE)

        raise IllegalCharError(self.pos, pos_start, "Expected '=' after '!'")
	
    def make_equals(self):
        tok_type = ASSIGN
        #pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = COMP_E

        return Token(tok_type)

    def make_less_than(self):
        tok_type = COMP_LT
        #pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = COMP_LTE

        return Token(tok_type)

    def make_greater_than(self):
        tok_type = COMP_GT
        #pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = COMP_GTE

        return Token(tok_type)        

#######################################
#NODES
########################################\
class Numnode:
    def __init__(self,token):
        self.token=token
        self.type=token.type
        self.value=token.value
    def __repr__(self):
        return f'{self.type}:{self.value}'
class Binnode:
    def __init__(self,left,op,right):
        self.left=left
        self.op=op
        self.right=right
    def __repr__(self):
        return f'({self.left},{self.op},{self.right})'

######################################
class VarNode:
    def __init__(self, var_name):
        self.var_name = var_name

    def __repr__(self):
        return f'(Var {self.var_name})'
    
class VarAssignNode:
    def __init__(self, var_name, value_node, var_type=None):
        self.var_type = var_type  # Type (e.g., int)
        self.var_name = var_name  # Variable name (e.g., a)
        self.value_node = value_node  # Assigned value (e.g., 2)

    def __repr__(self):
        return f'(Var {self.var_type} {self.var_name} = {self.value_node})'
    
class ArrayAssignNode:
    def __init__(self, var_name, value_node, var_type=None):
        self.var_type = var_type  # Type (e.g., int)
        self.var_name = var_name  # Variable name (e.g., a)
        self.value_node = value_node  # Assigned value (e.g., 2)

    def __repr__(self):
        return f'(Var {self.var_type} {self.var_name} = {self.value_node})'
    
class UnaryOpNode:
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

		# self.pos_start = self.op_tok.pos_start
		# self.pos_end = node.pos_end

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'

class Ifnode:
    def __init__(self,cases,elsecase):
        self.elsecase = elsecase
        self.cases = cases

    def __repr__(self):
        return f'({self.cases}, {self.elsecase})'    
    

class Whilenode:
    def __init__(self,condition,expressions):
        self.condition = condition
        self.expressions = expressions

    def __repr__(self):
        return f'({self.expressions}, {self.condition})'  
    
class Fornode:
        def __init__(self,decl,cond,inc,expressions):
            self.decl = decl
            self.cond = cond
            self.inc=inc
            self.expressions=expressions

class blocknode:
      def __init__(self,statements):
        self.statements=statements

      def __repr__(self):
        return f'({self.statements})' 
     
class stringnode:
    def __init__(self,token):
        self.value=token.value
        self.type=token.type

class givenode:
    def __init__(self,token):
        self.token=token

    def __repr__(self):
        return f'(print {self.token.value})' 

class arraynode:
    def __init__(self,expressions,num):
        self.expressions=expressions
        self.num=num

class arrayvalnode:
    def __init__(self,var_name,idx):
        self.var_name=var_name
        self.idx=idx

class arraysingularassignnode:
    def __init__(self,var_name,idx,val):
        self.var_name=var_name
        self.idx=idx
        self.value=val

class typecastnode:
    def __init__(self,val):
        self.value=val

# class VarDeclNode:
#     def __init__(self, var_type, var_name, value_node):
#         self.var_type = var_type  # Type (e.g., int)
#         self.var_name = var_name  # Variable name (e.g., a)
#         self.value_node = value_node  # Assigned value (e.g., 2)

#     def __repr__(self):
#         return f'(VarDecl {self.var_type} {self.var_name} = {self.value_node})'

#######################################
#PARSER
#######################################
class Parser:
    def __init__(self,tokens):
        self.tokens=tokens
        self.current_token=tokens[0]
        self.idx=0
    def next_token(self):
        self.idx+=1
        if(self.idx<len(self.tokens)):
            self.current_token=self.tokens[self.idx]
        else:
            self.current_token=Token(None)
    def peek_next_token(self):
        if self.idx + 1 < len(self.tokens):
            return self.tokens[self.idx + 1]
        return Token(None)
            
    def factor(self):
        token=self.current_token
        if token.type=='INT_CONST' or token.type=='DEC_CONST':
                self.next_token()
                return Numnode(token)
        elif token.type==WORD:
                self.next_token()
                return stringnode(token)
        elif token.type==CHAR:
                self.next_token()
                if self.current_token.type!=LPAREN:
                    raise Exception('expected parenthesis')
                self.next_token()
                val=self.comp_exprs()
                if self.current_token.type!=RPAREN:
                    raise Exception('expected parenthesis')
                self.next_token()
                return typecastnode(val)
        elif token.type=='IDENTIFIER':
                var=self.current_token.value
                self.next_token()
                if self.current_token.type==SLBRACES:
                    self.next_token()
                    n_node=self.comp_exprs()
                    if self.current_token.type!=SRBRACES:
                        raise Exception('expected right square braces')
                    self.next_token()
                    return arrayvalnode(var,n_node)
                return VarNode(token.value)
        elif token.type==MIN or token.type==PLUS:
                self.next_token()
                node=self.exprs()
                return UnaryOpNode(token,node)
        elif token.type == 'LPAREN':
            self.next_token()
            node = self.comp_exprs()  # Parse the inner expression
            if self.current_token and self.current_token.type == 'RPAREN':
                self.next_token()
            else:
                raise Exception("Expected ')'")  # Add error handling for unmatched parentheses
            return node
        raise Exception(f"Unexpected token: {token}")

    def term(self):
        node=self.factor()
        if isinstance(self.current_token, tuple):
            raise TypeError(f"Unexpected tuple encountered: {self.current_token}")

        while self.current_token.type is not None and self.current_token.type in ('MUL', 'DIV','MOD'):
            if(self.current_token.type=='DIV' or self.current_token.type=='MUL' or self.current_token.type=='MOD'):
                token= self.current_token
                self.next_token()
            node = Binnode(node,token,self.factor())
        return node
    
    def exprs(self):
        node =self.term()
        while self.current_token.type is not None and self.current_token.type in ('PLUS', 'MIN'):
            if(self.current_token.type=='PLUS' or self.current_token.type=='MIN'):
                token= self.current_token
                self.next_token()
            node =Binnode (node,token,self.term())
        return node
    
    def block(self):
        if self.current_token.type == LBRACES:
            self.next_token()
            statements=self.statement_list()
            if self.current_token.type != RBRACES:
                raise Exception("Expected right braces")
            self.next_token()
            return blocknode(statements)
        return self.statement()    


    def statement_list(self):
        node = self.statement()

        results = [node]
        while self.current_token.type == SEMI and self.peek_next_token().type!= RBRACES and self.peek_next_token().type!=None:
            self.next_token()
            results.append(self.statement())
        if self.current_token.type != SEMI:
            raise Exception("Expected semicolon")    
        self.next_token()
        return results

    def statement(self):
        if self.current_token.type == INT_T or self.current_token.type == DEC_T or self.current_token.type == WORD_T:
            node = self.parse_var_decl()
        elif self.current_token.type == ID and self.peek_next_token().type!=SLBRACES:
            node = self.parse_var_decl()
        elif self.current_token.type == ID and self.peek_next_token().type==SLBRACES:
            node = self.parse_array_decl()
        elif self.current_token.type == GIVE:
            node = self.parse_give()
        elif self.current_token.type == IF:
            node = self.ifexprs()
        elif self.current_token.type == WHILE:
            node = self.whileexprs()
        elif self.current_token.type == FOR:
            node = self.forexprs()
        elif self.current_token.type==LBRACES:
            node=self.block()
        else:
            raise Exception(f"Syntax error - {self.current_token}")
        return node
    
    def forexprs(self):
        if self.current_token.type == FOR:  # Look for 'for'
            self.next_token()
            if self.current_token.type != 'LPAREN':
                raise Exception("Expected '(' after 'for'")
            self.next_token()
            decl = self.parse_var_decl()  # Parse condition inside parentheses
            if self.current_token.type != SEMI:
                raise Exception("Expected ';' at the end of the statement")
            self.next_token()
            cond=self.comp_exprs()
            if self.current_token.type != SEMI:
                raise Exception("Expected ';' at the end of the statement")
            self.next_token()
            inc=self.parse_var_decl()
            if self.current_token.type != 'RPAREN':
                raise Exception("Expected ')' after condition")
            self.next_token()
            if self.current_token.type != LBRACES:
                raise Exception("Expected left braces")
            self.next_token()
            node = self.ifexprs()

            expressions = [node]

            while self.current_token.type == SEMI and self.peek_next_token().type != RBRACES:
                self.next_token()
                expressions.append(self.ifexprs())
            if self.current_token.type != SEMI:
                raise Exception("Expected semicolon")    
            self.next_token()
            if self.current_token.type != RBRACES:
                raise Exception("Expected right braces")
            self.next_token()
            return Fornode(decl,cond,inc,expressions) 
        return(self.statement())
    
    
    def whileexprs(self):
        if self.current_token.type == WHILE: 
            self.next_token()
            if self.current_token.type != 'LPAREN':
                raise Exception("Expected '(' after 'while'")
            self.next_token()
            condition = self.comp_exprs()  # Parse condition inside parentheses
            if self.current_token.type != 'RPAREN':
                raise Exception("Expected '(' after 'while'")
            self.next_token()
            if self.current_token.type != LBRACES:
                raise Exception("Expected left braces")
            self.next_token()
            node = self.ifexprs()
            expressions = [node]

            while self.current_token.type == SEMI and self.peek_next_token().type != RBRACES:
                self.next_token()
                expressions.append(self.ifexprs())
            if self.current_token.type != SEMI:
                raise Exception("Expected semicolon")    
            self.next_token()
            if self.current_token.type != RBRACES:
                raise Exception("Expected right braces")
            self.next_token()
            return Whilenode(condition,expressions)   
        return(self.statement())

    def ifexprs(self):
        cases=[]
        elsecase=None
        if self.current_token.type == IF:  
            self.next_token()
            if self.current_token.type != 'LPAREN':
                raise Exception("Expected '(' after 'if'")
            self.next_token()
            condition = self.comp_exprs()  # Parse condition inside parentheses
            if self.current_token.type != 'RPAREN':
                raise Exception("Expected '(' after 'if'")
            self.next_token()
            if self.current_token.type != LBRACES:
                raise Exception("Expected left braces")
            self.next_token()
            node = self.statement()

            expressions = [node]

            while self.current_token.type == SEMI and self.peek_next_token().type != RBRACES:
                self.next_token()
                expressions.append(self.statement())
            if self.current_token.type != SEMI:
                raise Exception("Expected semicolon")
            self.next_token()
            if self.current_token.type != RBRACES:
                raise Exception("Expected right braces")
            self.next_token()
            cases.append([condition,expressions])
            while self.current_token.type == ELIF: 
                self.next_token()
                if self.current_token.type != 'LPAREN':
                    raise Exception("Expected '(' after 'elif'")
                self.next_token()
                condition = self.comp_exprs()  # Parse condition inside parentheses
                if self.current_token.type != 'RPAREN':
                    raise Exception("Expected '(' after 'elif'")
                self.next_token()
                if self.current_token.type != LBRACES:
                    raise Exception("Expected left braces")
                self.next_token()
                node = self.statement()
                expressions = [node]
                while self.current_token.type == SEMI and self.peek_next_token().type != RBRACES:
                    self.next_token()
                    expressions.append(self.statement())
                if self.current_token.type != SEMI:
                    raise Exception("Expected semicolon")    
                self.next_token()
                if self.current_token.type != RBRACES:
                    raise Exception("Expected right braces")
                self.next_token()
                cases.append([condition,expressions])
            if self.current_token.type == ELSE:  # Look for 'int' or 'dec'
                self.next_token()
                if self.current_token.type != LBRACES:
                    raise Exception("Expected variable name")
                self.next_token()
                node = self.statement()

                expressions = [node]

                while self.current_token.type == SEMI and self.peek_next_token().type!= RBRACES:
                    self.next_token()
                    expressions.append(self.statement())
                if self.current_token.type != SEMI:
                    raise Exception("Expected semicolon")    
                self.next_token()
                if self.current_token.type != RBRACES:
                    raise Exception("Expected right braces")
                self.next_token()
                elsecase=expressions
            return Ifnode(cases,elsecase)
        return(self.statement())

    def parse_var_decl(self):
        if self.current_token.type == INT_T or self.current_token.type == DEC_T: 
            var_type = self.current_token.type
            self.next_token()
            var_name = self.current_token  # Variable name
            if var_name.type != ID:
                raise Exception("Expected variable name")
            self.next_token()
            if var_type==INT_T:
                     value_node = Numnode(Token(INT_C,0)) 
            else:
                value_node=Numnode(Token(DEC_C,0.0)) 
            if self.current_token.type == ASSIGN:
                self.next_token()
                value_node = self.comp_exprs()
            elif self.current_token.type==SLBRACES:
                self.next_token()
                num = self.comp_exprs()
                if self.current_token.type != SRBRACES:
                    raise Exception('Expected square bracket')
                self.next_token()
                expressions=None
                if self.current_token.type == ASSIGN:
                    self.next_token()
                    if self.current_token.type==LBRACES:
                        self.next_token()
                        element_node = self.comp_exprs()
                        expressions = [element_node]
                        while self.current_token.type == COMMA :
                            self.next_token()
                            expressions.append(self.comp_exprs())
                        if self.current_token.type != RBRACES:
                            raise Exception('Expected curly bracket')
                        self.next_token()
                    else:
                           raise Exception('Expected curly bracket')

                value_node=   arraynode(expressions,num)  

                return ArrayAssignNode(var_name.value, value_node,var_type)    
            return VarAssignNode(var_name.value,value_node,var_type)
        elif self.current_token.type == WORD_T:
            self.next_token()
            var_name = self.current_token  # Variable name
            if var_name.type != ID:
                raise Exception("Expected variable name")
            self.next_token()
            value_node=stringnode(Token(WORD,""))
            if self.current_token.type == ASSIGN:
                self.next_token()
                # if self.current_token.type!=WORD :
                #     if self.current_token.type!=CHAR:
                #         raise Exception("Expected double quotes")
                # if self.current_token.type==CHAR:
                value_node=self.type_cast()
                # else:    
                #     value_node = stringnode(self.current_token)
                #     self.next_token()
            return VarAssignNode(var_name.value,value_node,WORD_T)
            # if self.current_token.type != SEMI:
            #     raise Exception("Expected ';' at the end of the statement")
            # self.next_token()
        
        elif self.current_token.type == ID:
            var_name = self.current_token
            self.next_token()
            if self.current_token.type == ASSIGN:
                self.next_token()
                value_node = self.type_cast()    

            # if self.current_token.type != SEMI:
            #     raise Exception("Expected ';' at the end of the statement")
            # self.next_token()
        
                return VarAssignNode( var_name.value, value_node)
        else:
            node =self.comp_exprs()
            while self.current_token.type is not None and self.current_token.type in ('and', 'or'):
                token= self.current_token
                self.next_token()
                node =Binnode (node,token,self.comp_exprs())
            return node  # Handle other expressions
        
    def parse_array_decl(self):
        var_name=self.current_token.value
        self.next_token()
        self.next_token()
        n=self.comp_exprs()
        if self.current_token.type!=SRBRACES:
            raise Exception("expected square braces")
        self.next_token()
        if self.current_token.type!=ASSIGN:
            return arrayvalnode(var_name,n)
        elif self.current_token.type==ASSIGN:
            self.next_token()
            val=self.comp_exprs()
            return arraysingularassignnode(var_name,n,val)
        else:
            raise Exception("Sytax Error")
        
    def parse_give(self):
        if self.current_token.type== GIVE:
            self.next_token()
            if self.current_token.type!=LPAREN:
                raise Exception('Expected Left Braces')
            self.next_token()
            node = self.comp_exprs()
            if self.current_token.type!=RPAREN:
                raise Exception('Expected Right Braces')
            self.next_token()    
            return givenode(node)
        return self.statement()        

    def type_cast(self):
        if self.current_token.type== CHAR:
            self.next_token()
            if self.current_token.type!=LPAREN:
                raise Exception('expected parenthesis')
            self.next_token()
            val=self.comp_exprs()
            if self.current_token.type!=RPAREN:
                raise Exception('expected parenthesis')
            self.next_token()
            return typecastnode(val)
        return self.comp_exprs()


    def comp_exprs(self):
        if self.current_token.type ==NOT:
            self.next_token()
            node= self.comp_exprs()
            return UnaryOpNode(Token(NOT),node)
        else:
            node=self.exprs()
            while self.current_token.type is not None and self.current_token.type in (COMP_E,COMP_GT,COMP_GTE,COMP_LT,COMP_LTE,COMP_NE):
                op=self.current_token
                self.next_token()   
                node=Binnode (node,op,self.exprs()) 

        return node


#######################################################################
#######################################################################


class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)

    def powed_by(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self):
        return None, self.illegal_operation()


    def copy(self):
        raise Exception('No copy method defined')

    def is_true(self):
        return False

    def illegal_operation(self, other=None):
        if not other: other = self
        return RTError(
            self.pos_start, other.pos_end,
            'Illegal operation',
            self.context
        )

class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'Division by zero',
                    self.context
                )

            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def powed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0

    def __repr__(self):
        return str(self.value)

class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def is_true(self):
        return len(self.value) > 0

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return f'"{self.value}"'


#######################################
# SYMBOL TABLE
#######################################

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.types = {}       
        self.parent = None

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
           return self.parent.get(name)
        return value
    
    def gettype(self, name):
        type_ = self.symbols.get(name, None)
        if type_ == None and self.parent:
          return self.parent.get(name)
        return type_    

    def set(self, name, value):
        self.symbols[name] = value

    def settype(self, name, _type):
        self.types[name] = _type            

    def remove(self, name):
        del self.symbols[name]
        del self.types[name]

    def copy(self,symb):
        self.symbols=symb.symbols.copy()
        self.types=symb.types.copy()
       


#######################################
#GLOBAL VARIABLES
######################################

symbol_table = SymbolTable()

#######################################
# INTERPRETER
#######################################              
class Interpreter():
    def __init__(self, tree):
        self.tree = tree
        global symbol_table

    def visit(self, node):
        if isinstance(node, Binnode):
            return self.visit_Binnode(node)
        elif isinstance(node, VarNode):
            return self.visit_VarNode(node)
        elif isinstance(node, blocknode):
            return self.visit_blocknode(node)
        elif isinstance(node, ArrayAssignNode):
            return self.visit_arrayassignnode(node)
        elif isinstance(node, arraynode):
            return self.visit_arraynode(node)
        elif isinstance(node, arrayvalnode):
            return self.visit_arrayvalnode(node)
        elif isinstance(node, arraysingularassignnode):
            return self.visit_arraysingularassignnode(node)
        elif isinstance(node, Ifnode):
            return self.visit_Ifnode(node)
        elif isinstance(node, Whilenode):
            return self.visit_Whilenode(node)
        elif isinstance(node, Fornode):
            return self.visit_Fornode(node)
        elif isinstance(node, givenode):
            return self.visit_givenode(node)
        elif isinstance(node, typecastnode):
            return self.visit_typecastnode(node)
        elif isinstance(node, VarAssignNode):
            return self.visit_VarAssignNode(node)
        elif isinstance(node, Numnode):
            return self.visit_Numnode(node)
        elif isinstance(node, stringnode):
            return self.visit_stringnode(node)
        elif isinstance(node, UnaryOpNode):
            return self.visit_UnaryOpNode(node)
        elif isinstance(node, Token) and node.type == ID:  # Variable reference
            return symbol_table.get(node.value, f"Undefined variable: {node.value}")

    def visit_VarNode(self, node):
        var_name = node.var_name
        value=symbol_table.get(var_name)
        return value

    def visit_VarAssignNode(self, node):
        var_name = node.var_name
        var_type=node.var_type
        # print(symbol_table.symbols)
        if var_type!=None:
            if var_name in symbol_table.symbols.keys():
                raise Exception(f'variable declared twice {var_name},')
            symbol_table.settype(var_name, var_type)
        if var_type==None:
            if var_name not in symbol_table.symbols.keys():
                raise Exception('variable not declared')
        value = self.visit(node.value_node)

        var_type = symbol_table.types[var_name]
        if var_type==INT_T:
            symbol_table.set(var_name,int(value))
        elif var_type==DEC_T:
            symbol_table.set(var_name,float(value))
        elif var_type==WORD_T:
            symbol_table.set(var_name,value)
        
    def visit_Binnode(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MIN:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == DIV:
            return self.visit(node.left) / self.visit(node.right)
        elif node.op.type == MOD:
            return self.visit(node.left) % self.visit(node.right)
        elif node.op.type == COMP_GTE:
            return self.visit(node.left) >= self.visit(node.right)
        elif node.op.type == COMP_GT:
            return self.visit(node.left) > self.visit(node.right)
        elif node.op.type == COMP_E:
            return self.visit(node.left) == self.visit(node.right)
        elif node.op.type == COMP_NE:
            return self.visit(node.left) != self.visit(node.right)
        elif node.op.type == COMP_LT:
            return self.visit(node.left) < self.visit(node.right)
        elif node.op.type == COMP_LTE:
            return self.visit(node.left) <= self.visit(node.right)
        elif node.op.type == AND:
            return self.visit(node.left) and self.visit(node.right)
        elif node.op.type == OR:
            return self.visit(node.left) or self.visit(node.right)

    def visit_Numnode(self, node):
        return node.value
    
    def visit_stringnode(self, node):
        return node.value
    
    def visit_arrayassignnode(self,node):
        arr=[]
        var_name = node.var_name
        var_type=node.var_type
        if var_type!=None:
            if var_name in symbol_table.symbols.keys():
                raise Exception('variable declared twice')
            symbol_table.settype(var_name, var_type)
        if var_type==None:
            if var_name not in symbol_table.symbols.keys():
                raise Exception('variable not declared')
        value = self.visit(node.value_node)

        # Update the variable in the symbol table
        var_type=symbol_table.types[var_name]
        if var_type==INT_T:
            for i in value:
                arr.append(int(i))
            symbol_table.set(var_name,arr)
        elif var_type==DEC_T:
            for i in value:
                arr.append(int(i))
            symbol_table.set(var_name,arr)
        elif var_type==WORD_T:
            symbol_table.set(var_name,value)

    def visit_arraynode(self, node):
        arr=[]
        num=self.visit(node.num)
        expressions=node.expressions
        if node.expressions==None:
            for i in range(num):
                arr.append(0)
            return arr
        else:
            if num!=len(expressions):
                raise Exception('Expected same values as of size')
            for i in expressions:
                arr.append(self.visit(i))
        return arr
    

    def visit_arraysingularassignnode(self,node):
        arr=symbol_table.symbols[node.var_name]
        idx=self.visit(node.idx)
        val=self.visit(node.value)
        arr[idx]=val

    def visit_arrayvalnode(self,node):
        arr=symbol_table.symbols[node.var_name]
        idx=self.visit(node.idx)
        return arr[idx]

    def visit_typecastnode(self,node):
        val=self.visit(node.value)
        return chr(val)
    def visit_UnaryOpNode(self, node):
        if not hasattr(node.op_tok, 'type'):
           raise Exception(f"Invalid op_tok: expected Token, got {type(node.op_tok).__name__}")
        value = self.visit(node.node)

       # error = None

        if node.op_tok.type == MIN:
            value = -value
        elif node.op_tok.type == NOT:
            value = not(value)
        return value

    def visit_blocknode(self,node):
        symb=SymbolTable()
        symb.copy(symbol_table) 
        for statement in node.statements:
            self.visit(statement)
        keys_to_remove = [i for i in symbol_table.symbols.keys() if i not in symb.symbols.keys()]
        for i in keys_to_remove:
            symbol_table.remove(i)       

    def visit_Ifnode(self,node):
        j=0
        for condition,cases in node.cases:
            if(self.visit(condition)==True):
                j=1
                for case in cases:
                    self.visit(case)
        if node.elsecase and j==0:
            for case in node.elsecase:
                          self.visit(case)  

    def visit_Whilenode(self,node):
        symb=SymbolTable()
        symb.copy(symbol_table)
        while(self.visit(node.condition)):
            for cases in node.expressions:
                self.visit(cases) 
        keys_to_remove = [i for i in symbol_table.symbols.keys() if i not in symb.symbols.keys()]
        for i in keys_to_remove:
            symbol_table.remove(i)       
    def visit_Fornode(self,node):
        symb=SymbolTable()
        symb.copy(symbol_table) 
        self.visit(node.decl)
        while(self.visit(node.cond)):
            for cases in node.expressions:
                self.visit(cases) 
                self.visit(node.inc)
        keys_to_remove = [i for i in symbol_table.symbols.keys() if i not in symb.symbols.keys()]
        for i in keys_to_remove:
            symbol_table.remove(i)      

    def visit_givenode(self,node):
        value=self.visit(node.token)
        print(value)

    def interpret(self):
        return self.visit(self.tree)
    
    
            
#######################################
# RUN
#######################################

def main():
    parser = argparse.ArgumentParser(
        description='SWASPI - Simple WASP Interpreter'
    )
    parser.add_argument('inputfile', help='WASP source file')
    parser.add_argument(
        '--scope',
        help='Print scope information',
        action='store_true',
    )
    args = parser.parse_args()
    global _SHOULD_LOG_SCOPE
    _SHOULD_LOG_SCOPE = args.scope

    text = open(args.inputfile, 'r').read()
    lexer = Lexer(text)
    try:
        tokens, error = lexer.make_tokens()
    except Exception as e:
        print(f"Error: {e}")
    #print(tokens)
    # try:    
    # Parser(tokens).statement_list()
    # except Exception as e:
    #     print(f"Error: {e}")  
    tree_list=   Parser(tokens).statement_list()
    try:    
        for i in tree_list:
            Interpreter(i).interpret()
    except Exception as e:
        print(f"Error: {e}")   
 

if __name__ == '__main__':
    main()