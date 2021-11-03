import numpy as np
from scipy.optimize import linprog
def optimize_fulfillment(orders, sources):
    n_orders=len(orders); n_sources=len(sources)
    c=[]
    for o in orders:
        for s in sources:
            pick_cost=s["pick_cost"]*o["items"]
            ship_cost=s["ship_cost_per_lb"]*o["weight"]+s["ship_fixed"]
            if s["type"]=="store": ship_cost*=1.2
            c.append(pick_cost+ship_cost)
    A_eq=[]; b_eq=[]
    for i in range(n_orders):
        row=[0]*n_orders*n_sources
        for j in range(n_sources): row[i*n_sources+j]=1
        A_eq.append(row); b_eq.append(1)
    A_ub=[]; b_ub=[]
    for j in range(n_sources):
        row=[0]*n_orders*n_sources
        for i in range(n_orders): row[i*n_sources+j]=1
        A_ub.append(row); b_ub.append(sources[j]["capacity"])
    bounds=[(0,1)]*n_orders*n_sources
    res=linprog(c,A_ub=A_ub,b_ub=b_ub,A_eq=A_eq,b_eq=b_eq,bounds=bounds,method='highs')
    if res.success:
        assignments=[]
        for i in range(n_orders):
            j=np.argmax([res.x[i*n_sources+k] for k in range(n_sources)])
            assignments.append({"order":orders[i]["id"],"source":sources[j]["name"],"cost":round(c[i*n_sources+j],2)})
        return {"assignments":assignments,"total_cost":round(res.fun,2)}
    return {"error":"infeasible"}
if __name__=="__main__":
    orders=[{"id":"O1","items":3,"weight":5},{"id":"O2","items":1,"weight":2},{"id":"O3","items":5,"weight":8}]
    sources=[{"name":"DC-Main","type":"dc","pick_cost":0.50,"ship_cost_per_lb":0.80,"ship_fixed":3.0,"capacity":100},
             {"name":"Store-101","type":"store","pick_cost":1.20,"ship_cost_per_lb":1.00,"ship_fixed":5.0,"capacity":20}]
    print(optimize_fulfillment(orders,sources))
