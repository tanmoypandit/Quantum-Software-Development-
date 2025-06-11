import numpy as np

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


    
# To find the qubits that are being measured in the circuit.     
def qubit_measured(circ):
    tab = []
    for i in range(len(circ.data)):
        if circ.to_instruction().definition[i][0].name == 'measure':
            bit_map = {bit: index for index, bit in enumerate(circ.qubits)}
            tab.extend(list(map(bit_map.get, circ.to_instruction().definition[i][1])))
    return tab 
    
    
    
    
    
    
    

