
# coding: utf-8

# In[245]:


import pandas as pd
import numpy as np
import cvxpy as cvx
from functools import partial
from random import sample, shuffle
from copy import deepcopy
from warnings import filterwarnings

filterwarnings("ignore")
pd.options.display.max_rows = None


# In[239]:


#r_employees = {
#    "e1":["A", "B", "C"],
#    "e2":["B", "D"],
#    "e3":["B", "C"],
#    "e4":["A"],
#    "e5":["A", "C", "D"]
#}
#ticket_capacity = 2
#prev_rank = {
#    "e1":3,
#    "e2":1,
#    "e3":2,
#    "e4":3,
#    "e5":0
#}
#res = pd.DataFrame.from_dict(prev_rank, orient="index")



# Make fake data

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

# Generate ticket preferences for Gale Shapley

def ticket_prefs(r_employees, tickets, score=None):
    r = pd.DataFrame.from_dict(r_employees, orient="index")
    t_prefs = {}
    for t in tickets:
        r_t = []
        for col in r.columns:
            temp = r.loc[r.loc[:, col] == t].index.tolist()
            if(score is None):
                shuffle(temp)
            else:
                priority = score.mean(axis=1).sort_values(ascending=True).index.tolist()
                temp = [x for x in priority if x in temp]
            r_t.extend(temp)
        t_prefs[t] = r_t
    return t_prefs

# Gale Shapley

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
    
    return m_employees



# Get ranking of matches
def result_rank(real, ideal):
    e_rank = {}
    for e in real:
        m = real[e]
        if len(m) > 0:
            t = m[0]
            r = ideal[e].index(t)+1
        else:
            r = 0
        e_rank[e] = r
    return pd.DataFrame.from_dict(e_rank, orient="index")


# In[376]:


# Integer programming

def f(x, n=3, a=0.1, s=1):
    if x < 1 or x > n:
        v = 0
    elif s == 0:
        v = ((1-a)/(1-n))*x + ((a-n)/(1-n))
    else:
        v = (np.exp(s*(x-1))*(a-1)+np.exp(s*(n-1))-a)/(np.exp(s*(n-1))-1)
    return 1-v

def wagg(df, s=1):
    m = df.shape[1]
    x = np.linspace(1, m, m)
    s = s if s >= 0 else 0
    w = np.exp(s*(x-m))
    w = w/w.sum()
    return df.values.dot(w)

def ip(r_employees, ticket_capacity, prev_rankings=None, prev_window=3):
    
    r = pd.DataFrame.from_dict(r_employees, orient="index")
    tickets = sorted(r.unstack().dropna().unique().tolist())

    n_employees = len(r_employees)
    n_t = r.shape[1]
    
    if ticket_capacity is None:
        ticket_capacity = n_employees

    # Variables

    x = cvx.Variable((r.size,1), boolean=True)

    # Constraints

    # Each employee gets <= 1 ticket
    A1 = np.kron(np.eye(n_employees), np.ones(n_t))
    b1 = np.ones((A1.shape[0],1))

    # <= ticket capacity
    rows = []
    for t in tickets:
        temp = r.apply(lambda x: x.map({t:1})).fillna(0).values.reshape(1,-1)
        rows.append(temp)
    A2 = np.vstack(rows)
    b2 = np.ones((A2.shape[0],1))*ticket_capacity
    
    # Unvoted
    A3 = np.array(r.isnull().values.flatten(), np.float64)
    b3 = 0

    A = np.vstack((A1, A2, A3))
    b = np.vstack((b1, b2, b3))

    constraints = [A*x <= b, x >= 0]

    # Objective function
    
    c = np.kron(np.ones((1,r.shape[0])).flatten(), 1/np.array([1, 2, 3]))
    
    if prev_rankings is not None:
        w = prev_rankings.shape[1] if prev_rankings.shape[1] <= prev_window else prev_window
        temp = prev_rankings.iloc[:, prev_rankings.columns[-w:]]
        s_i = wagg(temp.loc[r.index].applymap(f), s=2)
        s_i = np.kron(s_i, np.array([1,-1,-1]))
        c = c + s_i
    
    c[A3 > 0] = 0
    obj = cvx.Maximize(c * x)

    # Solve

    problem = cvx.Problem(obj, constraints)
    problem.solve(solver=cvx.ECOS_BB, max_iters=100, mi_max_iters=5000)

    if problem.status == 'optimal':
        x_star = x.value.reshape(-1,n_t)
        r_m = r.where(x_star.round() == 1)
        m_employees = {}
        for e in r_m.index:
            m_employees[e] = r_m.loc[e].dropna().tolist()

        return m_employees
    else:
        print(problem.status)
        return {}


# In[381]:


n_tickets = 5
tickets = ["t"+str(x) for x in range(1,n_tickets+1)]
ticket_capacity = 2

n_employees = 10
n_preferences = 3

r_employees = employee_prefs(n_employees, n_preferences, tickets)


# In[382]:


r_tickets = ticket_prefs(r_employees, tickets, None)
m_employees_gs = gale_shapely(r_employees, r_tickets, ticket_capacity)


# In[383]:


res = result_rank(m_employees_gs, r_employees)
for i in range(0, 3):
    m_employees = ip(r_employees, ticket_capacity, res)
    res = pd.concat((res, result_rank(m_employees, r_employees)), axis=1, ignore_index=True)

