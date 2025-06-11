import copy
from typing import List, Optional, Union

from qiskit.circuit.exceptions import CircuitError

from qiskit import *
from qiskit import pulse
from qiskit.circuit import Gate
from qiskit.pulse import Play, Schedule, ShiftPhase


def list_duplicates_of(seq, item):
    start_at = -1
    locs = []
    while True:
        try:
            loc = seq.index(item, start_at+1)
        except ValueError:
            break
        else:
            locs.append(loc)
            start_at = loc
    return locs


class InverseGate:
    """Inverse of a quantum unitary operation."""

    def __init__(
        self,
        name: str,
        qubits: List,
        backend
    ):
        """Create the inverse of a given Gate.

        Args:
            name: The name of the gate.
            qubits: qubits the gate acts on.
            backend: IBM quantum system

        Examples:

        Create the inverse of a standard gate and apply it to a circuit.

        .. jupyter-execute::

           from qiskit import QuantumCircuit, QuantumRegister

           qr = QuantumRegister(2)
           qc = QuantumCircuit(qr)
           cxinv_gate = InverseGate('cx',[0,1],backend)
           qc.append(cxinv_gate, [0,1])
           qc.draw()

        """
        self._name = name
        self.backend = backend
        self.qubits = qubits
        self.num_qubits = len(qubits)
        # creating the new gate instance
        new_gate = Gate(self._name + '_inv', self.num_qubits, [])
        q = QuantumRegister(self.num_qubits, "q")
        qc = QuantumCircuit(q, name=self._name + '_inv')
        qc.append(new_gate, qargs=self.qubits)
        self._inv()
        qc.add_calibration(self._name + '_inv', self.qubits, self.schd, [])
        self.gate = qc


    def _inv(self):
        """Invert this gate by calling the pulse schedule of the base gate."""
        defaults = self.backend.defaults()
        inst_sched_map = defaults.instruction_schedule_map
        new_gate = inst_sched_map.get(self._name, qubits=self.qubits)
        #
        instructions = copy.deepcopy(new_gate.instructions)
        inst = []
        t0 = []
        for ints_ in instructions[::-1]:
            t, sch = ints_
            inst.append(sch)
            t0.append(t)
        #
        seen = set()
        t_steps = []
        #
        for t in t0:
            if t not in seen:
                t_steps.append(t)
                seen.add(t)
        #
        t_places = []
        for t in t_steps:
            t_temp = list_duplicates_of(t0, t)
            t_places.append(t_temp)
        schd = Schedule(name=self._name+"_inv")
        for idx_t in t_places:
            #
            schd_temp = Schedule()
            for idx in idx_t:
                #
                sh = inst[idx]
                if sh.__class__.__name__ == "ShiftPhase":
                    op, ch = sh.operands
                    schd_temp += ShiftPhase(-1.0*op, ch)
                else:
                    amp_ = copy.deepcopy(sh.pulse.amp)
                    sh.pulse.__dict__['_amp'] = -amp_
                    op, ch = sh.operands
                    schd_temp += Play(op, ch)
            #
            schd |= schd_temp << schd.duration
        self.schd = schd
        