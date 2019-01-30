
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
import cvxpy as cvx
from skopt import gp_minimize, forest_minimize, gbrt_minimize, dummy_minimize
from skopt.plots import plot_objective, plot_convergence, plot_evaluations
from scipy import sparse
from matplotlib import pyplot as plt

from warnings import filterwarnings
filterwarnings("ignore")

import sys
import traceback


# In[ ]:


def read_data(filename):
    data = pd.read_csv(filename, names=["id", "r1", "r2", "r3"])
    data.id = data.id.apply(lambda x: "e"+str(x))
    data = data.set_index("id")
    return data

def newton_k(x, k1, k2, k3):
    y = x - ((1+k1*x)*(1+k2*x)*(1+k3*x)-(1+x))/(3*(k1*k2*k3)*(x*x)+2*(k1*k2+k1*k3+k2*k3)*x+(k1+k2+k3-1))
    if np.abs(y-x) <= 0.00001:
        return y
    else:
        return newton_k(y, k1, k2, k3)
    
def U_init(model):
    priority = ["equity", "rank1", "unmatched"]
    k1, k2, k3 = [0.7, 0.65, 0.6]
    
    n, m = model.data.shape
    qi = model.qi
    temp = n - np.array([x for x in model.ticket_capacity.values()]).sum()
    u_min = temp if temp > 0 else 0
    
    U = [
        lambda x: 1-1/qi.sum()*x if qi.sum() > 0 else np.ones(x.shape),
        lambda x: 1/n*x,
        lambda x: 1-1/n*x #(x-u_min)
    ]
    k = newton_k(-2, k1, k2, k3) if (k1+k2+k3) > 1 else newton_k(2, k1, k2, k3)
    K = [k1, k2, k3, k]
    return priority, U, K
    
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

def U_eval(x_star, model):
    qi = model.qi
    U = model.U
    K = model.K
    priority = model.priority
    
    n, m = model.data.shape
    X = x_star.reshape(n,m)
    
    vals = pd.Series({
        "rank1": np.ones((n,1)).T.dot(X.dot(np.eye(1,m,0).T)).ravel()[0],
        "unmatched": np.ones((n,1)).T.dot(np.ones((n,1))-X.dot(np.ones((m,1)))).ravel()[0],
        "equity": qi.T.dot(X.dot(np.eye(1,m,2).T)+(np.ones((n,1))-X.dot(np.ones((m,1))))).ravel()[0]
    }).loc[priority].values.reshape(-1,3)
    score = U_joint(vals, U, K)[0]
    return score, vals


# In[ ]:


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
    A1 = sparse.kron(sparse.eye(n_employees), np.ones(n_t))
    b1 = np.ones((A1.shape[0],1))

    # <= ticket capacity
    rows = []
    b2 = []
    for t in tickets:
        temp = r.apply(lambda x: x.map({t:1})).fillna(0).values.reshape(1,-1)
        rows.append(temp)
        b2.append(ticket_capacity[t])
    A2 = sparse.bsr_matrix(np.vstack(rows))
    b2 = np.array(b2).reshape(-1,1)
    
    # Unvoted
    A3 = sparse.bsr_matrix(np.array(r.isnull().values.flatten(), np.float64))
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
    obj = cvx.Maximize(c*x)

    # Solve

    problem = cvx.Problem(obj, constraints)
    problem.solve(solver=cvx.ECOS_BB, max_iters=500, mi_max_iters=100000)

    if problem.status == 'optimal':
        x_star = x.value.reshape(-1,n_t).round()
        r_m = r.where(x_star == 1)
        
        ranks = x_star.argmax(axis=1) + 1
        ranks[(x_star.sum(axis=1) < 1)] = 0
        solranks = dict(zip(r_m.index, ranks))
        
        e_choices = dict(zip(r.index, r.where(r.notnull(), "").values.tolist()))
        
        m_employees = {}
        for e in r_m.index:
            match = r_m.loc[e].dropna().tolist()
            m_employees[e] = {
                "match": match[0] if len(match) > 0 else "",
                "rank": str(solranks[e]),
                "choices": e_choices[e]
            }

        return m_employees, x_star
    else:
        print(problem.status)
        return {}, None


# In[ ]:


class BO():
    
    def __init__(self, data, ticket_capacity, prev_rankings):
        
        self.bestscore = 0
        self.bestc = np.array([])
        self.sol = {}
        self.x_star = {}
        self.solsummary = None
        self.history = []
        
        missing = 3-data.shape[1]
        while missing > 0:
            data["r"+str(3-missing+1)] = None
            missing -= 1
        self.data = data.iloc[:, 0:3]
        
        self.ticket_capacity = ticket_capacity
        qi = prev_rankings.iloc[:, -1].values.flatten()
        self.qi = np.array(((qi == 0) | (qi == 3)), dtype=np.float64)
        
        self.priority, self.U, self.K = U_init(self)

        n, m = data.shape
        attrs = {
            "rank1":np.kron(np.ones(n), np.array([1,0,0])),
            "equity":np.kron(self.qi, np.array([1,1,0])),
            "unmatched":np.kron(np.ones(n), np.array([1,1,1]))
        }
        self.c1 = attrs[self.priority[0]]
        self.c2 = attrs[self.priority[1]]
        self.c3 = attrs[self.priority[2]]
        
        self.iter = 0

    def run(self, w):

        data = self.data
        ticket_capacity = self.ticket_capacity
        priority = self.priority
        
        epsilon = np.random.uniform(0, 0.001, size=(data.shape)).flatten()
        c = w[0]*self.c1 + w[1]*self.c2 + w[2]*self.c3 + epsilon
        
        try:
            m_employees, x_star = ip(data, ticket_capacity, c)
            score, vals = U_eval(x_star, self)
            
            self.iter = self.iter + 1
            print("Iteration {}".format(self.iter))
            
            if score >= self.bestscore:
                print(score, vals)
                self.bestscore = score
                self.bestc = c
                self.sol = m_employees
                self.x_star = x_star
                
                summary = pd.DataFrame(np.hstack((vals.flatten(), score)).reshape(1,-1),
                                       columns=priority + ["utility"])
                self.history.append(summary)
                self.solsummary = summary
            return -score
        
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback)
            pass

    def optimize(self):
        
        dimensions = [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)]
        
        def early_stop(res):
            return (res.func_vals == res.fun).sum() >= 10
        
        try:
            self.gp_res = gp_minimize(self.run, dimensions, n_points=50000, callback=early_stop)
            
        except:
            pass
    
    def show_results(self):
        if self.gp_res: 
            plot_convergence(self.gp_res)
            plot_objective(self.gp_res)
            plot_evaluations(self.gp_res)
            plt.show()
        


# In[ ]:


#data = read_data("data1.csv")
#prev_rankings = pd.DataFrame(np.random.randint(0, 4, data.shape), index=data.index)
#tickets = sorted(data.unstack().dropna().unique().tolist())
#ticket_capacity = {}
#for t in tickets:
#    ticket_capacity[t] = 180


# In[ ]:


#bo = BO(d, ticket_capacity, prev_rankings)
#bo.optimize()

