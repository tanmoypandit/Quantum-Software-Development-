from qiskit.circuit import Gate
from qiskit import QuantumCircuit 
from qiskit import transpile


def to_gate(shedule, num_qubits, qubits):
    circuit = QuantumCircuit(num_qubits)
    my_gate = Gate(name=shedule[1], num_qubits=num_qubits, params=[])  
    circuit.add_calibration(my_gate, qubits = qubits, schedule = shedule[0], params = None)
    circuit.append(my_gate, qubits)
    return circuit 

        
def to_gate_v2(shedule, name, backend):
    num_qubits = backend.configuration().n_qubits
    qubits = list(range(0,backend.configuration().n_qubits))
    circuit = QuantumCircuit(num_qubits)
    my_gate = Gate(name=name, num_qubits=num_qubits, params=[])  
    circuit.add_calibration(my_gate, qubits = qubits, schedule = shedule, params = None)
    circuit.append(my_gate, qubits)
    return circuit 


def to_gate_v3(shedule, name, num_qubits, qubits, backend):
    circuit = QuantumCircuit(backend.configuration().n_qubits)
    my_gate = Gate(name=name, num_qubits=num_qubits, params=[])  
    circuit.add_calibration(my_gate, qubits = qubits, schedule = shedule, params = None)
    circuit.append(my_gate, qubits)
    return circuit 

def to_gate_v4(shedule, name, num_qubits, num_bits_cr, qubits, backend):
    circuit = QuantumCircuit(backend.configuration().n_qubits, num_bits_cr)
    my_gate = Gate(name=name, num_qubits=num_qubits, params= [], label=f'{name}')  
    circuit.add_calibration(my_gate, qubits = qubits, schedule = shedule, params = [1])
    circuit.append(my_gate, qubits)
    return circuit #transpile(circuit , optimization_level = 0, seed_transpiler = 0, backend = backend, scheduling_method='asap')

