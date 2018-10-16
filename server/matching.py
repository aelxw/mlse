
# coding: utf-8

# In[1]:


# Generate test data

from random import sample, shuffle

def fake_data(n_tickets, n_employees, n_preferences):
    
    if n_preferences > n_tickets: n_preferences = n_tickets

    def random_combination(iterable, r):
        pool = tuple(iterable)
        n = len(pool)
        indices = sorted(sample(range(n), r))
        shuffle(indices)
        return list(pool[i] for i in indices)

    tickets = ["t"+str(x) for x in range(1,n_tickets+1)]
    employees = ["e"+str(x) for x in range(1,n_employees+1)]

    r_employees = {}
    for e in employees:
        r_employees[e] = random_combination(tickets, n_preferences)

    r_tickets = {}
    for t in tickets:
        shuffle(employees)
        r_tickets[t] = employees
        
    return r_employees, r_tickets


# In[2]:


# Gale Shapley

import numpy as np
from copy import deepcopy

def gale_shapely(r_employees, r_tickets):
    
    r_e = deepcopy(r_employees)
    r_t = deepcopy(r_tickets)
    
    m_employees = {}
    for e in r_employees.keys():
        m_employees[e] = None
    
    m_tickets = {}
    for t in r_tickets.keys():
        m_tickets[t] = []
    
    while None in m_employees.values():
        proceed = False
        for e, t in m_employees.items():
            if (t == None) & (len(r_e[e])>0):
                proceed = True
                break
        if(proceed):
            t = r_e[e].pop(0)
            if len(r_e[e]) == 0: m_employees[e] = []
            match_rankings = [r_t[t].index(x) for x in m_tickets[t]]
            if e not in r_t[t]:
                continue
            elif (len(m_tickets[t]) <= len(r_t[t])):
                m_tickets[t].append(e)
                m_employees[e] = [t]
            elif np.max(match_rankings) > r_t[t].index(e):
                old_e = m_tickets[t][np.argmax(match_rankings)]
                m_tickets[t][np.argmax(match_rankings)] = e
                if len(r_e[old_e] > 0): m_employees[old_e] = None
                else: m_employees[e] = []
    
    return m_employees, m_tickets


# In[3]:


# Integer programming

import cvxpy as cvx
import numpy as np
from scipy import sparse
from warnings import filterwarnings
filterwarnings("ignore")

def ip(r_employees, tickets):
    
    n_employees = len(r_employees)
    n_tickets = len(tickets)
    m_employees = {}
    
    
    # Variables

    x = cvx.Variable((n_employees*n_tickets,1), integer=True)
    
    # Constraints

    # Each employee gets >= 1 ticket
    A1 = -sparse.kron(sparse.eye(n_employees), np.ones(n_tickets))
    b1 = -np.ones((A1.shape[0],1))

    # <= ticket capacity
    A2 = np.zeros((n_tickets, A1.shape[1]))
    for i, row in enumerate(A2):
        A2[i, i::n_tickets] = 1
    A2 = sparse.csr_matrix(A2)
    b2 = np.ones((A2.shape[0],1))*n_employees

    # Variables >= 0
    A3 = -sparse.eye(n_employees * n_tickets)
    b3 = np.zeros((A3.shape[0], 1))

    A = sparse.vstack((A1, A2, A3))
    b = sparse.vstack((b1, b2, b3))

    constraints = [A*x <= b]

    # Objective function

    tickets = list(r_tickets.keys())

    i_employees = []
    C = np.array([])
    for e in r_employees.keys():
        i_employees.append(e)
        temp = np.ones(len(tickets))*(len(tickets)+1)
        for i, t in enumerate(r_employees[e]):
            temp[tickets.index(t)] = i+1
        if len(C) == 0:
            C = temp
        else:
            C = np.vstack((C,temp))
    c = C.flatten().reshape(1,-1)

    obj = cvx.Minimize(c * x.flatten())

    # Solve
    
    problem = cvx.Problem(obj, constraints)
    problem.solve(solver=cvx.ECOS_BB)
    
    for i, row in enumerate(np.round(x.value.reshape(n_employees, n_tickets))):
        m_employees[i_employees[i]] = np.array(tickets)[row>0].tolist()
        
    return m_employees


# In[9]:


n_tickets = 3
n_employees = 700
n_preferences = 6
tickets = ["t"+str(x) for x in range(1,n_tickets+1)]

r_employees, r_tickets = fake_data(n_tickets, n_employees, n_preferences)


# In[10]:


m_employees_gs, m_tickets_gs = gale_shapely(r_employees, r_tickets)


# In[11]:


m_employees_ip = ip(r_employees, tickets)

