
# coding: utf-8

# In[38]:


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
            if len(r_e[e]) == 0: m_employees[e] = ''
            match_rankings = [r_t[t].index(x) for x in m_tickets[t]]
            if e not in r_t[t]:
                continue
            elif (len(m_tickets[t]) <= len(r_t[t])):
                m_tickets[t].append(e)
                m_employees[e] = t
            elif np.max(match_rankings) > r_t[t].index(e):
                old_e = m_tickets[t][np.argmax(match_rankings)]
                m_tickets[t][np.argmax(match_rankings)] = e
                if len(r_e[old_e] > 0): m_employees[old_e] = None
                else: m_employees[e] = ''
                    
    m_score = {}
    for e in m_employees:
        if(m_employees[e] == ''):
            m_score[e] = len(r_employees[e])
        else:
            m_score[e] = r_employees[e].index(m_employees[e])
    
    return m_employees, m_tickets, m_score


# In[39]:


# Generate test data

from random import sample, shuffle

def fake_data(n_tickets, n_employees, n_preferences):
    
    if n_preferences > n_tickets: n_preferences = n_tickets

    def random_combination(iterable, r):
        pool = tuple(iterable)
        n = len(pool)
        indices = sorted(sample(range(n), r))
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

    for i, t in enumerate(r_tickets):
        r_tickets[t] = r_tickets[t][0:(i+1)*20]
        
    return r_employees, r_tickets


# In[40]:


# Conduct matching and calculate matching score
n_tickets = 8
n_employees = 200
n_preferences = 3

r_employees, r_tickets = fake_data(n_tickets, n_employees, n_preferences)
m_employees, m_tickets, m_score = gale_shapely(r_employees, r_tickets)

