#!/usr/bin/env python
# Simple debugger
# See instructions around line 34
import sys
import readline

# Our buggy program
def remove_html_markup(s):
    tag   = False
    quote = False
    out   = ""

    for c in s:
        if c == '<' and not quote:
            tag = True
        elif c == '>' and not quote:
            tag = False
        elif c == '"' or c == "'" and tag:
            quote = not quote
        elif not tag:
            out = out + c
    return out

# main program that runs the buggy program
def main():
    print remove_html_markup('xyz')
    print remove_html_markup('"<b>foo</b>"')
    print remove_html_markup("'<b>foo</b>'")

# globals
breakpoints = {9: True}
stepping = False
watchpoints = {}

def debug(command, my_locals):
    global stepping
    global breakpoints
    global watchpoints

    if command.find(' ') > 0:
        arg = command.split(' ')[1]
    else:
        arg = None

    if command.startswith('s'):     # step
        stepping = True
        return True
    elif command.startswith('c'):   # continue
        stepping = False
        return True
    elif command.startswith('p'):    # print
        if not arg:
            print repr(my_locals)
            return True

        if arg not in my_locals:
            print "No such variable:", arg
            return True

        print arg, "=", repr(my_locals[arg])
        return True
    elif command.startswith('b'):   # breakpoint
        if not arg:
            print "You must supply a line number"
            return False
        breakpoints[int(arg)] = True
        return True
    elif command.startswith('w'):   # watchpoint
        if not arg:
            print "You must supply a variable name"
            return False
        watchpoints[arg] = True
        return True
    elif command.startswith('q'):   # quit
        #sys.exit(0)
        return True
    else:
        print "No such command", repr(command)

    return False

commands = ["p", "s", "p tag", "p foo", "q"]

def input_command():
    #command = raw_input("(my-spyder) ")
    global commands
    command = commands.pop(0)
    return command

def traceit(frame, event, trace_arg):
    global stepping

    if event == 'line':
        if stepping or breakpoints.has_key(frame.f_lineno):
            resume = False
            while not resume:
                print event, frame.f_lineno, frame.f_code.co_name,
                print frame.f_locals
                command = input_command()
                resume = debug(command, frame.f_locals)
    return traceit

# Using the tracer
#sys.settrace(traceit)
#main()
#sys.settrace(None)

print breakpoints
debug("b 5", {'quote': False, 's': 'xyz', 'tag': False, 'c': 'b', 'out': ''})
print breakpoints == {9: True, 5: True}
