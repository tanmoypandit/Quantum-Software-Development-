import numpy as np
import itertools

def sn(r,n):
    # r: matrix with survival prob and error
    # n: the n in S_n
    
    r = np.array(r)
    
    def a(n,k):
        if k == 0:
            coef = -( 2 - 1/n )
        elif k>= 1:
            coef = -(2*(2*n-1)/n)*(np.math.factorial(n)**2)/(np.math.factorial(n-k)*np.math.factorial(n+k)) * (-1)**k
        else: 
            raise SyntaxError('error...') 
            sys.exit(1) 
        return coef
    
    dim = r.ndim
      
    if dim ==1:
        value = np.sum([a(n,k)*r[k] for k in range(n+1)])
        return value
    elif dim ==2:
        value = np.sum([a(n,k)*r[k][0] for k in range(n+1)])
        error = np.sqrt(np.sum([(a(n,k)*r[k][1])**2 for k in range(n+1)]))    
        return [value, error] 
    
    
def sig(r, n):
    # r: matrix with survival prob and error
    # n: the n in S_n    
    
    r = np.array(r)    
    
    def vander_matrix(n):
        return np.vander(range(n+1),increasing=True)
    
    def a(n,k): 
        pf = -1 # o python considera o primeiro elemento 0,0
        return np.linalg.inv(vander_matrix(n))[2+pf][k+1+pf]    

    dim = r.ndim
    
    if dim ==1:
        value = np.sum([a(n,k)*r[k] for k in range(n+1)])
        return value
    elif dim ==2:
        value = np.sum([a(n,k)*r[k][0] for k in range(n+1)])
        error = np.sqrt(np.sum([(a(n,k)*r[k][1])**2 for k in range(n+1)]))    
        return [value, error]     
    

def kik(r, n, N=2):
    
    # 1/(1+KIK)^{1/N}
    
    import scipy.special
    
    def binom(n,m):
        return scipy.special.binom(n, m)

    r = np.array(r)
    dim = r.ndim
      
    if dim ==1:
        r = r[0:n+1]

        tab_1=[]
        for l in range(n+1):
            tab_2=[]
            for m in range(l, n+1):                 
                tab_2.extend([(-1)**(m+l)*binom(-1/N,m)*binom(m,l)])
            tab_1.extend([sum(tab_2)])

        return np.inner(r,tab_1)
    
    elif dim ==2:
        
        r0 = r[0:n+1,0]
        r1 = r[0:n+1,1]

        tab_1=[]
        for l in range(n+1):
            tab_2=[]
            for m in range(l, n+1):                 
                tab_2.extend([(-1)**(m+l)*binom(-1/N, m)*binom(m,l)])
            tab_1.extend([sum(tab_2)])
            
        value = np.inner(r0, tab_1)
        error = np.sqrt(np.inner(np.square(r1),np.square(tab_1)))  
        return [value, error]  

def state_label(n):
    label=[f'{i:0{n}b}' for i in range(2**n)]
    return label
    
# To find the qubits that are being measured in the circuit.     
def qubit_measured(circ):
    tab = []
    for i in range(len(circ.data)):
        if circ.to_instruction().definition[i][0].name == 'measure':
            bit_map = {bit: index for index, bit in enumerate(circ.qubits)}
            tab.extend(list(map(bit_map.get, circ.to_instruction().definition[i][1])))
    return tab 
    
    
    
    
def kikL2(r, n, mu):
    
    
    def L2coefficients(mu, length): 
        # mu = np.abs(mu)
        if length == 0:
            return [1]
        elif length == 1:
            return [1 + 1/(1 + np.sqrt(mu))**3 + 3/(2*(1+np.sqrt(mu))**2), -(5+3*np.sqrt(mu))/(2*(1 + np.sqrt(mu))**3)]
        elif length == 2:
            return [+1+16/(3*(1 + np.sqrt(mu))**5) - 14/(3*(1+np.sqrt(mu))**4) + 4/(1 + np.sqrt(mu))**2, 
                    -((4*(10 + 8*np.sqrt(mu) + 9*mu + 3*mu**(3/2)))/(3*(1 + np.sqrt(mu))**5)), 
                    +(2*(13 + 5*np.sqrt(mu)))/(3*(1 + np.sqrt(mu))**5)]
        elif length == 3:
            return [(31 + 97*np.sqrt(mu) + 276*mu + 300*(mu)**(3/2) + 270*(mu)**2 + 114*mu**(5/2) + 28*(mu)**3 + 4*(mu)**(7/2))/(4*(1+np.sqrt(mu))**7), 
                    -((5*(29+35*np.sqrt(mu) + 84*(mu) + 44*(mu)**(3/2) + 26*(mu)**2 + 6*(mu)**(5/2)))/(4*(1 + np.sqrt(mu))**7)),
                    +(3*(81 + 47*np.sqrt(mu) + 76*(mu) + 20*(mu)**(3/2)))/(4*(1 + np.sqrt(mu))**7), 
                    -5*(25 + 7*np.sqrt(mu))/(4*(1+np.sqrt(mu))**7)]
    
    import scipy.special
    
    r = np.array(r)
    dim = r.ndim
      
    if dim == 1:
        r = r[0:n+1]

        return np.inner(r,np.array(L2coefficients(mu, n))) # np.array(L2coefficients(mu, n))
    
    elif dim ==2:
        
        r0 = r[0:n+1,0]
        r1 = r[0:n+1,1]

        value = np.inner(r0, np.array(L2coefficients(mu, n)))
        error = np.sqrt(np.inner(np.square(r1),np.square(np.array(L2coefficients(mu, n)))))  
        return [value, error]   # np.array(L2coefficients(mu, n))   
    
    
    

      
def combo(L,n):
    return list(map(list,list(itertools.product(L, repeat=n))))
