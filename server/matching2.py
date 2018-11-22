
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np
import cvxpy as cvx
from functools import partial
from random import sample, shuffle
from copy import deepcopy
from warnings import filterwarnings
from itertools import product, combinations
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from matplotlib import pyplot as plt

filterwarnings("ignore")
pd.options.display.max_rows = None


# In[89]:


# Make fake data

#n_tickets = 6
#tickets = ["t"+str(x) for x in range(1,n_tickets+1)]
#ticket_capacity = 3
#n_employees = 20
#n_preferences = 3

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


def f(x, n=3, a=0.1, s=1):
    undefined = (x>n) | (x<1)
    if s == 0:
        v = ((1-a)/(1-n))*x + ((a-n)/(1-n))
    else:
        v = (np.exp(s*(x-1))*(a-1)+np.exp(s*(n-1))-a)/(np.exp(s*(n-1))-1)
    v[undefined] = 0
    return 1-v

def wagg(arr, s=1):
    m = arr.shape[1]
    x = np.linspace(1, m, m)
    s = s if s >= 0 else 0
    w = np.exp(s*(x-m))
    w = w/w.sum()
    return arr.dot(w)


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
    df = pd.DataFrame.from_dict(e_rank, orient="index")
    return df
    
def rank_frequencies(rr):
    ret = []
    for x in [1, 2, 3, 0]:
        ret.append((rr.values==x).sum())
    return ret

def process_data(filename):
    data = pd.read_csv(filename, names=["id", "r1", "r2", "r3"])
    data.id = data.id.apply(lambda x: "e"+str(x))
    data = data.set_index("id")
    return data

def df_to_dict(df):
    r_dict = {}
    for i, e in enumerate(df.index):
        l = list(df.where(df.notnull(), None).values[i])
        l = [x for x in l if x is not None]
        r_dict[e] = l
    return r_dict


# In[159]:


prev_window = 3

r = data
w = prev_rankings.shape[1] if prev_rankings.shape[1] <= prev_window else prev_window
temp = prev_rankings.iloc[:, prev_rankings.columns[-w:]]
s_i = wagg(f(temp.loc[r.index].values), s=1)
s_i = np.kron(s_i, np.array([1,-1,-1]))
s_i = s_i*(0.1/np.abs(s_i).max())


# In[112]:


c = np.kron(np.ones(r.shape[0]), model) + np.random.normal(0.1, 0.005, size=r.shape).flatten()


# In[170]:


# Integer programming

def ip(r_employees, ticket_capacity, model, prev_rankings=None, prev_window=3):
    
    if type(r_employees) == pd.DataFrame:
        r = r_employees
    else:
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

    constraints = [
        A1*x <= b1,
        A2*x <= b2,
        A3*x <= b3,
        x >= 0
    ]

    # Objective function
    
    c = np.kron(np.ones(r.shape[0]), model) + np.random.normal(0.1, 0.005, size=r.shape).flatten()
    
    if prev_rankings is not None:
        w = prev_rankings.shape[1] if prev_rankings.shape[1] <= prev_window else prev_window
        temp = prev_rankings.iloc[:, prev_rankings.columns[-w:]]
        s_i = wagg(f(temp.loc[r.index].values), s=1)
        s_i = np.kron(s_i, np.array([1,0,-1]))
        s_i = s_i*(0.1/np.abs(s_i).max())
        c = c + s_i
    
    c[A3 > 0] = 0
    obj = cvx.Maximize(c * x)

    # Solve

    problem = cvx.Problem(obj, constraints)
    problem.solve(solver=cvx.ECOS_BB, max_iters=500, mi_max_iters=10000)

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


# In[162]:


def simulate(data, ticket_capacity, iters=11, prev_rankings=None):
    
    data_dict = df_to_dict(data)
    
    l = []
    w2 = np.linspace(0, 0.8, iters)
    w3 = np.linspace(0, 0.8, iters)
    for a in w2:
        for b in w3:
            if a>=b:
                m_employees = ip(data, ticket_capacity, np.array([1,a,b]), prev_rankings=prev_rankings)
                rr = result_rank(m_employees, data_dict)
                rf = rank_frequencies(rr)
                temp = []
                temp.append(a)
                temp.append(b)
                temp.extend(rf)
                l.append(temp)

    df = pd.DataFrame(l, columns=["w2", "w3", "r1", "r2", "r3", "unmatched"])
    return df

def U_linear(x, minimize=False):
    if minimize:
        B = x.min(axis=0)
        A = x.max(axis=0)
    else:
        B = x.max(axis=0)
        A = x.min(axis=0)
    return lambda y: ((1/(B-A))*y-(A/(B-A)))

def newton_k(x, k1, k2, k3):
    y = x - ((1+k1*x)*(1+k2*x)*(1+k3*x)-(1+x))/(3*(k1*k2*k3)*(x*x)+2*(k1*k2+k1*k3+k2*k3)*x+(k1+k2+k3-1))
    if np.abs(y-x) <= 0.00001:
        return y
    else:
        return newton_k(y, k1, k2, k3)

def U_joint(X, K, k, U):
    u1 = U[0]
    u2 = U[1]
    u3 = U[2]
    k1 = K[0]
    k2 = K[1]
    k3 = K[2]
    x1 = X[:,0]
    x2 = X[:,1]
    x3 = X[:,2]
    
    return k1*u1(x1) + k2*u2(x2) + k3*u3(x3) + k*k1*k2*u1(x1)*u2(x2) + k*k1*k3*u1(x1)*u3(x3) + k*k2*k3*u2(x2)*u3(x3) + (k*k)*k1*k2*k3*u1(x1)*u2(x2)*u3(x3)


# In[153]:


data = process_data("data1.csv")
ticket_capacity = 22


# In[154]:


prev_rankings = pd.DataFrame(np.random.randint(1, 4, data.shape), index=data.index)


# In[155]:


df_sim = simulate(data, ticket_capacity, 15, prev_rankings=None)


# In[167]:


priority = ["r1", "unmatched", "r3"]
minimize = {"r1":False, "unmatched":True, "r3":True}

U = [U_linear(df_sim.loc[:, col], minimize[col]) for col in priority]

k1 = 0.5
alpha1 = 0.5
k2 = k1*alpha1
alpha2 = 0.5
k3 = k2*alpha2
k = newton_k(-2, k1, k2, k3) if (k1+k2+k3) > 1 else newton_k(2, k1, k2, k3)

X = df_sim.loc[:, priority].values
K = [k1, k2, k3]

df = df_sim.assign(util=U_joint(X, K, k, U)).sort_values("util", ascending=False)


# In[168]:


model = np.hstack((1, df.loc[df.util.argmax(), ["w2", "w3"]].values))
m_employees = ip(data, ticket_capacity, model, prev_rankings=None)
rr = result_rank(m_employees, df_to_dict(data))


# In[169]:


pd.concat((prev_rankings, rr), axis=1)

