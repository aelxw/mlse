
# coding: utf-8

# In[210]:


# Generate test data

from random import sample, shuffle

def employee_prefs(n_employees, n_preferences, tickets):

    def random_combination(iterable, r):
        pool = tuple(iterable)
        n = len(pool)
        indices = sorted(sample(range(n), r))
        shuffle(indices)
        return list(pool[i] for i in indices)

    employees = ["e"+str(x) for x in range(1,n_employees+1)]

    r_employees = {}
    for e in employees:
        r_employees[e] = random_combination(tickets, n_preferences)
    
    return r_employees


# In[211]:


# Generate ticket preferences

import pandas as pd
from random import shuffle

def ticket_prefs(r_employees, tickets):
    r = pd.DataFrame.from_dict(r_employees, orient="index")
    t_prefs = {}
    for t in tickets:
        r_t = []
        for col in r.columns:
            temp = r.loc[r.loc[:, col] == t].index.tolist()
            shuffle(temp)
            r_t.extend(temp)
        t_prefs[t] = r_t
    return t_prefs
    
r_tickets = ticket_prefs(r_employees, tickets)


# In[212]:


# Gale Shapley

import numpy as np
from copy import deepcopy
from random import shuffle

def gale_shapely(r_employees, r_tickets, ticket_capacity):
    
    r_e = deepcopy(r_employees)
    r_t = deepcopy(r_tickets)
    
    m_employees = {}
    for e in r_employees.keys():
        m_employees[e] = []
    
    m_tickets = {}
    for t in r_tickets.keys():
        m_tickets[t] = []
        
    def unproposed(r_e, m_employees):
        for e in r_e:
            if (len(m_employees[e]) == 0) & (len(r_e[e]) > 0):
                return e
        return None
    
    while True:
        e = unproposed(r_e, m_employees)
        if e is None:
            break
        t = r_e[e].pop(0)
        match_rankings = [r_t[t].index(x) for x in m_tickets[t]]
        if (len(m_tickets[t]) < ticket_capacity):
            m_tickets[t].append(e)
            m_employees[e] = [t]
        elif np.max(match_rankings) > r_t[t].index(e):
            old_e = m_tickets[t][np.argmax(match_rankings)]
            m_tickets[t][np.argmax(match_rankings)] = e
            m_employees[e] = [t]
            m_employees[old_e] = []
    
    return m_employees, m_tickets


# In[213]:


n_tickets = 8
tickets = ["t"+str(x) for x in range(1,n_tickets+1)]
ticket_capacity = 17

n_employees = 136
n_preferences = 3

r_employees = employee_prefs(n_employees, n_preferences, tickets)


# In[214]:


r_tickets = ticket_prefs(r_employees, tickets)
m_employees_gs, m_tickets_gs = gale_shapely(r_employees, r_tickets, ticket_capacity)


# In[221]:


# See how many employees were matched with given game
for t in m_tickets_gs:
    print(t + ": " + str(len(m_tickets_gs[t])))

# Check to see if any employees got matched with tickets they didn't want
for e in m_employees_gs:
    for t in m_employees_gs[e]:
        if t not in r_employees[e]: print(e)


# In[3]:


# Integer programming

import cvxpy as cvx
import pandas as pd
import numpy as np
from warnings import filterwarnings
filterwarnings("ignore")

def ip(r_employees, ticket_capacity=None, verbose=False):
    
    r = pd.DataFrame(r_employees).T
    r = r.assign(x="x")
    r.columns = range(1, r.shape[1]+1)
    tickets = sorted(r.unstack().unique().tolist())

    n_employees = len(r_employees)
    n_t = r.shape[1]
    
    if ticket_capacity is None:
        ticket_capacity = n_employees

    # Variables

    x = cvx.Variable((r.size,1), boolean=True)

    # Constraints

    # Each employee gets >= 1 ticket
    A1 = -np.kron(np.eye(n_employees), np.ones(n_t))
    b1 = -np.ones((A1.shape[0],1))

    # <= ticket capacity
    rows = []
    for t in tickets[:-1]:
        temp = r.apply(lambda x: x.map({t:1})).fillna(0).values.reshape(1,-1)
        rows.append(temp)
    A2 = np.vstack(rows)
    b2 = np.ones((A2.shape[0],1))*ticket_capacity

    # Variables >= 0
    A3 = -np.eye(n_employees * n_t)
    b3 = np.zeros((A3.shape[0], 1))

    A = np.vstack((A1, A2, A3))
    b = np.vstack((b1, b2, b3))

    constraints = [A*x <= b]

    # Objective function
    
    c = np.tile(np.array(range(1, r.shape[1]+1)), r.shape[0])
    obj = cvx.Minimize(c * x)

    # Solve

    problem = cvx.Problem(obj, constraints)
    problem.solve(solver=cvx.ECOS_BB, max_iters=100, mi_max_iters=5000, verbose=verbose)

    if problem.status == 'optimal':
        x_star = x.value.reshape(-1,n_t)
        r_m = r.where(x_star.round() == 1)
        m_employees = {}
        for e in r_m.index:
            m_employees[e] = r_m.loc[e].dropna().tolist()

        return m_employees, r_m, problem
    else:
        print(problem.status)
        return {}, None, problem


# In[ ]:


m_employees_ip, r_m, p = ip(r_employees, ticket_capacity, True)


# In[ ]:


for e in m_employees_ip:
    if m_employees_ip[e][0] != r_employees[e][0]:
        print(e)

