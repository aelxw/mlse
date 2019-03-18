#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Import the neccessary libraries

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

#%config Completer.use_jedi = False


# In[2]:


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
    
    # Unvoted (employees shouldn't get what they didn't vote for)
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
    
    try:
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
    
    except:
        pass


# In[3]:


# Class that does the Bayesian Optimization (BO) iterations
class BO():
    
    def __init__(self, data, ticket_capacity, prev_rankings=None):
        
        self.bestscore = 0
        self.bestc = np.array([])

        self.sol = {}
        self.x_star = {}
        self.solsummary = None
        self.history = []
        
        self.prev_rankings = prev_rankings
        
        # In case data is passed without 3 columns (1 column for each rank)
        missing = 3-data.shape[1]
        while missing > 0:
            data["r"+str(3-missing+1)] = None
            missing -= 1
        self.data = data.iloc[:, 0:3]
        
        if len(data.index) > len(data.index.drop_duplicates()):
            temp = pd.DataFrame(data.index, columns=["id"]).assign(n=1).groupby("id").sum().reset_index()
            dupes = ", ".join(temp.loc[temp.n > 1, ["id"]].values.flatten().tolist())
            raise Exception('Duplicate employee emails: {}'.format(dupes))
        
        self.ticket_capacity = ticket_capacity
        
        # qi represents the employees that got bad results in the previous round
        if prev_rankings is None:
            qi = np.ones(len(data))
            self.qi = qi
        else:
            qi = self.data.join(self.prev_rankings, how="left").iloc[:, -1].fillna(1).values.flatten()
            self.qi = np.array(((qi == 0) | (qi == 3)), dtype=np.float64)
        
        # Uses the default K values specified in the function
        self.set_utility()

        # c1, c2, and c3 are components used to make the objective function in the IP
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

    def set_utility(self, equity=0.7, rank1=0.5, unmatched=0.6):
        
        # Model 1: [0.7, 0.5, 0.6]
        # Model 2: [0.6, 0.5, 0.7]
        # Model 3: [0.4, 0.5, 0.2]
        # Model 4: [0.2, 0.5, 0.4]
        
        # Used newton's method to solve for k
        def newton_k(x, k1, k2, k3):
            y = x - ((1+k1*x)*(1+k2*x)*(1+k3*x)-(1+x))/(3*(k1*k2*k3)*(x*x)+2*(k1*k2+k1*k3+k2*k3)*x+(k1+k2+k3-1))
            return y if np.abs(y-x) <= 0.00001 else newton_k(y, k1, k2, k3)
        
        priority = ["equity", "rank1", "unmatched"]
        k1, k2, k3 = [equity, rank1, unmatched]

        n, m = self.data.shape
        qi = self.qi

        # Individual utility functions for each attribute
        # They should correspond to the same order of the priority list 
        U = [
            lambda x: 1-1/qi.sum()*x if qi.sum() > 0 else np.ones(x.shape),
            lambda x: 1/n*x,
            lambda x: 1-1/n*x
        ]
        
        k = newton_k(-2, k1, k2, k3) if (k1+k2+k3) > 1 else newton_k(2, k1, k2, k3)
        K = [k1, k2, k3, k]
        
        self.priority = priority
        self.U = U
        self.K = K
    
    def U_joint(self, X, U, K):
        # Multi-attribute utility function
        
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

    def U_eval(self, x_star):
        # Evaluate the quality of the current solution
        
        qi = self.qi
        U = self.U
        K = self.K
        priority = self.priority

        n, m = self.data.shape
        X = x_star.reshape(n,m)

        vals = pd.Series({
            "rank1": np.ones((n,1)).T.dot(X.dot(np.eye(1,m,0).T)).ravel()[0],
            "unmatched": np.ones((n,1)).T.dot(np.ones((n,1))-X.dot(np.ones((m,1)))).ravel()[0],
            "equity": qi.T.dot(X.dot(np.eye(1,m,2).T)+(np.ones((n,1))-X.dot(np.ones((m,1))))).ravel()[0]
        }).loc[priority].values.reshape(-1,3)
        score = self.U_joint(vals, U, K)[0]
        return score, vals
    
    def run(self, w):
        # This function is iteratively called by gp_minimize
        # gp_minimize is the function that does the bayesian optimization

        data = self.data
        ticket_capacity = self.ticket_capacity
        priority = self.priority
        
        epsilon = np.random.uniform(0, 0.001, size=(data.shape)).flatten()
        
        # IP objective function coefficients
        c = w[0]*self.c1 + w[1]*self.c2 + w[2]*self.c3 + epsilon
        
        try:
            m_employees, x_star = ip(data, ticket_capacity, c)
            score, vals = self.U_eval(x_star)
            
            self.iter = self.iter + 1
            
            if score >= self.bestscore:
                print("Iteration {}".format(self.iter))
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
        
        # Bounds for the 3 weight hyperparameters
        dimensions = [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)]
        
        def early_stop(res):
            # Stop the iterations if the current best solution comes up n times
            n = 10
            return (res.func_vals == res.fun).sum() >= n
        
        try:
            self.gp_res = gp_minimize(self.run, dimensions, n_points=50000, noise=1e-6, callback=early_stop)
            
        except:
            pass
    
    def show_results(self):
        # Plots results from the bayesian optimization iterations
        if self.gp_res: 
            plot_convergence(self.gp_res)
            plot_objective(self.gp_res)
            plot_evaluations(self.gp_res)
            plt.show()
        


# In[55]:


# Misc functions for project

def read_data(filename):
    temp = pd.read_csv(filename, header=None).iloc[:, 0:4]
    temp.columns = ["id", "r1", "r2", "r3"]
    temp = temp.set_index("id")
    return temp

def make_ticket_capacity(data, cap):
    tickets = sorted(data.unstack().dropna().unique().tolist())
    ticket_capacity = {}
    for t in tickets:
        ticket_capacity[t] = cap
    return ticket_capacity

def evaluate_solution(x_star, data, prev_rankings, name):
    rank1, rank2, rank3 = x_star.sum(axis=0)
    unmatched = x_star.shape[0] - rank1 - rank2 - rank3
    prev_rank = data.join(prev_rankings).iloc[:, -1].fillna(1)
    prev_angry = np.array((prev_rank == 0) | (prev_rank == 3), dtype=np.int64)
    new_angry = np.array((x_star[:, 2] > 0) | (x_star.sum(axis=1) == 0), dtype=np.int64)
    unlucky = prev_angry.dot(new_angry)
    return pd.Series({
        "rank1": rank1,
        "rank2": rank2,
        "rank3": rank3,
        "unmatched": unmatched,
        "unlucky": unlucky
    }, name=name)

def compare(data, cap, prev_rankings, admin_file, title="Performance Comparison"):
    
    ticket_capacity = make_ticket_capacity(data, cap)
    
    bo_proposed = BO(data, ticket_capacity, prev_rankings)
    bo_requested = BO(data, ticket_capacity, prev_rankings=None)

    bo_requested.optimize()
    bo_proposed.optimize()

    admin_x_star = np.array(read_data(admin_file).notnull(), dtype=np.int64)

    solutions = [
        evaluate_solution(admin_x_star, data, prev_rankings, "Admin"),
        evaluate_solution(bo_requested.x_star, data, prev_rankings, "Requested"),
        evaluate_solution(bo_proposed.x_star, data, prev_rankings, "Proposed")
    ]

    res = pd.DataFrame(solutions)
    
    ax = res.T.plot(kind="bar", color=["blue", "green", "purple"])
    plt.title(title)
    plt.ylabel("# of employees")
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.3),
              fancybox=True, shadow=True, ncol=5)
    plt.show()
    
    display(res)


# In[5]:


# Make comparison graphs

#prev_rankings = pd.DataFrame(data=np.random.randint(0, 4, 1000), index=range(0,1000), columns=["rank"])

# Typical case
#nhl_data = read_data("data/NHL3_all.csv")
#admin_file = "prev_rankings/NHL3.csv"
#title = "Performance Comparison (Typical)"
#compare(nhl_data, 17, prev_rankings, admin_file, title)

# High-demand case
#nba_data = read_data("data/NBA4_all.csv")
#admin_file = "prev_rankings/NBA4.csv"
#title = "Performance Comparison (High-demand)"
#compare(nba_data, 22, prev_rankings, admin_file, title)


# In[6]:


# Test max employee capacity
#data = read_data("data/max_employees.csv")
#prev_rankings = pd.DataFrame(np.random.randint(0, 4, data.shape), index=data.index)
#tickets = sorted(data.unstack().dropna().unique().tolist())
#ticket_capacity = make_ticket_capacity(data, 400)
#bo = BO(data, ticket_capacity, prev_rankings)
#bo.optimize()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




