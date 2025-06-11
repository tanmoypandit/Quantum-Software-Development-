import math
from math import log10, floor


# Rounding half to even



class Pretty_result():
    
    def __init__(self, result, error):
        self.result = result
        self.error = error

    def round_result(self):
        from math import log10, floor
        if self.error == 0:
            return f"{self.result}"
        else:        
            def round_to_1_sig_fig(x):
                return round(x, -int(floor(log10(abs(x)))))
            x =  -int(floor(log10(abs(round_to_1_sig_fig(self.error))))) 
            return f"{self.result:.{x}f}"
    
    def round_error(self):
        def round_to_1_sig_fig(x):
            return round(x, -int(floor(log10(abs(x)))))
        x =  -int(floor(log10(abs(round_to_1_sig_fig(self.error)))))
        return f"{self.error:.{x}f}"
    
    def pretty_form(self):
        if self.error == 0:
            return str(self.result)+str(r'({})'.format(round(self.error)))
        else:        
            def sig_dig(x): 
                y = round(x, -int(floor(log10(abs(x)))))
                return round(y / (10**floor(log10(y))))
    
            def round_result(result, error):
                def round_to_1_sig_fig(x):
                    return round(x, -int(floor(log10(abs(x)))))
                x =  -int(floor(log10(round_to_1_sig_fig(self.error))))
                return f"{result:.{x}f}"
            
            return str(round_result(self.result, self.error)+str(r'({})'.format(sig_dig(self.error))))
    