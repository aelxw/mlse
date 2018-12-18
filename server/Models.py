
# coding: utf-8

# In[28]:


import pandas as pd
pd.options.display.max_rows = None
import numpy as np
import cvxpy as cvx
from functools import partial
from matplotlib import pyplot as plt
from skopt import gp_minimize


# In[2]:


def read_data(filename):
    data = pd.read_csv(filename, names=["id", "r1", "r2", "r3"])
    data.id = data.id.apply(lambda x: "e"+str(x))
    data = data.set_index("id")
    return data

def U_linear(limits):
    B = limits["best"]
    A = limits["worst"]
    return lambda y: ((1/(B-A))*y-(A/(B-A)))

def newton_k(x, k1, k2, k3):
    y = x - ((1+k1*x)*(1+k2*x)*(1+k3*x)-(1+x))/(3*(k1*k2*k3)*(x*x)+2*(k1*k2+k1*k3+k2*k3)*x+(k1+k2+k3-1))
    if np.abs(y-x) <= 0.00001:
        return y
    else:
        return newton_k(y, k1, k2, k3)

def U_joint(X, U, K):
    u1 = U[0]
    u2 = U[1]
    u3 = U[2]
    k1 = K[0]
    k2 = K[1]
    k3 = K[2]
    k = K[3]
    x1 = X[:,0]
    x2 = X[:,1]
    x3 = X[:,2]
    
    return k1*u1(x1) + k2*u2(x2) + k3*u3(x3) + k*k1*k2*u1(x1)*u2(x2) + k*k1*k3*u1(x1)*u3(x3) + k*k2*k3*u2(x2)*u3(x3) + (k*k)*k1*k2*k3*u1(x1)*u2(x2)*u3(x3)

def U_init(self):
    data = self.data
    utilities = {
        "ec":{"best":0, "worst":len(data)},
        "r1":{"best":len(data), "worst":0},
        "unmatched":{"best":0, "worst":len(data)}
    }
    
    priority = ["ec", "r1", "unmatched"]
    k1 = 0.7
    k2 = 0.6
    k3 = 0.55
    
    k = newton_k(-2, k1, k2, k3) if (k1+k2+k3) > 1 else newton_k(2, k1, k2, k3)

    U = [U_linear(utilities[x]) for x in priority]
    K = [k1, k2, k3, k]
    return U, K, priority

def U_eval(x_star, model):
    ei = model.ei
    U = model.U
    K = model.K
    priority = model.priority
    
    n, m = model.data.shape
    X = x_star.reshape(n,m)
    
    r1 = np.ones((n,1)).T.dot(X.dot(np.eye(1,m,0).T)).ravel()[0]
    unmatched = np.ones((n,1)).T.dot(np.ones((n,1))-X.dot(np.ones((m,1)))).ravel()[0]
    ec = ei.T.dot(X.dot(np.eye(1,m,2).T)+(np.ones((n,1))-X.dot(np.ones((m,1))))).ravel()[0]
    
    vals = pd.Series({"r1":r1, "unmatched":unmatched, "ec":ec}).loc[priority].values.reshape(-1,3)
    score = U_joint(vals, U, K)[0]
    return score, vals


# In[3]:


# Integer programming

def ip(r_employees, ticket_capacity, c):
    
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
    b2 = []
    for t in tickets:
        temp = r.apply(lambda x: x.map({t:1})).fillna(0).values.reshape(1,-1)
        rows.append(temp)
        b2.append(ticket_capacity[t])
    A2 = np.vstack(rows)
    b2 = np.array(b2).reshape(-1,1)
    
    # Unvoted
    A3 = np.array(r.isnull().values.flatten(), np.float64)
    b3 = 0
    
    A = np.vstack((A1, A2, A3))
    b = np.vstack((b1, b2, b3))

    constraints = [
        A1*x <= b1,
        A2*x <= b2,
        A3*x <= b3,
        x >= 0
    ]

    # Objective function
    c[A3 > 0] = 0
    obj = cvx.Maximize(c*x)

    # Solve

    problem = cvx.Problem(obj, constraints)
    problem.solve(solver=cvx.ECOS_BB, max_iters=500, mi_max_iters=10000)

    if problem.status == 'optimal':
        x_star = x.value.reshape(-1,n_t).round()
        r_m = r.where(x_star == 1)
        m_employees = {}
        for e in r_m.index:
            m_employees[e] = r_m.loc[e].dropna().tolist()

        return m_employees, x_star
    else:
        print(problem.status)
        return {}, None


# In[4]:


class BO():
    
    def __init__(self, data, ticket_capacity, prev_rankings):
        
        self.bestscore = 0
        self.bestc = np.array([])
        self.sol = {}
        self.solsummary = None
        
        self.data = data
        self.ticket_capacity = ticket_capacity
        self.prev_rankings = prev_rankings
        self.U, self.K, self.priority = U_init(self)
        
        ei = prev_rankings.iloc[:, -1].values.flatten()
        self.ei = np.array(((ei == 0) | (ei == 3)), dtype=np.float64)
        
        n, m = data.shape
        attrs = {
            "r1":np.kron(np.ones(n), np.array([1,0,0])),
            "ec":np.kron(self.ei, np.array([1,1,0])),
            "unmatched":np.kron(np.ones(n), np.array([1,1,1]))
        }
        self.c1 = attrs[self.priority[0]]
        self.c2 = attrs[self.priority[1]]
        self.c3 = attrs[self.priority[2]]
        
    def run(self, w):
            
        epsilon = np.random.normal(0, 0.001, size=(self.data.shape)).flatten()
        c = w[0]*self.c1 + w[1]*self.c2 + w[2]*self.c3 + epsilon

        m_employees, x_star = ip(self.data, self.ticket_capacity, c)

        score, vals = U_eval(x_star, self)

        if score > self.bestscore:
            print(score, vals)
            self.bestscore = score
            self.bestc = c
            self.sol = m_employees
            self.solsummary = pd.DataFrame(np.hstack((vals.flatten(), score)).reshape(1,-1), columns=self.priority + ["score"])
        
        return -score
    
    def optimize(self):
        dimensions = [(0.01,0.99), (0.01,0.99), (0.01,0.99)]
        gp_minimize(self.run, dimensions, n_calls=50, noise=1e-10, acq_func="EI")


# In[20]:


class GRID():
    
    def __init__(self, data, ticket_capacity, prev_rankings):
        
        self.bestscore = 0
        self.bestc = np.array([])
        self.sol = {}
        self.solsummary = None
        
        self.data = data
        self.ticket_capacity = ticket_capacity
        self.prev_rankings = prev_rankings
        self.U, self.K, self.priority = U_init(self)
        
        ei = prev_rankings.iloc[:, -1].values.flatten()
        self.ei = np.array(((ei == 0) | (ei == 3)), dtype=np.float64)
        
    def run(self, loc):
        
        scale = [0.001, 0.005, 0.005]
        c = np.abs(np.random.normal(loc=loc, scale=scale, size=self.data.shape)).flatten()
        m_employees, x_star = ip(self.data, self.ticket_capacity, c)
        
        score, vals = U_eval(x_star, self)
        
        if score > self.bestscore:
            print(score, vals)
            self.bestscore = score
            self.bestc = c
            self.sol = m_employees
            self.solsummary = pd.DataFrame(np.hstack((vals.flatten(), score)).reshape(1,-1), columns=self.priority + ["score"])
    
    def optimize(self):
        for a in np.linspace(0, 0.8, 15):
            for b in np.linspace(0, 0.8, 15):
                if a > b:
                    loc = [1,a,b]
                    for trail in range(0, 5):
                        self.run(loc)


# In[24]:


#data = read_data("data1.csv")
#prev_rankings = pd.DataFrame(np.random.randint(0, 4, data.shape), index=data.index)
#tickets = sorted(data.unstack().dropna().unique().tolist())
#ticket_capacity = {}
#for t in tickets:
#    ticket_capacity[t] = 22


# In[25]:


#bo = BO(data, ticket_capacity, prev_rankings)
#bo.optimize()


# In[26]:


#grid = GRID(data, ticket_capacity, prev_rankings)
#grid.optimize()

