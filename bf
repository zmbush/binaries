#!/usr/bin/env python
import sys
import string

debug = False

def main(): 
  if len(sys.argv) < 2:
    print 'You must specify a file'
    return 1
  else:
    try:
      program = list(open(sys.argv[1], 'r').read())
      p = 0
      pc = 0
      memory = [ 0 ]
      backSearch = 0
      forwardSearch = 0
      while pc >= 0 and pc < len(program):
        c = program[pc]
        if backSearch == 0 and forwardSearch == 0:
          if c == '>':
            p += 1
            if p == len(memory):
              memory.append(0)
          elif c == '<':
            p -= 1
            if p < 0:
              print 'Error: You can\'t have a negative pointer'
          elif c == '+':
            memory[p] = memory[p] + 1 
          elif c == '-':
            memory[p] -= 1
          elif c == '.':
            sys.stdout.write(chr(memory[p]))
          elif c == ',':
            memory[p] = ord(sys.stdin.read(1))
          elif c == '[':
            if memory[p] == 0:
              forwardSearch = 1
          elif c == ']':
            if memory[p] != 0:
              backSearch = 1
              pc -= 2
          pc += 1
        elif backSearch:
          if c == '[':
            backSearch -= 1
          elif c == ']':
            backSearch += 1
          if backSearch > 0:
            pc -= 1
        elif forwardSearch:
          if c == ']':
            forwardSearch -= 1
          elif c == '[':
            forwardSearch += 1
          if forwardSearch > 0:
            pc += 1
        if debug:
          print memory
          continue
          memstr = '['
          for m in memory:
            if chr(m) in string.printable:
              memstr += chr(m) + ","
            else:
              memstr += str(m) + ','
          memstr = memstr[:-1] + ']'
          print memstr
    except IOError: 
      print '%s: File not found' % sys.argv[1]
      return 2
if __name__ == "__main__":
  sys.exit(main())
