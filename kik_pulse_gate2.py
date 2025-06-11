# from qiskit import schedule as build_schedule
# import itertools
# from qiskit import pulse
# import numpy as np
import sys
import importlib


# importlib.reload(sys.modules['schedule_manipulation2'])
from schedule_manipulation_pulse_gate import *
from qiskit.circuit import Gate
from qiskit import QuantumCircuit 
from quiskit_functions import *


class Kik2(Schedule_manipulation2):
    def __init__(self, circ, backend):
        """Initialize attributes of the parent class."""
        super().__init__(circ, backend)

# method_1:  'open_pulse' or 'gate'                (default: 'gate')
# method_2:  'pulse_inverse' or 'circuit_inverse'  (default: 'pulse_inverse')


################################
################################
################################
################################

    def trol3(self):  
        temp = transpile(self.circ, optimization_level = 3, seed_transpiler = 0, backend = self.backend) #, scheduling_method='alap') 
        return temp 

    
    def forward(self):
            """I realized that, maybe it is important to redefined the forward (the normal gate). The point is that, I think qiskit is using an update 
            version of the normal gate, but using the expiried version for the inverse gate. I think it will be more correct to use the both definitions
            equall footing"""

            N = self.backend.configuration().n_qubits
            Ncr = self.circ.to_instruction().num_clbits    
            forward_cicuit = self.circ # .reverse_ops()
            def gate(i):
                circ = QuantumCircuit(N,Ncr)  
                circ.append(*list(forward_cicuit.to_instruction().definition[i]))
                ### circ = transpile(circ, optimization_level = 0, seed_transpiler = 0, backend = self.backend) 
                bit_map = {bit: index for index, bit in enumerate(circ.qubits)}
                ### , method='alap'# Schedule_manipulation2(circ, self.backend).forward_sched() # .backward_sched() #.forward_sched() #
                ### sched = schedule(circuits = circ, backend = self.backend, method='alap' ) #, )
                ### sched = Schedule_manipulation2(circ, self.backend).forward_sched()
                sched = Schedule_manipulation2(circ, self.backend).forward_sched()
                return to_gate_v4(sched, 
                                  forward_cicuit.to_instruction().definition[i][0].name+f'{"F",i}',  # Por incrivel que pareca, esse {f} fez o negocio funcionar
                                  len(circ.to_instruction().definition[0][1]), 
                                  Ncr,        
                                  list(map(bit_map.get, circ[0][1])), 
                                  self.backend)
            # y = gate(0)
            # for i in range(1,reversed_cicuit.size()):  
            #     ###### y = y + gate(i)
            #     y = y.compose(gate(i))
            # return y 
            y = gate(0)
            for i in range(1,forward_cicuit.size()):  
                y = y.compose(gate(i))
            return y    
    
    
    def inverse(self):
        """ I try to use reverse_ops() to reverse the order of the gates, but sometimes it also changed the name of some gates,
        (I just saw rz_reverse), and, when I try to take to pulse schedule of this, it does not understant (I guess it is because it does accept 
        rz_reverse as a gate. Then I decided to use another approach which is just take the reversed order myself. Take a look at the line 
        y = y.compose(gate(i), I am taking the gates at the reversed order."""
        
        N = self.backend.configuration().n_qubits
        Ncr = self.circ.to_instruction().num_clbits    
        reversed_cicuit = self.circ # .reverse_ops()
        def gate(i):
            circ = QuantumCircuit(N,Ncr)  
            circ.append(*list(reversed_cicuit.to_instruction().definition[i]))
            ### circ = transpile(circ, optimization_level = 0, seed_transpiler = 0, backend = self.backend) 
            bit_map = {bit: index for index, bit in enumerate(circ.qubits)}
            ### , method='alap'# Schedule_manipulation2(circ, self.backend).forward_sched() # .backward_sched() #.forward_sched() #
            ### sched = schedule(circuits = circ, backend = self.backend, method='alap' ) #, )
            ### sched = Schedule_manipulation2(circ, self.backend).forward_sched()
            sched = Schedule_manipulation2(circ, self.backend).backward_sched()
            return to_gate_v4(sched, 
                              reversed_cicuit.to_instruction().definition[i][0].name+f'{"B",i}',  # Por incrivel que pareca, esse {i} fez o negocio funcionar
                              len(circ.to_instruction().definition[0][1]), 
                              Ncr,        
                              list(map(bit_map.get, circ[0][1])), 
                              self.backend)
        # y = gate(0)
        # for i in range(1,reversed_cicuit.size()):  
        #     ###### y = y + gate(i)
        #     y = y.compose(gate(i))
        # return y 
        y = gate(reversed_cicuit.size()-1)
        for i in reversed(range(reversed_cicuit.size()-1)):  
            ###### y = y + gate(i)
            y = y.compose(gate(i))
        return y             
        
    
    def kkik(self, n):
        N = self.backend.configuration().n_qubits
        Ncr = self.circ.to_instruction().num_clbits            
        # circ = QuantumCircuit(N,Ncr)  
        # circ.barrier()
        k = self.forward()
        ki = self.inverse()
        kik = k.compose(ki)
        for _ in range(n-1):
            kik = kik.compose(k).compose(ki)
        if n==0:
            return k
        elif n>0:
            kkik = kik.compose(k)
        else: 
            raise SyntaxError('error') 
            sys.exit(1)           
                
        duration_1 = schedule(k, backend = self.backend).duration 
        duration_2 = schedule(kkik, backend = self.backend).duration
        if (2*n+1)*duration_1 == duration_2:
            return kkik
        else: 
            raise SyntaxError(f'The duration of the kik is weird... you should check that! {duration_1,duration_2}') 
            sys.exit(1)           
        
    def ki(self):
        N = self.backend.configuration().n_qubits
        Ncr = self.circ.to_instruction().num_clbits            
        ki = self.inverse()
        if schedule(self.circ, backend = self.backend).duration == schedule(ki, backend = self.backend).duration:
            return ki      
        else: 
            return print('The duration of the inverse is not equal to the duration of the original circuit/schedule')       
          
    def kik(self, n):
        N = self.backend.configuration().n_qubits
        Ncr = self.circ.to_instruction().num_clbits            
        k = self.forward()
        ki = self.inverse()
        kik = k.compose(ki)
        for _ in range(n-1):
            kik = kik.compose(k).compose(ki)
        if n==0:
            circ = QuantumCircuit(N, Ncr)  
            circ.barrier()
            return circ
        elif n>0:
            duration_1 = schedule(k, backend = self.backend).duration 
            duration_2 = schedule(kik, backend = self.backend).duration
            if (2*n)*duration_1 == duration_2:
                return kik
            else: 
                raise SyntaxError(f'The duration of the kik is weird... you should check that! {duration_1,duration_2}') 
                sys.exit(1)
        else: 
            raise SyntaxError('error') 
            sys.exit(1)           
                
           