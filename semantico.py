#!/usr/bin/env python2.7.12
#-*- coding: utf-8 -*-

import unicodedata
import re
from compilador import *
import hashlib

tokenList = token
lexemaList = lexema
arq = open('saida.txt','w')

id_node = None

int_type = 0
float_type = 1
dicionario = {}

class Operand():
    def __init__(self):
        self.name = None;
        self.temporary=None;
        self.tableEntry=None;
        self.tipo = None;
        self.live = None;
        self.next_use = None;

cont = 0;
class Temp():
    def __init__(self):
        global cont;
        self.name = "t" + str(cont);
        cont = cont + 1;
cont3 = 0
class Label(Operand):

    def __init__(self):
        global cont3;
        self.name = "L"+str(cont3);
        cont3= cont3+1;

class AST(object):
    def __init__(self, nome, father):
         self.nome = nome;
         self.children = []
         self.father = father #cria uma referência para o pai
         self.tipo = None  #inteiro ou ponto flutuante
         self.value = None
         self.hasParenthesis = None
         self.address = None
         self.next = None

    def __str__(self, level=0):
        ret = "\t"*level+ repr(self) +"\n"
        for child in self.children:
            if (child != None):
                ret += child.__str__(level+1) #level+1
                #print(child.__str__())
        return ret

    def __repr__(self):
        return self.nome

    def __evaluate__(self):
        print('Avaliando nó ' + str(self.nome))
        for child in self.children:
            if (child != None):
                x = child.__evaluate__()



    def __checkTypes__(self):
        for child in self.children:
            if (child != None):
                child.__checkTypes__()

    #code = " ";
    #for child in self.children:
            #code += child.__codegen__();
    #return code
    def generateCode(self):
        for child in self.children:
            child.generateCode();

class Compound(AST):
    """Represents a 'BEGIN ... END' block"""
    def __init__(self,father):
        AST.__init__(self,'Block',father)
        print('Criando um nó do tipo Block.')
        #self.children = []
    def __repr__(self):
        return self.nome

    def __codegen__(self):
        code = " ";
        for child in self.children:
            code += child.__codegen__();
        return "{" + code + "}"

class Attr(AST):
    def __init__(self, left, op, right, father):
        AST.__init__(self,'Assign',father);
        print('Criando um nó do tipo Assign.')
        self.children.append(left)
        self.children.append(right)
        self.left = left
        self.token = self.op = op
        self.right = right
        self.isDecl = None

    def __repr__(self):
        return self.nome

    def __setIsDecl__(self, isDecl):
        self.isDecl = isDecl

    def __evaluate__(self):
        print('Avaliando atribuição.')
        id_node = self.children[0]
        lex = id_node.lexema
        tipo = dicionario[lex][0]
        dict3 = {}
        expr_value = self.children[1].__evaluate__()
        if(expr_value != True or expr_value != False):
        	dict3[lex] = (tipo, expr_value)
        	dicionario.update(dict3)


    def __codegen__(self):
        if (self.isDecl):
            id_node = self.children[0]
            te = tabSimbolos.getEntry(id_node.token.lexema)
            return typeNames[te.tipo] + " " + self.children[0].__codegen__() + " = " + self.children[1].__codegen__() + ";"
        else:
            return self.children[0].__codegen__() + " = " + self.children[1].__codegen__() + ";"

    def __checkTypes__(self):
        if(self.children[0] != None and self.children[1] != None):
            if(self.children[0].__checkTypes__() == self.children[1].__checkTypes__()):
                print('Tipos compatíveis.')
                return True
            elif (self.children[0].__checkTypes__() < self.children[1].__checkTypes__()):
                print('Tipos incompatíveis. Será realizada uma conversão permitida pela hierarquia de tipos.')
                self.children[0].__convertTo__(self.children[1].tipo)
                return True
            else:
                print('Tipos incompatíveis. Será realizada uma conversão permitida pela hierarquia de tipos.')
                self.children[1].__convertTo__(self.children[0].tipo)
                return True

    def generateCode(self):
        self.children[0].generateCode();
        self.children[1].generateRValueCode();
        self.children[0].address.temporary = (self.children[1].address.temporary);
        arq.write(self.children[0].lexema + " = " + self.children[1].address.name + "\n");  #

class If(AST):
    def __init__(self, exp, c_true, c_false, father):
        AST.__init__(self, 'If', father)
        print('Criando um nó do tipo If.')
        self.children.append(exp)
        self.children.append(c_true)
        self.children.append(c_false)
        self.exp = exp;
        self.c_true = c_true;
        self.c_false = c_false;

    def __init__(self,nome):
    	AST.__init__(self, nome, None)

    def __repr__(self):
        return self.nome

    def __evaluate__(self):
    	print('Avaliando If.')
        valor = self.children[0].__evaluate__()
        if(valor == True):
            self.children[1].__evaluate__()
        else:
        	if(len(self.children) is not 2):
        		self.children[2].__evaluate__()

    def generateCode(self):
        self.next = Label();
        if (len(self.children) == 3): #Tem o else
            self.children[0].true_label = Label();
            self.children[0].false_label = Label();
            self.children[0].next = self.children[1].next = self.next;
            self.children[0].generateBranchCode(); #Gera código da expressão
            if (self.children[0].address != None):
                arq.write("if " + self.children[0].address.name + " == 0 goto " + self.children[0].false_label.name + "\n");
            else:

                arq.write( self.children[0].true_label.name + ":");
            self.children[1].generateCode();
            arq.write( "goto " + self.next.name + "\n");
            arq.write(self.children[0].false_label.name + ":");
            self.children[2].generateCode();

        else:
            self.children[0].true_label = Label();
            self.children[0].false_label = self.children[1].next = self.next;
            self.children[0].generateBranchCode(); #Gera código da expressão
            if (self.children[0].address != None):
                arq.write("if " + self.children[0].address.name + " == 0 goto " + self.children[0].false_label.name + "\n");
            else:

                arq.write(self.children[0].true_label.name + ":");
            self.children[1].generateCode();

        arq.write(self.next.name + ":");

# class For(AST):
#     def __init__(self, exp, commands, father):
#         AST.__init__(self,'For', father)
#         print('Criando um nó do tipo For.')
#         self.children.append(exp)
#         self.children.append(commands)
#         self.exp = exp;
#         self.commands = commands;
#     def __init__(self,nome):
#     	AST.__init__(self, nome, None)

#     def __repr__(self):
#         return self.nome

    # def __evaluate__(self):
    # 	print('Avaliando For.')
    #     valor = self.children[0].__evaluate__()
    #     while(valor == True):
    #     	self.children[1].__evaluate__()
    #     	valor = self.children[0].__evaluate__()


class While(AST):
    def __init__(self, exp, commands, father):
        AST.__init__(self,'While', father)
        print('Criando um nó do tipo While.')
        self.children.append(exp)
        self.children.append(commands)
        self.exp = exp;
        self.commands = commands;
    def __init__(self,nome):
    	AST.__init__(self, nome, None)

    def __repr__(self):
        return self.nome

    def __evaluate__(self):
    	print('Avaliando While.')
        valor = self.children[0].__evaluate__()
        while(valor == True):
        	self.children[1].__evaluate__()
        	valor = self.children[0].__evaluate__()

    def generateCode(self):
        self.begin = Label();
        self.children[0].true_label = Label();
        self.children[0].false_label = self.next = Label();
        self.children[1].next = self.begin;
 
 
        arq.write(self.begin.name + ":");
        self.children[0].generateBranchCode() ; #Gera código para a expressão
        if (self.children[0].address != None):
            arq.write("if " + self.children[0].address.name + " == 0 goto " + self.children[0].false_label.name + "\n");
        else:
            arq.write(self.children[0].true_label.name + ":");
        self.children[1].generateCode() ; #Gera código para a lista de comandos
        arq.write("goto " + self.begin.name + "\n");
        arq.write(self.next.name + ":");


class Read(AST):
    def __init__(self, id_, father):
        AST.__init__(self,'Read', father)
        print('Criando um nó do tipo Read.')
        self.children.append(id_)
        self.id = id_;
    def __init__(self,nome):
    	AST.__init__(self, nome, None)
    def __repr__(self):
        return self.nome

class Print(AST):
    def __init__(self, exp, father):
        AST.__init__(self,'Print', father)
        print('Criando um nó do tipo Print.')
        self.children.append(exp)
        self.exp = exp;
    def __init__(self,nome):
		AST.__init__(self, nome, None)

    def __repr__(self):
        return self.nome

class BinOp(AST):
    def __init__(self, nome, left, op, right, father):
        AST.__init__(self,nome, father)
        self.children.append(left)
        self.children.append(right)
        self.left = left
        #self.token =
        self.op = op
        self.right = right

    def __repr__(self):
        #self.left.repr();
        return self.op

    def __evaluate__(self):
        print('Avaliando nó ' + str(self.nome))
        for child in self.children:
            if (child != None):
                return child.__evaluate__()

    def __checkTypes__(self):
        if(self.children[0] != None and self.children[1] != None):
            if(self.children[0].__checkTypes__() == self.children[1].__checkTypes__()):
                print('Tipos compatíveis.')
                return True
            elif (self.children[0].__checkTypes__() < self.children[1].__checkTypes__()):
                print('Tipos incompatíveis. Será realizada uma conversão permitida pela hierarquia de tipos.')
                self.children[0].__convertTo__(self.children[1].tipo)
                return True
            else:
                print('Tipos incompatíveis. Será realizada uma conversão permitida pela hierarquia de tipos.')
                self.children[1].__convertTo__(self.children[0].tipo)
                return True

    def __codegen__(self):
        return self.left.__codegen__() + self.op + self.right.__codegen__()

class LogicalOp(BinOp):
    def __init__(self, left, op, right, father):
        BinOp.__init__(self,'LogicalOp',left, op, right, father)
        print('Criando um nó do tipo LogicalOp com operador ' + str(op))

    def __evaluate__(self):
    	print('Avaliando LogicalOp.')
    	a = self.children[0].__evaluate__()
        b = self.children[1].__evaluate__()

    	if(self.op == '&&'):
        	if(a is True and b is True):
        		c = True
        		return c
        	else:
        		c = False
        		return c
        elif(self.op == '||'):
        	if(a is True or b is True):
        		c = True
        		return c
        	else:
        		c = False
        		return c
    def generateBranchCode(self):
        if (self.op == "||"):
            self.children[0].true_label = self.true_label;
            self.children[0].false_label = Label();
            self.children[1].true_label = self.true_label;
            self.children[1].false_label = self.false_label;
            self.children[0].generateBranchCode();
            if (self.children[0].address != None):
                arq.write( "if " + self.children[0].address.name + " != 0 goto " + self.children[0].true_label.name + "\n");
            else:
                arq.write( self.children[0].false_label.name + ":");
            self.children[1].generateBranchCode();
            if (self.children[1].address != None):
                arq.write( "if " + self.children[1].address.name + " == 0 goto " + self.children[1].false_label.name + "\n");
                arq.write( "goto " + self.children[1].true_label.name + "\n");
        elif (self.op == "&&"):
            self.children[0].true_label = Label();
            self.children[0].false_label = self.false_label;
            self.children[1].true_label = self.true_label;
            self.children[1].false_label = self.false_label;
            self.children[0].generateBranchCode();
            if (self.children[0].address != None): #Verifica se o nó filho é um Id, Num ou ArithOp verificando se ele possui endereço
                 arq.write( "if " + self.children[0].address.name + " == 0 goto " + self.children[0].false_label.name + "\n");
            else:
                arq.write( self.children[0].true_label.name + ":");
            self.children[1].generateBranchCode() ;
            if (self.children[1].address != None):
                arq.write( "if " + self.children[1].address.name + " == 0 goto " + self.children[1].false_label.name + "\n");
                arq.write( "goto " + self.children[1].true_label.name + "\n");

    def generateRValueCode(self):
        self.true_label = Label()
        self.false_label = Label()
        self.next = Label()
        self.address = Operand()
        if(self.op == "||"):
            self.children[0].generateRValueCode()
            self.children[1].generateRValueCode()
            teste = self.children[0].address.name + " " + "!= 0"
            teste1 = self.children[1].address.name + " " + "!= 0"
            temp = Temp()

            arq.write("if " + teste + " goto " + self.true_label.name + "\n")

            arq.write("if " + teste1 + " goto " + self.true_label.name + "\n")
            arq.write(temp.name+"=0\n"+" goto "+self.next.name+"\n");
            arq.write(self.true_label.name+":"+temp.name+"=1\n");
            self.address.temporary = temp
            self.address.name = temp.name
            arq.write(self.next.name+":")
        elif(self.op == "&&"):
            self.children[0].generateRValueCode()
            self.children[1].generateRValueCode()
            teste = self.children[0].address.name + " " + "== 0"
            teste1 = self.children[1].address.name + " " + "== 0"
            temp = Temp()

            arq.write("if " + teste + " goto " + self.false_label.name + "\n")

            arq.write("if " + teste1 + " goto " + self.false_label.name + "\n")
            arq.write(temp.name+"= 1\n"+" goto "+self.next.name+"\n");
            arq.write(self.false_label.name+":"+temp.name+"=0\n");
            self.address.temporary = temp
            self.address.name = temp.name
            arq.write(self.next.name+":")

class ArithOp(BinOp):
    def __init__(self, left, op, right, father):
        BinOp.__init__(self,'ArithOp',left, op, right, father)
        print('Criando um nó do tipo ArithOp com operador ' + str(op))

    def __evaluate__(self):
        a = self.children[0].__evaluate__()
        b = self.children[1].__evaluate__()
        if(self.op == '+'):
        	c = float(a) + float(b)
        	return c
        elif(self.op == '-'):
        	c = float(a) - float(b)
        	return c
        elif(self.op == '*'):
            c = float(a) * float(b)
            return c
        elif(self.op == '/'):
            c = float(a) / float(b)
            return c

    def __codegen__(self):
        return self.left.__codegen__() + self.op + self.right.__codegen__()

    def generateBranchCode(self):
        self.children[0].generateBranchCode();
        self.children[1].generateBranchCode();
        temp = Temp();
        self.address = Operand();
        self.address.temporary = temp;
        self.address.name = temp.name;
        arq.write( temp.name + " = " + self.children[0].address.name + " " + self.op + " " + self.children[1].address.name + "\n");

    def generateRValueCode(self):
        self.children[0].generateRValueCode();
        self.children[1].generateRValueCode();
        temp = Temp();
        self.address = Operand();
        self.address.temporary = temp;
        self.address.name = temp.name;
        arq.write(temp.name + " = " + self.children[0].address.name + " " + self.op + " " + self.children[1].address.name + "\n");

class RelOp(BinOp):
    def __init__(self, left, op, right, father):
        BinOp.__init__(self,'RelOp',left, op, right, father)
        print('Criando um nó do tipo RelOp com operador ' + str(op))
    def __evaluate__(self):
    	a = self.children[0].__evaluate__()
        b = self.children[1].__evaluate__()
        if(self.op == '<'):
        	if(float(a) < float(b)):
        		c = True
        		return c
        	else:
        		c = False
        		return c
        elif(self.op == '<='):
        	if(float(a) <= float(b)):
        		c = True
        		return c
        	else:
        		c = False
        		return c
        elif(self.op == '>'):
        	if(float(a) > float(b)):
        		c = True
        		return c
        	else:
        		c = False
        		return c
        elif(self.op == '>='):
        	if(float(a) >= float(b)):
        		c = True
        		return c
        	else:
        		c = False
        		return c
        elif(self.op == '=='):
        	if(float(a) == float(b)):
        		c = True
        		return c
        	else:
        		c = False
        		return c
        elif(self.op == '!='):
        	if(float(a) != float(b)):
        		c = True
        		return c
        	else:
        		c = False

        		return c

    def generateBranchCode(self):
        self.children[0].generateBranchCode() ;
        self.children[1].generateBranchCode() ;
        test = self.children[0].address.name + self.op + self.children[1].address.name;
        arq.write("if " +  test +  " goto " +  self.true_label.name + "\n");
        arq.write("goto " + self.false_label.name + "\n");


    def generateRValueCode(self):
        self.true_label = Label()
        self.false_label = Label()
        self.next = Label()
        self.address = Operand()
        temp = Temp()
        self.children[0].generateRValueCode()
        self.children[1].generateRValueCode()
        arq.write("if "+self.children[0].address.name + self.op + self.children[1].address.name +" goto "+ self.true_label.name+"\n");
        arq.write(temp.name+ "= 0\n"+" goto "+self.next.name+"\n")
        arq.write(self.true_label.name+":"+temp.name+"=1\n")
        arq.write(self.next.name +":")
        self.address.temporary = temp;
        self.address.name = temp.name;


class Id(AST):
    """The Var node is constructed out of ID token."""
    def __init__(self,token,lexema,father):
        AST.__init__(self,'Id',father)
        print('Criando um nó do tipo Id.')
        #self.children.append(token)
        self.token = token
        self.lexema = lexema
        #ref para entrada da tabela de símbolos

    def __repr__(self):
        #return repr(self.token)
        return self.token

    def __evaluate__(self):
        te = dicionario[self.lexema][1]
        if (te != None):
            return te
        else:
            return 0;

    def generateCode(self):
        operand = Operand();
        operand.name =  self.lexema;
        self.address = operand;

    def generateRValueCode(self):
        return self.generateCode();

    def generateBranchCode(self):
        return self.generateCode();


class Num(AST):
    def __init__(self, token, father, tipo):
        AST.__init__(self,'Num', father)
        print('Criando um nó do tipo Num.')
        #self.children.append(token)
        self.token = token
        self.value = token #em python, não precisamos nos preocupar com o tipo de value
        self.tipo = tipo

    def __repr__(self):
        #return repr(self.token)
        return self.value

    def __evaluate__(self):
        return self.value

    def __checkTypes__(self):
        return self.tipo

    def __convertTo__(self, novotipo):
        self.tipo = novotipo
        #testa se o tipo atual é float e o novo tipo é int para realizar um truncamento ou arrendondamento

    def __codegen__(self):
        return str(self.value)
    def generateCode(self):
        operand = Operand();
        operand.name = self.value;
        self.address = operand;
    def generateRValueCode(self):
        return self.generateCode();

    def generateBranchCode(self):
        return self.generateCode();


def print_tree(current_node, indent="", last='updown'):

    nb_children = lambda node: sum(nb_children(child) for child in node.children) + 1
    size_branch = {child: nb_children(child) for child in current_node.children}

    """ Creation of balanced lists for "up" branch and "down" branch. """
    up = sorted(current_node.children, key=lambda node: nb_children(node))
    down = []
    while up and sum(size_branch[node] for node in down) < sum(size_branch[node] for node in up):
        down.append(up.pop())

    """ Printing of "up" branch. """
    for child in up:
        next_last = 'up' if up.index(child) is 0 else ''
        next_indent = '{0}{1}{2}'.format(indent, ' ' if 'up' in last else '│', " " * len(current_node.__repr__()))
        print_tree(child, indent=next_indent, last=next_last)

    """ Printing of current node. """
    if last == 'up': start_shape = '┌'
    elif last == 'down': start_shape = '└'
    elif last == 'updown': start_shape = ' '
    else: start_shape = '├'

    if up: end_shape = '┤'
    elif down: end_shape = '┐'
    else: end_shape = ''

    print('{0}{1}{2}{3}'.format(indent, start_shape, current_node.__repr__(), end_shape))

    """ Printing of "down" branch. """
    for child in down:
        next_last = 'down' if down.index(child) is len(down) - 1 else ''
        next_indent = '{0}{1}{2}'.format(indent, ' ' if 'down' in last else '│', " " * len(current_node.__repr__()))
        print_tree(child, indent=next_indent, last=next_last)


def symbleTable():
	tamanho = len(tokenList)
	tipo = []
	dict2 = {}
	for i in range(0,tamanho):
		if((tokenList[i] == 'INT' and tokenList[i+1] == 'ID') or (tokenList[i] == 'FLOAT' and tokenList[i+1] == 'ID')):
			tipo = []
			tipo.append(tokenList[i])
			i = i+1
			while(tokenList[i] != 'PCOMMA'):
				if(tokenList[i] == 'ID'):
					dict2[lexemaList[i]] = (tipo, 0)
					dicionario.update(dict2)
					if(tokenList[i+1] == 'PCOMMA'):
						dict2[lexemaList[i]] = (tipo, 0)
						dicionario.update(dict2)
					if(tokenList[i+1] == 'ATTR' and tokenList[i+2] == 'ID'):
						dict2[lexemaList[i]] = (tipo, 0)
						dicionario.update(dict2)
					if((tokenList[i+1] == 'ATTR' and tokenList[i+2] == 'INTEGER_CONST') or (tokenList[i+1] == 'ATTR' or tokenList[i+2] == 'FLOAT_CONST')):
						dict2[lexemaList[i]] = (tipo, lexemaList[i+2])
						dicionario.update(dict2)
					if(tokenList[i+1] == 'COMMA'):
						dict2[lexemaList[i]] = (tipo, 0)
						dicionario.update(dict2)

				i=i+1
	print dicionario
	return dicionario


def match(token):
	if(tokenList[0] == token):
		print 'Entrada correta -  ' , token
		tokenList.pop(0)
		lexemaList.pop(0)
	else:
		print 'Erro sintatico'

def Programa():
	match('INT')
	match('MAIN')
	match('LBRACKET')
	match('RBRACKET')
	match('LBRACE')
	vetor = AST('decl_comando', None)
   	ast = Decl_Comando(vetor);
	match('RBRACE')
	return ast

def Decl_Comando(vetor):
    if (tokenList[0] == 'INT' or tokenList[0] == 'FLOAT'):
        vetor1 = Declaracao(vetor);
        return Decl_Comando(vetor1);
    elif (tokenList[0] == 'ID' or tokenList[0] == 'IF' or tokenList[0] == 'WHILE' or tokenList[0] == 'PRINT'
          or tokenList[0] == 'READ' or tokenList[0] == 'LBRACE'):
       	vetor1 = Comando(vetor);
       	return Decl_Comando(vetor1);
    else:
    	return vetor

def Declaracao(vetor):
	global id_node
	Tipo();
	if(tokenList[0] == 'ID'):
		id_node = Id(lexemaList[0],lexemaList[0],None)
		match('ID')

	return Decl2(vetor);

def Decl2(vetor):
	global id_node

	if(tokenList[0] == 'COMMA'):
		match('COMMA')
		id_node = Id(lexemaList[0],lexemaList[0],None)
		match('ID')
		return Decl2(vetor)

	elif(tokenList[0] == 'PCOMMA'):
		match('PCOMMA')
		return vetor

	elif(tokenList[0] == 'ATTR'):
		match('ATTR')
		expr_node = Expressao()
		attr_node = Attr(id_node,'=',expr_node,None)
		vetor.children.append(attr_node)
		return Decl2(vetor);

  	return vetor;


def Tipo():
	if(tokenList[0] == 'INT'):
		match('INT')
	elif(tokenList[0] == 'FLOAT'):
		match('FLOAT')


def Comando(vetor):
	if(tokenList[0] == 'LBRACE'):
		return Bloco(vetor)
	elif(tokenList[0] == 'ID'):
		return Atribuicao(vetor)
	elif(tokenList[0] == 'IF'):
		return ComandoSe(vetor)
	elif(tokenList[0] == 'WHILE'):
		return ComandoEnquanto(vetor)
	elif(tokenList[0] == 'READ'):
		return ComandoRead(vetor)
	elif(tokenList[0] == 'PRINT'):
		return ComandoPrint(vetor)

def Bloco(vetor):
	match('LBRACE')
	bloco = AST('Bloco',None)
	retorno = Decl_Comando(bloco)
	match('RBRACE')
	vetor.children.append(retorno)

	return vetor

def Atribuicao(vetor):
	id_node = Id(lexemaList[0],lexemaList[0],None)
	match('ID')
	match('ATTR')
	expr_node = Expressao()
	vetor.children.append(Attr(id_node,'=',expr_node,None));
	match('PCOMMA')
	return vetor


def ComandoRead(vetor):
	read_node = Read('READ')
	match('READ')
	id_node = Id(lexemaList[0],lexemaList[0],None)
	read_node.children.append(id_node)
	match('ID')
	match('PCOMMA')
	vetor.children.append(read_node)
	return vetor

def ComandoSe(vetor):
	if_node = If('IF')
	match('IF')
	match('LBRACKET')
	expr_node = Expressao()
	if_node.children.append(expr_node)
	match('RBRACKET')
	c_true = AST('C_TRUE',None)
	retorno = Comando(c_true)
	if_node.children.append(retorno)
	ComandoSenao(if_node)
	vetor.children.append(if_node)
	return vetor

def ComandoSenao(if_node):
	if(tokenList[0] == 'ELSE'):
		c_false = AST('C_FALSE',None)
		match('ELSE')
		retorno = Comando(c_false)
		if_node.children.append(retorno)
		return if_node
	else :
		return if_node

def ComandoEnquanto(vetor):
	while_node = While('WHILE')
	match('WHILE')
	match('LBRACKET')
	expr_node = Expressao()
	while_node.children.append(expr_node)
	match('RBRACKET')
	c_true = AST('C_TRUE',None)
	retorno = Comando(c_true)
	while_node.children.append(retorno)
	vetor.children.append(while_node)
	return vetor

# def ComandoPara(vetor):
#     #global id_node
#     for_node = For('For')
#     match('FOR')
#     match('LBRACKET')
#     id_node = Id(token)
#     match('ID')
#     match('ATTR')
#     expr_node = Expressao()
#     for_node.children.append(Attr(id_node,'=',expr_node))
#     expr_node = Expressao()
#     for_node.children.append(expr_node)
#     id_node = Id(token)
#     match('ID')
#     match('ATTR')
#     expr_node = Expressao()
#     for_node.children.append(expr_node)
#     match('RBRACKET')
#     c_true = AST('C_TRUE', None)
#     retorno = Comando(c_true)
#     for_node.children.append(retorno)
#     vetor.children.append(for_node)
#     return vetor

def ComandoPrint(vetor):
	print_node = Print('PRINT')
	match('PRINT')
	match('LBRACKET')
	expr = Expressao()
	print_node.children.append(expr)
	match('RBRACKET')
	match('PCOMMA')
	vetor.children.append(print_node)
	return vetor


def Expressao():
    expr = Conjuncao();
    return ExpressaoOpc(expr);

def ExpressaoOpc(expr):
	if(tokenList[0] == 'OR'):
		match('OR')
		expr2 = Conjuncao()
		or_node = LogicalOp(expr,'||',expr2,None)
		expr2 = ExpressaoOpc(or_node)
		return expr2
	else:
		return expr

def Conjuncao():
	expr = Igualdade()
	return ConjuncaoOpc(expr)


def ConjuncaoOpc(expr):
	if(tokenList[0] == 'AND'):
		match('AND')
		expr2= Igualdade()
		and_node = LogicalOp(expr,'&&',expr2,None)
		expr2 = ConjuncaoOpc(and_node)
		return expr2
	else :
		return expr

def Igualdade():
	expr = Relacao()
	return IgualdadeOpc(expr)

def IgualdadeOpc(expr):
	if(tokenList[0] == 'EQ'):
		OpIgual()
		expr2 = Relacao()
		igual_node = RelOp(expr,'==',expr2,None)
		return IgualdadeOpc(igual_node)

	elif(tokenList[0] == 'NE'):
		OpIgual()
		expr2 = Relacao()
		diferente_node = RelOp(expr,'!=',expr2,None)
		return IgualdadeOpc(diferente_node)

	else :
		return expr

def OpIgual():
	if(tokenList[0] == 'EQ'):
		match('EQ')
	elif(tokenList[0] == 'NE'):
		match('NE')

def Relacao():
	expr = Adicao()
	return RelacaoOpc(expr)

def RelacaoOpc(expr):
	if(tokenList[0] == 'LT'):
		OpRel()
		expr2 = Adicao()
		menor_node = RelOp(expr,'<',expr2,None)
		return RelacaoOpc(menor_node)
	elif(tokenList[0] == 'LE'):
		OpRel()
		expr2 = Adicao()
		menorigual_node = RelOp(expr,'<=',expr2,None)
		return RelacaoOpc(menorigual_node)
	elif(tokenList[0] == 'GT'):
		OpRel()
		expr2 = Adicao()
		maior_node = RelOp(expr,'>',expr2,None)
		return RelacaoOpc(maior_node)
	elif(tokenList[0] == 'GE'):
		OpRel()
		expr2 = Adicao()
		maiorigual_node = RelOp(expr,'>=',expr2,None)
		return RelacaoOpc(maiorigual_node)
	else :
		return expr



def OpRel():
	if(tokenList[0] == 'LT' ):
		match('LT')
	elif(tokenList[0] == 'LE') :
		match('LE')
	elif(tokenList[0] == 'GT'):
		match('GT')
	elif(tokenList[0] == 'GE'):
		match('GE')

def Adicao():
	expr = Termo()
	return AdicaoOpc(expr)

def AdicaoOpc(expr):
	if(tokenList[0] == 'PLUS'):
		OpAdicao()
		expr2 = Termo()
		plus_node = ArithOp(expr,'+',expr2,None)
		return AdicaoOpc(plus_node)

	elif(tokenList[0] == 'MINUS'):
		OpAdicao()
		expr2 = Termo()
		minus_node = ArithOp(expr,'-',expr2,None)
		return AdicaoOpc(minus_node)

	else:
		return expr

def OpAdicao():
	if(tokenList[0] == 'PLUS'):
		match('PLUS')
	elif(tokenList[0] == 'MINUS'):
		match('MINUS')

def Termo():
	expr = Fator()
	return TermoOpc(expr)

def TermoOpc(expr):
	if(tokenList[0] == 'MULT'):
		OpMult()
		expr2 = Fator()
		mult_node = ArithOp(expr,'*',expr2,None)
		return TermoOpc(mult_node)

	elif(tokenList[0] == 'DIV'):
		OpMult()
		expr2 = Fator()
		div_node = ArithOp(expr,'/',expr2,None)
		return TermoOpc(div_node)
	else:
		return expr

def OpMult():
	if(tokenList[0] == 'MULT'):
		match('MULT')
	elif(tokenList[0] == 'DIV'):
		match('DIV')

def Fator():
	if(tokenList[0] == 'ID'):
		id_node = Id(lexemaList[0],lexemaList[0],None)
		match('ID')
		return id_node
	elif(tokenList[0] == 'INTEGER_CONST'):
		num_node = Num(lexemaList[0],None,int_type)
		match('INTEGER_CONST')
		return num_node
	elif(tokenList[0] == 'FLOAT_CONST'):
		num_node = Num(lexemaList[0],None,float_type)
		match('FLOAT_CONST')
		return num_node
	elif(tokenList[0] == 'LBRACKET'):
		match('LBRACKET')
		expr = Expressao()
		match('RBRACKET')
		return expr





symbleTable()

while (len(tokenList)>0 and len(lexemaList)>0):

   
    root = Programa()
    print('Árvore de Sintaxe Abstrata: ')
    print root
    root.__evaluate__()
    root.generateCode()

    print "Tabela de Símbolos - pós programa"
    print dicionario
