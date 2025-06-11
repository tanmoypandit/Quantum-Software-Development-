import numpy as np
import itertools
from qiskit import pulse, transpile, schedule as build_schedule
from qiskit import schedule
from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister

# 1) You should use schedule manipulation in your final K circuit. Transpile your circuit before use schedule manipulation.

class Sched_manipulation():
    
    def __init__(self, circuit_K, backend_device): 
        self.circ = circuit_K.remove_final_measurements(inplace=False)
        self.circ_with_meas = circuit_K
        self.backend = backend_device 
        self.num_qubits = circuit_K.num_qubits
        self.num_clbits = circuit_K.num_clbits

    def meas_sched(self): 
        local_schedule = schedule(self.circ_with_meas, self.backend)
        return local_schedule.filter(channels=list(itertools.chain(*[[pulse.AcquireChannel(i),pulse.MeasureChannel(i)] for i in range(100)])))

    def meas_circ(self): 
        qc = self.circ_with_meas.copy_empty_like()
        for _inst in self.circ_with_meas.data:
            if _inst.operation.name == 'measure':
                qc.data.append(_inst)
        return qc        
    
        
    def forward_sched(self): 
        return schedule(self.circ, self.backend)
    
    def backward_sched(self):
    
        def reverse_sig(x):
        # possibilities:
            # Delay
            # ShiftPhase
            # Waveform
            # GaussianSquare
            # Drag
            
            if type(x) == pulse.instructions.delay.Delay:
                return pulse.instructions.delay.Delay(duration = x.duration, 
                                                             channel = x.channel)
            
            elif type(x) == pulse.instructions.phase.ShiftPhase:
                return pulse.instructions.phase.ShiftPhase(-x.phase, x.channel)
            
            elif type(x) == pulse.instructions.play.Play:
                if type(x.pulse) == pulse.library.waveform.Waveform:
                    return pulse.instructions.Play(pulse.Waveform((-1)*np.flip(x.pulse.samples),
                                                                  name=x.pulse.name), x.channel, x.name)
                elif x.pulse.pulse_type == 'GaussianSquare':
                    return pulse.instructions.Play(pulse.GaussianSquare(duration = x.pulse.duration, 
                                                                        sigma    = x.pulse.sigma, 
                                                                        width    = x.pulse.width, 
                                                                        amp      = x.pulse.amp, 
                                                                        angle    = x.pulse.angle + np.pi,
                                                                        name     = x.pulse.name), x.channel, x.name)
                elif x.pulse.pulse_type == 'Drag': 
                    return pulse.instructions.Play(pulse.Drag(duration = x.pulse.duration, 
                                                              sigma    = x.pulse.sigma, 
                                                              beta     = x.pulse.beta, 
                                                              amp      = x.pulse.amp,
                                                              angle    = x.pulse.angle + np.pi,
                                                              name     = x.pulse.name), x.channel, x.name)                
                else:                              
                    raise SyntaxError('error')     
                    sys.exit(1)  
            else:                              
                raise SyntaxError('New instruction.')     
                sys.exit(1)                       

        

        local_schedule = self.forward_sched()
        duration_local = local_schedule.duration
        sched_ch = [local_schedule.filter(channels=local_schedule.channels[i]) for i in range(len(local_schedule.channels))]
        
        backward_sched = pulse.Schedule()
        for i in range(len(local_schedule.channels)):
            new_tab = tuple(list(zip(tuple(list(map(lambda x: duration_local-(x.duration),
                                                          np.array(sched_ch[i].instructions)[::,1]))-np.array(sched_ch[i].instructions)[::,0]),
            tuple(list(map(reverse_sig,np.array(sched_ch[i].instructions)[::,1]))))))    
            backward_sched += pulse.Schedule(*new_tab)    
    
        if self.forward_sched().duration == backward_sched.duration:
            return backward_sched
        else:
            raise SyntaxError('error in Sched_manipulation backward_sched') 
            sys.exit(1)   
            
 


    
