#!/usr/bin/env python
# Simple Daikon-style invariant checker
# Andreas Zeller, May 2012
# Complete the provided code around lines 28 and 44
# Do not modify the __repr__ functions.
# Modify only the classes Range and Invariants,
# if you need additional functions, make sure
# they are inside the classes.

import sys
import math
import random
import itertools

def square_root(x, eps = 0.00001):
    assert x >= 0
    y = math.sqrt(x)
    assert abs(square(y) - x) <= eps
    return y

def square(x):
    return x * x

def double(x):
    y = x + x
    y = abs(y)
    print x, y
    return y

# The Range class tracks the types and value ranges for a single variable.
class Range:
    def __init__(self):
        self.min  = None  # Minimum value seen
        self.max  = None  # Maximum value seen
        self.type = None  # type of variable
        self.set  = set() # set of values taken

    # Invoke this for every value
    def track(self, value):
        if self.min is None or value < self.min:
            self.min = value

        if self.max is None or value > self.max:
            self.max = value

        self.type = type(value)
        self.set.add(value)

    def __repr__(self):
        return repr(self.min) + ".." + repr(self.max)


# The Invariants class tracks all Ranges for all variables seen.
class Invariants:
    def __init__(self):
        # Mapping (Function Name) -> (Event type) -> (Variable Name)
        # e.g. self.vars["sqrt"]["call"]["x"] = Range()
        # holds the range for the argument x when calling sqrt(x)
        self.vars = {}

    def track(self, frame, event, arg):
        if event not in ["call", "return"]:
            return
        fname = frame.f_code.co_name
        if fname not in self.vars:
            self.vars[fname] = dict()

        if event not in self.vars[fname]:
            self.vars[fname][event] = dict()
            for var in frame.f_locals:
                self.vars[fname][event][var] = Range()
            if event == "return":
                self.vars[fname][event]["ret"] = Range()

        for var,value in frame.f_locals.iteritems():
            self.vars[fname][event][var].track(value)

        if event == "return":
            self.vars[fname][event]["ret"].track(arg)

    def __repr__(self):
        # Return the tracked invariants
        s = ""
        for function, events in self.vars.iteritems():
            for event, vars in events.iteritems():
                s += event + " " + function + ":\n"

                for var, range in vars.iteritems():
                    s += "    assert isinstance(" + var + ", " + range.type.__name__ + ")\n"
                    s += "    assert "
                    if range.min == range.max:
                        s += var + " == " + repr(range.min)
                    else:
                        s += repr(range.min) + " <= " + var + " <= " + repr(range.max)
                    s += "\n"
                    s += "    assert %s in %s\n" % ( var, range.set)

                for var1, var2 in itertools.combinations(vars, 2):
                    val1 = vars[var1]
                    val1 = [val1.min, val1.max]
                    val2 = vars[var2]
                    val2 = [val2.min, val2.max]

                    rel = ""
                    if val1 == val2:
                        rel = "=="
                    elif val1 <= val2:
                        rel = "<="
                    elif val1 >= val2:
                        rel = ">="
                    else:
                        print "oops", var1, var2, val1, val2
                        continue

                    s += "    assert %s %s %s\n" % (var1, rel, var2)
        return s

invariants = Invariants()

def traceit(frame, event, arg):
    invariants.track(frame, event, arg)
    return traceit

#sys.settrace(traceit)
# Tester. Increase the range for more precise results when running locally
#eps = 0.000001
#for i in range(1, 10000):
#    r = int(random.random() * 1000) # An integer value between 0 and 999.99
#    z = square_root(r, eps)
#    z = square(z)
#sys.settrace(None)
#print invariants

invariants = Invariants()
sys.settrace(traceit)
for i in [3, 0, -10]:
    r = double(i)
sys.settrace(None)
print invariants
