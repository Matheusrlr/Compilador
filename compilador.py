#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
lexema = []
token = []


arquivo= open ("teste.txt", 'r')
lista = ['>','<','!','=','|','&']
dic = {}
dic ['('] = 'LBRACKET'
dic [')'] = 'RBRACKET'
dic ['main'] = 'MAIN'
dic ['int'] = 'INT'
dic ['float'] = 'FLOAT'
dic ['if'] = 'IF'
dic ['else'] = 'ELSE'
dic ['while'] = 'WHILE'
dic ['for'] = 'FOR'
dic ['read'] = 'READ'
dic ['print'] = 'PRINT'
dic ['{'] = 'LBRACE'
dic ['}'] = 'RBRACE'
dic [','] = 'COMMA'
dic [';'] = 'PCOMMA'
dic ['='] = 'ATTR'
dic ['<'] = 'LT'
dic ['<='] = 'LE'
dic ['>'] = 'GT'
dic ['>='] = 'GE'
dic ['=='] = 'EQ'
dic ['!='] = 'NE'
dic ['||'] = 'OR'
dic ['&&'] = 'AND'
dic ['+'] = 'PLUS'
dic ['/'] = 'DIV'
dic ['-'] = 'MINUS'
dic ['*'] = 'MULT'
separadores = ["(", ")", ",",";", "{", "}", "!", " ","=","<",">","=","|","&","+","-","*","/",",","\n"]

for linha,i in enumerate(arquivo.readlines()):
    #j= i.split(" ")
    flag = 0
    flag_lendo_const=0
    flag_especial = 0
    palavra = ""
    const_int= ""
    const_float = ""
    flagzz=0
    last=""
    for k in i:

        if flag_especial is 1:

            if(k in lista):
                especial+=k

                try:
                    #print "Esp",especial

                    token.append (dic[especial])
                    lexema.append (especial)

                    continue
                except Exception as e:
                    print "Token invalido"
                flag_especial=1
                especial=""
            else:
                flag_especial=1

        if flag_lendo_const is 1:

            if re.search("[0-9.]",k):

                const_int+= k



            elif re.match("[0-9]*(. | [0-9])([0-9])*", const_int):

                if flagzz == 0:

                    lexema.append (const_int)
                    flagzz = 1

# mudar leitura float
            elif(k in separadores):
                if flagzz !=1:
                    if re.search('[0-9]([0-9])*.[0-9]([0-9])*',const_int):
                        #gambiarra float
                        token.append('FLOAT_CONST')
                        lexema.append(const_int)


                    else :

                        lexema.append (const_int)
                        token.append('INTEGER_CONST')
                    #token.append (const_int)

                    #Aqui imprime float


                flagzz=0
                const_int=""
                if k is not " ":

                     token.append (dic[k])
                     lexema.append (k)

                flag_lendo_const= 0

        else:
            #print k

            if all (k != y for y in separadores) or (k=="."):


                if re.search ('[A-Za-z]([A-Za-z])*',k):
                    palavra+=k

                #verifica ID
                if re.search('[A-Za-z]([A-Za-z]|[0-9]|_)*', k ):

                    flag = 1

                     #verifica FLOAT_CONST

                if re.search('[0-9]([0-9])*.[0-9]([0-9])*',k):
                    token.append('FLOAT_CONST')
                    lexema.append(k)

                    flag = 1

                         #verifica INTEGER_CONST

                elif re.search('[0-9.]([0-9.])*',k):
                        #print("INTE",k)
                        #token.append('INTEGER_CONST3')
                        #lexema.append(k)
                        #Não utilizar esse lexema
                        #print "INTEGER_CONST",k
                        #print "valido const",k,linha+1
                        flag = 1
                        flag_lendo_const = 1
                        const_int+= k

                        #continue

                 # verifica os tokens

                if flag is 0:
                    lexema.append(k)
                    #print "invalido",k,linha+1
                #print("entrouu",palavra)
                final=""

                try:
                    final=dic[palavra]
                    if(last!=final):


                        lexema.append(palavra)
                        token.append(final)
                    last=final
                except Exception as e:
                    pass

            else:



                if k in lista:
                    flag_especial=1
                    especial+=k
                else:
                    especial= ""
                    flag_especial=0
                if palavra in dic :
                    # print 'lexema33',palavra,linha+1
                    # lexema.append (palavra)
                    #
                    #
                    # print 'token',dic[palavra],linha+1
                    # token.append ('ID')

                    flag = 1
                    palavra = ""
                elif re.search('[A-Za-z]([A-Za-z]|[0-9]|_)*', palavra ):
                    token.append('ID')

                    lexema.append (palavra)

                    palavra = ""


                    flag = 1
            if k in dic:

                teste = i.index(k)
                aux = ""
                aux = k+i[teste+1] ##especial
                try:
                    if not  (aux in dic and i[teste+1] in dic) :



                        lexema.append (k)


                        token.append (dic[k])
                        #token.append (k)
                        flag = 1

                except: #aqui é caractere especial

                    #imprime.append (k)
                    token.append (dic[k])
                    flag = 1
                    continue



arquivo.close()
