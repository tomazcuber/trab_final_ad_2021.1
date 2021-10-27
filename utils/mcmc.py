from scipy.sparse.csgraph import floyd_warshall
from scipy.sparse import csr_matrix

import numpy as np
import random as rd
import networkx as nx
import copy

# gerar_grafo_inicial
# -------------------
# > Objetivo: Deve gerar um grafo inicial biconexo (robusto)
# > Entradas:
# - n_vertices: número de vértices que o grafo terá
# - n_arestas: número de arestas que o grafo deve ter
# > Saídas:
# - grafo biconexo em formato de matriz

def gerar_grafo_inicial(n_vertices, n_arestas):
    grafo = np.zeros((n_vertices, n_vertices))

    # Cria grafo circular
    for vertice in range(n_vertices):
        proximo = (vertice + 1) % n_vertices
        if proximo > vertice:
            grafo[proximo, vertice] = 1
        else:
            grafo[vertice, proximo] = 1
    
    arestas_restantes = n_arestas - n_vertices
    
    # Cria lista de arestas ainda não existentes
    possiveis = list()
    for i in range(n_vertices):
        for j in range(i):
            if grafo[i,j] == 0:
                possiveis.append((i,j))
    
    # Escolhe arestas aleatorias não existentes para criar
    for aresta in rd.sample(possiveis, arestas_restantes):
        grafo[aresta] = 1
    
    return grafo


# propoe_novo_grafo
# -------------------
# > Objetivo: Deve propor um novo grafo biconexo, baseado na entrada
# > Entradas:
# - grafo: o grafo biconexo a ser utilizado como base para gerar outro
# > Saídas:
# - outro grafo biconexo, com mesma quantidade de vértices e arestas

import itertools
import random as rd

def propoe_novo_grafo(grafo):
    n_vertices = grafo.shape[0]
    arestas = list()
    nao_arestas = list()
    for i in range(n_vertices):
        for j in range(i):
            if grafo[i,j] == 1:
                arestas.append((i,j))
            else:
                nao_arestas.append((i,j))
    
    possibilidades = list( itertools.product(arestas, nao_arestas) )
    rd.shuffle(possibilidades)

    for ativa, inativa in possibilidades:
        tmp = copy.deepcopy(grafo)
        tmp[ativa] = 0
        tmp[inativa] = 1

        nx_grafo = nx.Graph(tmp)
        if nx.is_biconnected(nx_grafo):
            return tmp
    
    raise Exception("Nenhum estado biconexo vizinho")


# metrica_eficiencia
# -------------------
# > Objetivo: Deve medir a eficiencia de um grafo, retornando um número que quanto maior, mais eficiente
# > Entradas:
# - grafo: o grafo biconexo a ser avaliado
# > Saídas:
# - um número avaliando a eficiência do grafo

def metrica_eficiencia(grafo):
    dist_matrix = floyd_warshall(csgraph=csr_matrix(grafo), directed=False)
    return 1/np.sum(dist_matrix)


# criador_grafo_mcmc
# -------------------
# > Objetivo: Deve utilizar MCMC para encontrar um grafo eficiente e biconexo
# > Entradas:
# - n_vertices: número de vértices do grafo
# - n_arestas: número de arestas do grafo
# - iteracoes: quantidade de iterações que o MCMC fará
# > Saídas:
# - grafo biconexo mais eficiente encontrado
# - lista com informações da métrica por iteração (para plotar gráfico)

def criador_grafo_mcmc(n_vertices, n_arestas, iteracoes, log = None):
    #assert n_vertices+1 <= n_arestas and n_arestas <= 2*n_vertices-6, \
    #    "Restrição: vertices+1 <= arestas <= 2*vertices-6"

    evolucao = []
    evolucao_melhor = []

    grafo_atual = gerar_grafo_inicial(n_vertices, n_arestas)
    melhor_grafo = grafo_atual

    for i in range(iteracoes):
        evolucao.append( [float(i), metrica_eficiencia(grafo_atual)] )
        evolucao_melhor.append( [float(i), metrica_eficiencia(melhor_grafo)] )

        grafo_proposto = propoe_novo_grafo(grafo_atual)
        melhor_grafo = grafo_proposto if metrica_eficiencia(grafo_proposto) > metrica_eficiencia(melhor_grafo) else melhor_grafo

        aceitacao = metrica_eficiencia(grafo_proposto) / metrica_eficiencia(grafo_atual)

        U = rd.uniform(0,1)

        if log != None:
            log.debug("({}) Proposto: {}|Atual: {}".format( i, metrica_eficiencia(grafo_proposto), metrica_eficiencia(grafo_atual) ))
            log.debug("({}) Aceitação: {}|U: {}".format( i, aceitacao, U ))
        
        if aceitacao > U:
            grafo_atual = grafo_proposto
            if log != None:
                log.debug("({}) Aceito!".format(i))
        else:
            if log != None:
                log.debug("({}) Reprovado!".format(i))

    return grafo_atual, melhor_grafo, evolucao, evolucao_melhor