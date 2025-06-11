import sys
import importlib


from schedule_manipulation_v2 import *
from qiskit.circuit import Gate
from qiskit import QuantumCircuit 
from qiskit import pulse, transpile
from qiskit import schedule
from qiskit.pulse.transforms.canonicalization import block_to_schedule
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import TemplateOptimization
from qiskit.transpiler.passes.calibration import rzx_templates
from qiskit.transpiler.passes import RZXCalibrationBuilderNoEcho
from qiskit.transpiler.passes import RZXCalibrationBuilder
from qiskit.exceptions import QiskitError
from qiskit.circuit import CircuitInstruction


from qiskit.transpiler import TransformationPass
from qiskit.converters import circuit_to_dag




def to_gate(schedule_, name_, num_qubits_, num_bits_cr_, qubits_, backend_):
    circ_local = QuantumCircuit(backend_.configuration().n_qubits, num_bits_cr_)
    gate_local = Gate(name=name_, num_qubits=num_qubits_, params= [], label=f'{name_}')  
    circ_local.add_calibration(gate_local, qubits = qubits_, schedule = schedule_) # , params = []
    circ_local.append(gate_local, qubits_)
    return circ_local 




class Kik(Sched_manipulation):
    def __init__(self, circ, backend):
        super().__init__(circ, backend)
        
    def kkik(self, order):
        
        sched = self.forward_sched() 
        
        with pulse.build(self.backend) as barrier_sched:
            pulse.barrier(*list(sched.channels))
        lbs = block_to_schedule(barrier_sched)
        
        for i in range(order):
            sched = self.forward_sched() + lbs +  self.backward_sched() + lbs + sched 
        return sched    
    
    def kik(self, order):
        
        sched = self.forward_sched()
        
        with pulse.build(self.backend) as barrier_sched:
            pulse.barrier(*list(sched.channels))
        lbs = block_to_schedule(barrier_sched)
        
        sched = self.forward_sched() + lbs +  self.backward_sched() 
                
        if order==0:
            return pulse.Schedule()
        else: 
            for _ in range(order-1):
                sched = self.forward_sched() + lbs +  self.backward_sched() + lbs + sched  
            return sched    
            



# KIK PULSE GATE - This fuctions gi
class Kik_pg(Sched_manipulation):
    def __init__(self, circ, backend):
        super().__init__(circ, backend)

    # """
    # defining defaults
    # """
    # backend_version = self.backend.version
    # if backend_version == 1:
    #     defaults = self.backend.defaults()
    # elif backend_version == 2:    
    #     defaults = self.backend
    # else:
    #     raise QiskitError("Error")

    def forward(self):
        N = self.backend.configuration().n_qubits
        Ncr = self.circ.to_instruction().num_clbits    
        input_cicuit = self.circ
        def gate(i):                
            circ_local = QuantumCircuit(N, Ncr)
            #
            def_i = input_cicuit.to_instruction().definition[i]
            operation_ = def_i.operation
            qbits_ = def_i.qubits
            cbits_ = def_i.clbits
            qbits_list = [input_cicuit.find_bit(qbits_[i]).index for i in range(len(qbits_))]
            cbits_list = [input_cicuit.find_bit(cbits_[i]).index for i in range(len(cbits_))]
            circ_local.append(CircuitInstruction(operation_, qbits_list, cbits_list))
            #
            # circ_local.append(*list(input_cicuit.to_instruction().definition[i]))
            bit_map = {bit: index for index, bit in enumerate(circ_local.qubits)}
            sched_local = Sched_manipulation(circ_local, self.backend).forward_sched()
            return to_gate(sched_local, 
                           input_cicuit.to_instruction().definition[i][0].name+f'{"F",i}', 
                           len(circ_local.to_instruction().definition[0][1]), 
                           Ncr,        
                           list(map(bit_map.get, circ_local[0][1])), 
                           self.backend)
        y = gate(0)
        size_with_barriers = len(input_cicuit.to_instruction().definition)
        # old_size = input_cicuit.size()
        for i in range(1,size_with_barriers):  
            y = y.compose(gate(i))
        return y    
    
    
    def backward(self):
        N = self.backend.configuration().n_qubits
        Ncr = self.circ.to_instruction().num_clbits    
        input_cicuit = self.circ
        def gate(i):
            circ_local = QuantumCircuit(N, Ncr)  
            #
            def_i = input_cicuit.to_instruction().definition[i]
            operation_ = def_i.operation
            qbits_ = def_i.qubits
            cbits_ = def_i.clbits
            qbits_list = [input_cicuit.find_bit(qbits_[i]).index for i in range(len(qbits_))]
            cbits_list = [input_cicuit.find_bit(cbits_[i]).index for i in range(len(cbits_))]
            circ_local.append(CircuitInstruction(operation_, qbits_list, cbits_list))
            #            
            # circ_local.append(*list(input_cicuit.to_instruction().definition[i]))
            bit_map = {bit: index for index, bit in enumerate(circ_local.qubits)}
            sched_local = Sched_manipulation(circ_local, self.backend).backward_sched()
            return to_gate(sched_local, 
                           input_cicuit.to_instruction().definition[i][0].name+f'{"B",i}', 
                           len(circ_local.to_instruction().definition[0][1]), 
                           Ncr,        
                           list(map(bit_map.get, circ_local[0][1])), 
                           self.backend) 
        # old_size = input_cicuit.size()
        size_with_barriers = len(input_cicuit.to_instruction().definition)
        y = gate(size_with_barriers-1)
        for i in reversed(range(size_with_barriers-1)):  
            y = y.compose(gate(i))
        return  transpile(y, scheduling_method="asap", backend=self.backend)

    def k(self):
        N = self.backend.configuration().n_qubits
        Ncr = self.circ.to_instruction().num_clbits    
        k_circ = self.forward()
        if schedule(self.circ, backend = self.backend).duration == schedule(k_circ, backend = self.backend).duration:
            final_circuit = k_circ.compose(Sched_manipulation(self.circ_with_meas, self.backend).meas_circ())     
            return final_circuit 
        else:
            return print('The duration of the inverse is not equal to the duration of the original circuit/schedule')

        
    def ki(self):
        N = self.backend.configuration().n_qubits
        Ncr = self.circ.to_instruction().num_clbits
        ki_circ = self.backward()
        if schedule(self.circ, backend = self.backend).duration == schedule(ki_circ, backend = self.backend).duration:
            final_circuit = ki_circ.compose(Sched_manipulation(self.circ_with_meas, self.backend).meas_circ())     
            return final_circuit 
        else:
            return print('The duration of the inverse is not equal to the duration of the original circuit/schedule')
        
    def kkik(self, n):
        N = self.backend.configuration().n_qubits
        Ncr = self.circ.to_instruction().num_clbits            
        def local_barrier_circuit():
            lbc = QuantumCircuit(N, Ncr)  
            lbc.barrier()
            return lbc
        k = self.forward()
        ki = self.backward()
        kik = k.compose(local_barrier_circuit()).compose(ki)        
        for _ in range(n-1):
            kik = kik.compose(local_barrier_circuit()).compose(k).compose(local_barrier_circuit()).compose(ki).compose(local_barrier_circuit())    
        if n==0:
            final_circuit = k.compose(Sched_manipulation(self.circ_with_meas, self.backend).meas_circ())     
        elif n>0:
            kkik = kik.compose(local_barrier_circuit()).compose(k)
            duration_1 = schedule(k, backend = self.backend).duration
            duration_2 = schedule(kkik, backend = self.backend).duration
            if (2*n+1)*duration_1 == duration_2:
                final_circuit = kkik.compose(Sched_manipulation(self.circ_with_meas, self.backend).meas_circ())
            else:
                raise SyntaxError(f'The duration of the kik is weird... you should check that! {duration_1,duration_2}')
                sys.exit(1)
        else:
            raise SyntaxError('error')
            sys.exit(1)
        return final_circuit    
     
          
    def kik(self, n):
        N = self.backend.configuration().n_qubits
        Ncr = self.circ.to_instruction().num_clbits    
        def local_barrier_circuit():
            lbc = QuantumCircuit(N, Ncr)  
            lbc.barrier()
            return lbc        
        k = self.forward()
        ki = self.backward()
        kik = k.compose(local_barrier_circuit()).compose(ki)
        for _ in range(n-1):
            kik = compose(local_barrier_circuit()).compose(k)\
            .compose(local_barrier_circuit()).compose(ki).compose(local_barrier_circuit()).kik
        if n==0:
            circ = QuantumCircuit(N, Ncr)  
            # circ.barrier()
            final_circuit = circ.compose(Sched_manipulation(self.circ_with_meas, self.backend).meas_circ())     
            return final_circuit
        elif n>0:
            duration_1 = schedule(k, backend = self.backend).duration 
            duration_2 = schedule(kik, backend = self.backend).duration
            if (2*n)*duration_1 == duration_2:
                final_circuit = kik.compose(Sched_manipulation(self.circ_with_meas, self.backend).meas_circ())     
                return final_circuit
            else: 
                raise SyntaxError(f'The duration of the kik is weird... you should check that! {duration_1,duration_2}') 
                sys.exit(1)
        else: 
            raise SyntaxError('error') 
            sys.exit(1)           





class DigitalForward(TransformationPass):
    """ based on:
    https://quantumcomputing.stackexchange.com/questions/22149/replace-gate-with-known-identity-in-quantum-circuit 
    """
    def __init__(self, backend):    
        super().__init__()
        # self.circ = circuit
        self.backend = backend 
    
    """
    A transpiler pass to replace native gates with their inverse.
    """
    def run(self, dag):
        """
        defining defaults
        """
        backend_version = self.backend.version
        if backend_version == 1:
            defaults = self.backend.defaults()
        elif backend_version == 2:    
            defaults = self.backend
        else:
            raise QiskitError("Error")
            
            
        for node in dag.op_nodes():
            if node.op.name in ["barrier"]:
                dag_qubit_map = {bit: index for index, bit in enumerate(dag.qubits)}
                qubits = [dag_qubit_map[q] for q in list(node.qargs)]
                qnum = node.op.num_qubits
                replacement = QuantumCircuit(qnum)
                replacement.barrier(range(len(qubits)))
            elif node.op.name in ["rz"]:
                angle = node.op.params[0]
                replacement = QuantumCircuit(1)
                replacement.rz(angle, 0)
            elif node.op.name in ["x"]:
                replacement = QuantumCircuit(1)
                replacement.x(0)
            elif node.op.name in ["sx"]:
                replacement = QuantumCircuit(1)
                replacement.sx(0)
                #
            elif node.op.name in ["ecr"]:
                replacement = QuantumCircuit(2)
                replacement.rzx(+np.pi/4, 0, 1)
                replacement.x(0)
                replacement.rzx(-np.pi/4, 0, 1)
                #
            elif node.op.name in ["cx"]:
                dag_qubit_map = {bit: index for index, bit in enumerate(dag.qubits)}
                qubits = [dag_qubit_map[q] for q in list(node.qargs)]
                t1 = defaults.instruction_schedule_map.get('cx', qubits=qubits).duration
                t2 = defaults.instruction_schedule_map.get('cx', qubits=qubits[::-1]).duration
                if t1 < t2:
                  replacement = QuantumCircuit(2)
                  # ECR 
                  replacement.x(0)
                  replacement.rz(-np.pi/2,0)
                  # 
                  replacement.sx(1)
                  replacement.barrier(0,1)  
                  # ECR  
                  replacement.barrier(0,1)  
                  replacement.rzx(+np.pi/4, 0, 1)
                  replacement.barrier(0)  
                  replacement.x(0)
                  replacement.barrier(0)  
                  replacement.rzx(-np.pi/4, 0, 1)
                  replacement.barrier(0)      
                  #  
                elif t2 < t1:
                  replacement = QuantumCircuit(2)
                  replacement.barrier(0,1)  
                  replacement.rz(np.pi/2, 0)
                  replacement.rz(np.pi/2, 1)
                  replacement.sx(0)
                  replacement.sx(1)  
                  #
                  replacement.rz(np.pi/2, 0)
                  #
                  replacement.barrier(0,1)    
                  replacement.rzx(+np.pi/4, 1, 0)     
                  replacement.barrier(0,1)  
                  replacement.x(1)
                  replacement.barrier(0,1)  
                  replacement.rzx(-np.pi/4, 1, 0)
                  replacement.barrier(0,1)  
                  replacement.rz(1/2*np.pi, 0)
                  replacement.rz(1/2*np.pi, 1)
                  #
                  replacement.sx(0)
                  replacement.sx(1)
                  #
                  replacement.rz(-np.pi/2, 1)
                  replacement.barrier(0,1)  
            else:
                raise QiskitError("Error - miti_v3")
            dag.substitute_node_with_dag(node, circuit_to_dag(replacement))
        return dag     






class DigitalInverse(TransformationPass):
    """ based on:
    https://quantumcomputing.stackexchange.com/questions/22149/replace-gate-with-known-identity-in-quantum-circuit 
    """
    def __init__(self, backend):    
        super().__init__()
        # self.circ = circuit
        self.backend = backend 
    
    """
    A transpiler pass to replace native gates with their inverse.
    """
    def run(self, dag):
        """
        defining defaults
        """
        backend_version = self.backend.version
        if backend_version == 1:
            defaults = self.backend.defaults()
        elif backend_version == 2:    
            defaults = self.backend
        else:
            raise QiskitError("Error")
            
        for node in dag.op_nodes():
            if node.op.name in ["barrier"]:
                dag_qubit_map = {bit: index for index, bit in enumerate(dag.qubits)}
                qubits = [dag_qubit_map[q] for q in list(node.qargs)]
                qnum = node.op.num_qubits
                replacement = QuantumCircuit(qnum)
                replacement.barrier(range(len(qubits)))
            elif node.op.name in ["rz"]:
                angle = node.op.params[0]
                replacement = QuantumCircuit(1)
                replacement.rz(-1 * angle, 0)
            elif node.op.name in ["x"]:
                replacement = QuantumCircuit(1)
                replacement.rz(+1 * np.pi,0)
                replacement.x(0)
                replacement.rz(-1 * np.pi,0)
            elif node.op.name in ["sx"]:
                replacement = QuantumCircuit(1)
                replacement.rz(+1 * np.pi,0)
                replacement.sx(0)
                replacement.rz(-1 * np.pi,0)
            elif node.op.name in ["ecr"]:
                replacement = QuantumCircuit(2)
                replacement.barrier(0,1)  
                replacement.rzx(+np.pi/4, 0, 1)
                replacement.rz(+1 * np.pi,0)
                replacement.x(0)
                replacement.rz(-1 * np.pi,0)
                replacement.barrier(0,1)  
                replacement.rzx(-np.pi/4, 0, 1)
                #
            elif node.op.name in ["cx"]:
                dag_qubit_map = {bit: index for index, bit in enumerate(dag.qubits)}
                qubits = [dag_qubit_map[q] for q in list(node.qargs)]
                t1 = defaults.instruction_schedule_map.get('cx', qubits=qubits).duration
                t2 = defaults.instruction_schedule_map.get('cx', qubits=qubits[::-1]).duration
                if t1 < t2:
                  replacement = QuantumCircuit(2)
                  replacement.barrier(0,1)  
                  replacement.rzx(+np.pi/4, 0, 1)
                  replacement.barrier(0)  
                  replacement.rz(-1 * np.pi,0)
                  replacement.x(0)
                  replacement.rz(+1 * np.pi,0)
                  replacement.barrier(0)  
                  replacement.rzx(-np.pi/4, 0, 1)
                  #
                  replacement.rz(-np.pi/2,0)
                  replacement.x(0)
                  replacement.rz(+np.pi,0)
                  # 
                  replacement.rz(-1 * np.pi,1)
                  replacement.sx(1)
                  replacement.rz(+1 * np.pi,1)
                  replacement.barrier(0,1)  
                  #  
                  #  
                elif t2 < t1:
                  replacement = QuantumCircuit(2)
                  replacement.barrier(0,1)  
                  replacement.rz(-np.pi, 0)
                  replacement.sx(0)
                  replacement.rz(+np.pi/2, 0)
                  #
                  #
                  replacement.rz(-np.pi/2, 1)
                  replacement.sx(1)
                  #
                  replacement.rz(+np.pi/2, 1)
                  replacement.rzx(+np.pi/4, 1, 0)     
                  replacement.barrier(0,1)  
                  #
                  replacement.rz(-np.pi, 1)
                  replacement.x(1)
                  replacement.rz(+np.pi, 1)
                  #
                  replacement.barrier(0,1)  
                  replacement.rzx(-np.pi/4, 1, 0)  
                  replacement.rz(-3/2*np.pi, 0)
                  #
                  replacement.sx(0)
                  #
                  replacement.rz(+np.pi/2, 0)
                  #
                  replacement.rz(-np.pi, 1)
                  replacement.sx(1)
                  #
                  replacement.rz(+1/2 * np.pi, 1)
                  replacement.barrier(0,1)  
            else:
                raise QiskitError("Error - mit")
            dag.substitute_node_with_dag(node, circuit_to_dag(replacement))
        return dag     



def digital_gate(circuit: QuantumCircuit, backend)->QuantumCircuit:   
    backend_version = backend.version
    if backend_version == 1:
        defaults = backend.defaults()
    elif backend_version == 2:    
        defaults = backend
    else:
        raise QiskitError("Error")
    inst = Sched_manipulation(circuit, backend)
    final_meas = inst.meas_circ() 
    qc_regular = circuit.remove_final_measurements(inplace=False)  
    qc_regular = DigitalForward(backend)(qc_regular)
    pass_ = TemplateOptimization(**rzx_templates.rzx_templates()) 
    qc_regular = PassManager(pass_).run(qc_regular)
    pass_ = RZXCalibrationBuilderNoEcho(defaults.instruction_schedule_map)
    qc_regular = PassManager(pass_).run(qc_regular)
    qc_regular = transpile(qc_regular.compose(final_meas), backend=backend, optimization_level=0)
    return qc_regular

    
def dig_inv(circuit: QuantumCircuit, backend)->QuantumCircuit:   
    backend_version = backend.version
    if backend_version == 1:
        defaults = backend.defaults()
    elif backend_version == 2:    
        defaults = backend
    else:
        raise QiskitError("Error")
    inst = Sched_manipulation(circuit, backend)
    final_meas = inst.meas_circ() 
    _qc = circuit.remove_final_measurements(inplace=False)  
    qc_inverse = _qc.reverse_ops()
    qc_inverse = DigitalInverse(backend)(qc_inverse)
    pass_ = TemplateOptimization(**rzx_templates.rzx_templates()) 
    qc_inverse = PassManager(pass_).run(qc_inverse)
    pass_ = RZXCalibrationBuilderNoEcho(defaults.instruction_schedule_map)
    qc_inverse = PassManager(pass_).run(qc_inverse)
    qc_inverse = transpile(qc_inverse.compose(final_meas), scheduling_method="asap", backend=backend, optimization_level=0)
    return qc_inverse



def kikdigital(circuit: QuantumCircuit, n, backend)->QuantumCircuit:
    """ Building the KIK circuits.
    """
    #
    circ_barrier = QuantumCircuit(circuit.num_qubits, circuit.num_clbits)
    circ_barrier.barrier()
    #
    inst = Sched_manipulation(circuit, backend)
    final_meas = inst.meas_circ() 
    qc = circuit.remove_final_measurements(inplace=False)
    if n==0:
      circ = qc
    elif n>=1:
      qc_inv = dig_inv(qc, backend)  
      kik = qc_inv.compose(circ_barrier).compose(qc)
      circ = qc
      for i in range(n):
        circ = circ.compose(circ_barrier).compose(kik)
    circ = circ.compose(final_meas)    
    circ = transpile(circ, backend=backend, optimization_level=0)
    return circ


def kikdigitalset(circuit: QuantumCircuit, n, backend):
    """ Building the KIK circuits - mitigation and Omega_1.
    
    """
    def q_barrier():
        dag_ = circuit_to_dag(circuit)
        dag_qubit_map_ = {bit: index for index, bit in enumerate(dag_.qubits)}
        idle_wires_ = list(dag_.idle_wires())
        qubits_ = [dag_qubit_map_[q] for q in idle_wires_]
        n_ = backend.configuration().n_qubits
        list_ = list(set([i for i in range(n_)]).symmetric_difference(set(qubits_)))
        return list_

    inst = Sched_manipulation(circuit, backend)
    final_meas = inst.meas_circ() 
    qc = circuit.remove_final_measurements(inplace=False)
    kik_list = []
    kik_list.append(qc)
    qc_inv = dig_inv(qc, backend)  
    _qc = qc.copy()  
    _qc.barrier(q_barrier())
    kik = _qc.compose(qc_inv)
    _kik = kik.copy()
    _kik.barrier(q_barrier())  
    if n==0:
      circ = qc
    elif n>=1:
      circ = qc
      for i in range(n):
        circ = _kik.compose(circ)
        kik_list.append(circ)
    kik_list_with_meas = []    
    for qc in kik_list:
        _qc = qc.compose(final_meas)
        _qc = transpile(_qc, backend=backend, optimization_level=0)
        kik_list_with_meas.append(_qc)
    #    
    # kik for (Omega_1)
    __kik = kik.compose(final_meas)    
    __kik = transpile(__kik, backend=backend, optimization_level=0)
    kik_list_with_meas.append(__kik)    
    #
    return kik_list_with_meas