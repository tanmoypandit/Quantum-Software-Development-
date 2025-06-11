# This code is given as is. It is not permitted to copy or transfer this code or parts of it.

import numpy as np
import itertools
from qiskit import pulse
from qiskit import transpile
from qiskit import schedule




class Schedule_manipulation2():
    

    
    def __init__(self, circ, backend):  
        self.circ = circ
        self.backend = backend 
        self.num_qubits = circ.num_qubits
        
    
    def forward_sched(self): 
        return schedule(circuits = self.circ, backend = self.backend) # , method='alap'
            
    
    def backward_sched(self):
    
        def reverse_sig(x):
            if type(x) == pulse.instructions.phase.ShiftPhase:
                return pulse.instructions.phase.ShiftPhase(-x.phase, x.channel)
            elif type(x) == pulse.instructions.delay.Delay:
                return x
            elif type(x) == pulse.instructions.play.Play:
                if type(x.pulse) == pulse.library.parametric_pulses.GaussianSquare:
                    return pulse.instructions.Play(pulse.GaussianSquare(x.pulse.duration, -x.pulse.amp, x.pulse.sigma, x.pulse.width, name=x.pulse.name),x.channel, x.name)
                if type(x.pulse) == pulse.library.parametric_pulses.Drag:
                    return pulse.instructions.Play(pulse.Drag(x.pulse.duration, -x.pulse.amp, x.pulse.sigma, x.pulse.beta, name=x.pulse.name),x.channel, x.name)
            else:                              # new
                raise SyntaxError('error')     # new
                sys.exit(1)                    # new   
 
        sched = schedule(self.circ, self.backend)
        channel = [sched.filter(channels=sched.channels[i]) for i in range(len(sched.channels))]
        duration = sched.duration
        new_sched = pulse.Schedule()      
        
        
        for i in range(len(sched.channels)):
            def reversing_amp_and_phase(i): return tuple(list(map(reverse_sig, np.array(channel[i].instructions)[::,1])))
            def channel_duration(i): return channel[i].duration
                
            tab = tuple(list(zip(tuple(list(
                map(lambda x: duration-(x.duration),np.array(channel[i].instructions)[::,1]))-np.array(channel[i].instructions)[::,0]),                                         reversing_amp_and_phase(i))))    
            channel_sched = pulse.Schedule(*tab)
            if channel_sched.duration == duration:
                new_sched += channel_sched
            elif duration > channel_sched.duration:
                completing_duration = duration-channel_sched.duration
                new_sched += channel_sched + pulse.Schedule(pulse.instructions.delay.Delay(completing_duration, channel_sched.channels[0]))
            else:
                raise SyntaxError('error') 
                sys.exit(1)    
        return new_sched
    
        
