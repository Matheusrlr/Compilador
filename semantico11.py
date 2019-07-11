#!/usr/bin/env python2.7.12
#-*- coding: utf-8 -*-


listaTokensDeclaracao = []
listaDeclaracao = []
def avaliacaoRedeclaracao(token): ### a partir daqui será feita a avaliação semântica do código
    if not token in listaTokensDeclaracao:
        listaTokensDeclaracao.append(token)
    else:
        print "Erro, redeclaração da variavel ", token
        exit()

def avaliacaoDeclaracao(token):
    if not token in listaTokensDeclaracao:
        print "Erro, variável ",token," não declarada"
        exit()

def avaliacaoAttr(expressao): ### checagem de tipos
    xp = []
    for i in expressao:
        if i == ';':
            break
        else:
            xp.append(i)
    return xp
