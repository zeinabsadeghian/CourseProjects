import ply.yacc as yacc
import lex
import ast
import ply

from lex import tokens

import sys
import logging
from lex import tokens as tok

binops = {
    '+' : 'add',
    '-' : 'minus',
    '*' : 'mult',
    '%' : 'remain',
    '/' : 'div',
    '&&' : 'and',
    '||' : 'or',
    '==' : 'eq',
    '!=' : 'neq',
    '<' : 'lt',
    '<=' : 'leq',
    '>' : 'gt',
    '>=' : 'geq'
}


precedence = (
    ('right', 'ASSIGN'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQ', 'NEQ'),
    ('nonassoc', 'LEQ', 'GEQ', 'LT', 'GT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE','REMAIN'),
    ('right', 'NOT'),
    ('right', 'UMINUS'),
    ('right', 'ELSE'),
    ('right', 'RPAREN'),
)

program_node = ast.Node("program")
current_type = None
current_context = None
current_modifiers = None
current_class = None
current_vartable = None
current_variable_kind = None
current_storage_kind = None

def init():
    lex.error_flag = False


start = 'pgm'

def p_pgm(p):
    'pgm : class_decl_list'
    p[0] = p[1]
    p[0].other_name()
    pass

def p_class_decl_list_nonempty(p):
    'class_decl_list : class_decl class_decl_list'
    p[0] = p[1]

def p_class_decl_list_empty(p):
    'class_decl_list : '
    p[0] = []
    pass

def p_class_decl(p):
    'class_decl : class_decl_head LBRACE class_body_decl_list RBRACE'
    p[0] = ast.Node("class dec",children=[p[1],p[2],p[3],p[4]])
    #print(type(p[4]))
    pass
def p_class_decl_error(p):
    'class_decl : class_decl_head LBRACE error RBRACE'
    # error in class declaration; skip to next class decl.
    pass

def p_class_decl_head(p):
    'class_decl_head : CLASS ID extends'
    #global current_class, current_context
    #cid = p[2]
    #sc = p[3]
    #c = ast.lookup(ast.classtable, cid)
    #if (c != None):
    #    signal_error('Class {0} already exists!'.format(cid), p.lineno(2))
    #else:
    #    c = ast.Class(cid, sc)
    #    ast.addtotable(ast.classtable, cid, c)
    #current_class = c
    #current_context = 'class'
    p[0] = ast.Node("class decleration header",children=[p[1],p[2],p[3]])
    pass


def p_extends_id(p):
    'extends : EXTENDS ID '
    #cid = ast.lookup(ast.classtable, p[2])
    #if (not cid):
    #    signal_error('Class {0} does not exist!'.format(p[2]), p.lineno(2))
    #p[0] = cid
    p[0] = ast.Node("extend id",children=[p[1],p[2]])
    pass


def p_extends_empty(p):
    ' extends : '
    p[0] = None
    pass

def p_class_body_decl_list_plus(p):
    'class_body_decl_list : class_body_decl_list class_body_decl'
    p[0] = ast.Node("body",children=[p[1],p[2]])
    pass
def p_class_body_decl_list_single(p):
    'class_body_decl_list : class_body_decl'
    p[0] = p[1]
    pass

def p_class_body_decl_field(p):
    'class_body_decl : field_decl'
    p[0] = p[1]
    pass
def p_class_body_decl_method(p):
    'class_body_decl : method_decl'
    p[0] = p[1]
    pass
def p_class_body_decl_constructor(p):
    'class_body_decl : constructor_decl'
    p[0] = p[1]
    pass

def p_field_decl(p):
    'field_decl : mod var_decl'
    p[0] = ast.Node("fields",children=[p[1],p[2]])
    pass

def p_method_decl(p):
    'method_decl : method_header LPAREN param_list_opt RPAREN block'
    #m = p[1]
    #m.update_body(p[5])
    p[0] = ast.Node("method dec",children=[p[1],p[2],p[3],p[4],p[5]])

def p_method_decl_header_void(p):
    'method_header : mod VOID ID'
    global current_context, current_vartable, current_storage_kind
    current_context = 'method'
    #(v, s) = current_modifiers
    #m = ast.Method(p[3], current_class, v, s, ast.Type('void'))
    #current_class.add_method(m)
    #current_vartable = m.vars
    #current_storage_kind = s
    #p[0] = m
    p[0] = ast.Node("method decleration",children=[p[1],p[2],p[3]])

def p_method_decl_header_nonvoid(p):
    'method_header : mod type ID'
    #global current_context, current_vartable, current_storage_kind
    #current_context = 'method'
    #(v, s) = current_modifiers
    #m = ast.Method(p[3], current_class, v, s, current_type)
    #current_class.add_method(m)
    #current_vartable = m.vars
    #current_storage_kind = s
    #p[0] = m
    p[0] = ast.Node("method decleration no void",children=[p[1],p[2],p[3]])

def p_constructor_decl(p):
    'constructor_decl : constructor_header LPAREN param_list_opt RPAREN block'
    #c = p[1]
    #c.update_body(p[5])

def p_constructor_header(p):
    'constructor_header : mod ID'
    global current_context, current_vartable, current_storage_kind
    current_context = 'method'
    #(v, s) = current_modifiers
    #c = ast.Constructor(p[2], v)
    # note: 's' is ignored.  should we signal error for s?
    #current_class.add_constructor(c)
    #current_vartable = c.vars
    current_storage_kind = 'instance'
    #p[0] = c
    p[0] = ast.Node("header of constructor",children=[p[1],p[2]])

def p_mod(p):
    'mod : visibility_mod storage_mod'
    global current_modifiers
    current_modifiers = (p[1], p[2])

def p_visibility_mod_pub(p):
    'visibility_mod : PUBLIC'
    p[0] = ast.Node('public',children=p[1])

def p_visibility_mod_priv(p):
    'visibility_mod : PRIVATE'
    p[0] = ast.Node('private',children=p[1])

def p_visibility_mod_empty(p):
    'visibility_mod : '
    p[0] = ast.Node('private')

def p_storage_mod_static(p):
    'storage_mod : STATIC'
    p[0] = ast.Node('static',children=p[1])

def p_storage_mod_empty(p):
    'storage_mod : '
    p[0] = ast.Node('instance')


def p_var_decl(p):
    'var_decl : type var_list SEMICOLON'
    p[0] = ast.Node("var decleration",children=[p[1], p[2],p[3]])


def p_type_int(p):
    'type :  INT'
    global current_type
    p[0] = ast.Node("int", children=p[1])
    #current_type = ast.Type('int')
def p_type_bool(p):
    'type :  BOOLEAN'
    global current_type
    p[0] = ast.Node("bool", children=p[1])
    #current_type = ast.Type('boolean')
def p_type_float(p):
    'type :  FLOAT'
    global current_type
    p[0] = ast.Node("type",children=p[1])
    #current_type = ast.Type('float')
def p_type_id(p):
    'type :  ID'
    global current_type
    #baseclass = ast.lookup(ast.classtable, p[1])
    #if (baseclass == None):
    #    signal_error('Class {0} does not exist!'.format(p[1]), p.lineno(1))
    p[0] = ast.Node("typeid",children=p[1])
    #current_type = ast.Type(baseclass)

def p_var_list_plus(p):
    'var_list : var_list COMMA var'
    if type(p[1]) == list:
        p[0] = ast.Node("var list", children=[p[1] + [p[2]]])
    elif type(p[1]) == ast.Node:
        p[0] = ast.Node("var list",children=[p[1],p[2].children])
def p_var_list_single(p):
    'var_list : var'
    p[0] = ast.Node("var list", children=[p[1]])

def p_var_id(p):
    'var : ID dim_star'
    p[0] = p[1]
    #print(p[1])
    global current_class, current_context, current_modifiers, current_type
    global current_vartable, current_variable_kind
#    if p[2] == 0:
#        ftype = current_type
#    else:
#       ftype = ast.Type(current_type, params=p[2])
#    if (current_context == 'class'):
     #   if (current_class.lookup_field(p[1])):
     #       signal_error('Duplicate definition of field {0} in class!'.format(p[1]), p.lineno(1))
     #   else:
     #       (v,s) = current_modifiers
     #       f = ast.Field(p[1], current_class, v, s, ftype)
     #       current_class.add_field(p[1], f)
    #else:
        # we're in a method/constructor
        # Then, current_vartable is the current table of variables
        #if (current_vartable.find_in_current_block(p[1])):
        #    signal_error('Duplicate definition of variable {0} within the same block!'.format(p[1]), p.lineno(1))
        #else:
        #    current_vartable.add_var(p[1], current_variable_kind, ftype)

def p_param_list_opt(p):
    'param_list_opt : params_begin param_list params_end'
    p[0] = ast.Node("param list opt", children=[p[1], p[2], p[3]])
    pass
def p_param_list_empty(p):
    'param_list_opt : params_end'
    p[0] = p[1]
    pass

def p_param_list(p):
    'param_list : param_list COMMA param'
    p[0] = ast.Node("param list",children=[p[1],p[2],p[3]])
    pass
def p_param_list_single(p):
    'param_list : param'
    p[0] = p[1]
    pass

def p_param(p):
    'param : type var'
    p[0] = ast.Node("param", children=[p[1], p[2]])
    pass

def p_params_begin(p):
    'params_begin : '
    p[0] = []
    global current_variable_kind
    current_variable_kind = 'formal'

def p_params_end(p):
    'params_end : '
    p[0] = []
    global current_variable_kind
    current_variable_kind = 'local'

# Statements

def p_block(p):
    'block : LBRACE block_begin stmt_list block_end RBRACE'
    p[0] = ast.Node("block",children=[p[1], p[2],p[3],p[4],p[5]])
    #print(p[3])
def p_block_error(p):
    'block : LBRACE block_begin stmt_list error block_end RBRACE'
    p[0] = ast.SkipStmt(p.lineno(1))
    # error within a block; skip to enclosing block

def p_block_begin(p):
    'block_begin : '
    p[0] = []
    global current_vartable
    #current_vartable.enter_block()

def p_block_end(p):
    'block_end : '
    p[0] = []
    global current_vartable
    #current_vartable.leave_block()

def p_stmt_list_empty(p):
    'stmt_list : '
    p[0] = []
def p_stmt_list(p):
    'stmt_list : stmt_list stmt'
    if type(p[1]) == list:
        p[0] = ast.Node("stmt list",children=[p[1] + [p[2]]])
        #p[0] = [p[1] + [p[2]]]
    elif type(p[1]) == ast.Node:
        p[0] = ast.Node("stmt list",children=[p[1], p[2].children])
        #p[0] = [p[1], p[2].children]
    #print("statemnetlist")

def p_stmt_if_else(p):
    'stmt : IF LPAREN expr RPAREN stmt ELSE stmt'
    print("in this stetment")
    p[0] = ast.Node("IfStmtElse",children=[p[1], p[2], p[3],p[4],p[5],p[6],p[7]])

def p_stmt_if_noelse(p):
    'stmt : IF LPAREN expr RPAREN stmt'
    p[0] = ast.Node("IfStmtNoelse",children=[p[1], p[2],p[3],p[4],p[5]])

def p_stmt_while(p):
    'stmt : WHILE LPAREN expr RPAREN stmt'
    p[0] = ast.Node("while stmt",children = [p[1], p[2],p[3],p[4],p[5]])
def p_stmt_for(p):
    'stmt : FOR LPAREN stmt_expr_opt SEMICOLON expr_opt SEMICOLON stmt_expr_opt RPAREN stmt'
    p[0] = ast.Node("for stmt",children = [p[1], p[2], p[3], p[4],p[5],p[6],p[7],p[8],p[9]])
def p_stmt_return(p):
    'stmt : RETURN LPAREN expr_opt RPAREN SEMICOLON'
    p[0] = ast.Node("ret stmt",children = [p[1],p[2],p[3],p[4],p[5]])
    print("return stmt")
def p_stmt_stmt_expr(p):
    'stmt : stmt_expr SEMICOLON'
    p[0] = ast.Node("stmt",children = [p[1], p[2]])
def p_stmt_break(p):
    'stmt : BREAK SEMICOLON'
    p[0] = ast.Node("breakstmt",children=[p.lineno(1),p[1]])
def p_stmt_continue(p):
    'stmt : CONTINUE SEMICOLON'
    p[0] = ast.Node("continuestmt",children=[p.lineno(1),p[1]])

def p_stmt_block(p):
    'stmt : block'
    p[0] = p[1]
def p_stmt_var_decl(p):
    'stmt : var_decl'
    p[0] = ast.Node("stmt",children=p[1])
def p_stmt_empty(p):
    'stmt : SEMICOLON'
    p[0] = ast.Node("empty stmt",children=p.lineno(1))
def p_stmt_error(p):
    'stmt : error SEMICOLON'
    signal_error("Invalid statement", p.lineno(2))
    lex.error_flag = True
    p[0] = ast.Node("error stmt", children=p.lineno(2))
#def p_stmt_method_inv(p):
#    'stmt : method_invocation'
#    p[0] = p[1]

# Expressions
def p_literal_int_const(p):
    'literal : INT_CONST'
    name = p[1]
    #print(p[1])
    p[0] = ast.Node(name, children=p[1])

def p_literal_float_const(p):
    'literal : FLOAT_CONST'
    p[0] = ast.Node('float', children=p[1])
def p_literal_string_const(p):
    'literal : STRING_CONST'
    p[0] = ast.Node('string', children=p[1])
    print(p[1])
def p_literal_null(p):
    'literal : NULL'
    p[0] = ast.Node('Null', children=p[1])
def p_literal_true(p):
    'literal : TRUE'
    p[0] = ast.Node('True', children=p[1])
def p_literal_false(p):
    'literal : FALSE'
    p[0] = ast.Node('False',children=p[1])

def p_primary_literal(p):
    'primary : literal'
    p[0] = p[1]
def p_primary_this(p):
    'primary : THIS'
    #if (current_storage_kind == 'instance'):
    p[0] = ast.Node("this",children=p[1])
    #else:
    #    signal_error("'this' expression cannot be used in a static context", p.lineno(1))
    #    p[0] = None
def p_primary_super(p):
    'primary : SUPER'
    #if (current_storage_kind == 'instance'):
    p[0] = ast.Node(children=p[1])
    #else:
    #    signal_error("'super' expression cannot be used in a static context", p.lineno(1))
    #    p[0] = None
def p_primary_paren(p):
    'primary : LPAREN expr RPAREN'
    p[0] = p[2]

def p_primary_newobj(p):
    'primary : NEW ID LPAREN args_opt RPAREN'
    #cname = p[2]
    #c = ast.lookup(ast.classtable, cname)
    #if (c != None):
    p[0] = ast.Node(p[2],children=[p[1], p[2], p[3], p[4],p[5]])
    #else:
    #    signal_error('Class "{0}" in "new" not defined (yet?)'.format(cname), p.lineno(2))

def p_primary_lhs(p):
    'primary : lhs'
    p[0] = p[1]
def p_primary_method_invocation(p):
    'primary : method_invocation'
    p[0] = p[1]

def p_args_opt_nonempty(p):
    'args_opt : arg_plus'
    p[0] = p[1]
def p_args_opt_empty(p):
    'args_opt : '
    p[0] = []

def p_args_plus(p):
    'arg_plus : arg_plus COMMA expr'
    if type(p[1]) == ast.Node:
        p[0] = ast.Node("args",children=[p[1],p[2] , p[3].children])
    elif type(p[1]) == list:
        p[0] = ast.Node("args", children=[p[2],p[1] , p[3]])

def p_args_single(p):
    'arg_plus : expr'
    p[0] = ast.Node(p[1], children=p[1])


    #p[0] = [p[1]]

def p_lhs(p):
    '''lhs : field_access
           | array_access'''
    p[0] = p[1]

def p_field_access_dot(p):
    'field_access : primary DOT ID'
    p[0] = ast.Node("field_access_dot",children=[p[1],p[2], p[3]])
def p_field_access_id(p):
    'field_access : ID'
    vname = p[1]
    #v = current_vartable.find_in_scope(vname)
    #if (v != None):
        # local variable in current scope
    p[0] = ast.Node(vname,children=p[1])
    #else:
        #c = ast.lookup(ast.classtable, vname)
        #if (c != None):
            # there is a class with this name
            #p[0] = ast.ClassReferenceExpr(c, p.lineno(1))
        #else:
            # reference to a non-local var; assume field
            #p[0] = ast.FieldAccessExpr(ast.ThisExpr(p.lineno(1)), vname, p.lineno(1))

def p_array_access(p):
    'array_access : primary LBRACKET expr RBRACKET'
    p[0] = ast.Node("arreyaccess",children=[p[1], p[2],p[3], p[4]])

def p_method_invocation(p):
    'method_invocation : field_access LPAREN args_opt RPAREN'
    #if (isinstance(p[1], ast.FieldAccessExpr)):
    p[0] = ast.Node("method_inv",children=[p[1], p[2], p[3], p[4]])
    #else:
        # p[1] is a local variable or a class name
     #   if (isinstance(p[1], ast.VarExpr)):
     #       name = p[1].var.name
     #   else:
     #       name = p[1].classref.name
     #   signal_error('Non-method name "{0}" used in a method invocation'.format(name), p.lineno(2))

def p_expr_basic(p):
    '''expr : primary
            | assign
            | new_array'''
    p[0] = p[1]

def p_expr_binop(p):
    '''expr : expr PLUS expr
            | expr REMAIN expr
            | expr MINUS expr
            | expr MULTIPLY expr
            | expr DIVIDE expr
            | expr EQ expr
            | expr NEQ expr
            | expr LT expr
            | expr LEQ expr
            | expr GT expr
            | expr GEQ expr
            | expr AND expr
            | expr OR expr
            '''

    p[0] = ast.Node("binop",children=[p[1], p[2],p[3]])
    print(p[1])

def p_expr_unop_plus(p):
    'expr : PLUS expr %prec UMINUS'
    p[0] = p[1]

#def p_expr_const(p):
#    'expr : INT_CONST'
#    p[0] = p[1]

def p_expr_unop_minus(p):
    'expr : MINUS expr %prec UMINUS'
    p[0] = ast.Node('uminus',children=[ p[1], p[2]])
def p_expr_unop_not(p):
    'expr : NOT expr'
    p[0] = ast.Node('neg', children=[p[1],p[2]])

def p_assign_equals(p):
    'assign : lhs ASSIGN expr'
    p[0] = ast.Node("assign",children = [p[1], p[2],p[3]])

def p_assign_post_inc(p):
    'assign : lhs INC'
    p[0] = ast.Node("inc post",children=[p[1],p[2]])
def p_assign_pre_inc(p):
    'assign : INC lhs'
    p[0] = ast.Node("inc pre",children=[p[1],p[2]])
def p_assign_post_dec(p):
    'assign : lhs DEC'
    p[0] = ast.Node("DEC PRE",children=p[1])
def p_assign_pre_dec(p):
    'assign : DEC lhs'
    p[0] = ast.Node("DEC post",children=p[2])

def p_new_array(p):
    'new_array : NEW type dim_expr_plus dim_star'
    if (p[4] == 0):
        t = p[2]
    #else:
    #    t = ast.Type(p[2], params=p[4])
    p[0] = ast.Node("New Array",children=p[3])

def p_dim_expr_plus(p):
    'dim_expr_plus : dim_expr_plus dim_expr'
    p[0] = p[1] + [p[2]]
def p_dim_expr_single(p):
    'dim_expr_plus : dim_expr'
    p[0] = [p[1]]

def p_dim_expr(p):
    'dim_expr : LBRACKET expr RBRACKET'
    p[0] = p[2]

def p_dim_star(p):
    'dim_star : LBRACKET RBRACKET dim_star'
    p[0] = p[3]+1
def p_dim_star_empty(p):
    'dim_star : '
    p[0] = 0

def p_stmt_expr(p):
    '''stmt_expr : assign
                 | method_invocation'''
    p[0] = p[1]

def p_stmt_expr_opt(p):
    'stmt_expr_opt : stmt_expr'
    p[0] = p[1]
def p_stmt_expr_empty(p):
    'stmt_expr_opt : '
    p[0] = None

def p_expr_opt(p):
    'expr_opt : expr'
    p[0] = p[1]
def p_expr_empty(p):
    'expr_opt : '
    p[0] = None


def p_error(p):
    if p is None:
        signal_error("Unexpected end-of-file", 'end')
    else:
        signal_error("Unexpected token '{0}'".format(p.value), p.lineno)

parser = yacc.yacc()

def signal_error(string, lineno):
    print ("{1}: {0}".format(string, lineno))
    lex.error_flag = True

def from_file(filename):
    try:
        with open(filename, "rU") as f:
            init()
            parser.parse(f.read(), lexer=ply.lex.lex(module=lex), debug=None)
        return not lex.error_flag
    except IOError as e:
        print("I/O error: %s: %s" % (filename, e.strerror))


if __name__ == "__main__" :
    f = open(sys.argv[1], "r")
    logging.basicConfig(
            level=logging.CRITICAL,
    )
    log = logging.getLogger()
    res = parser.parse(f.read(), lexer=ply.lex.lex(module=lex), debug=log)

    if parser.errorok :
        print("Parsing succeeded")
    else:
        print("Parsing failed")