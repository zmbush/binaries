# coding=UTF-8

"""
  To use this file, add the following lines to:

  export PROMPT_COMMAND='PS1=/path/to/this/file'
  export PS1 PROMPT_COMMAND
"""

import sys
import os
import subprocess
import time

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

TOP    = 0b1000
BOTTOM = 0b0100
LEFT   = 0b0010
RIGHT  = 0b0001
lines = {
  TOP                 | RIGHT : '└',
  TOP          | LEFT         : '┘',
  TOP | BOTTOM                : '│',
                 LEFT | RIGHT : '─',
        BOTTOM        | RIGHT : '┌',
        BOTTOM | LEFT         : '┐',
  TOP | BOTTOM | LEFT         : '┤',
  TOP          | LEFT | RIGHT : '┴',
  TOP | BOTTOM        | RIGHT : '├',
  TOP | BOTTOM | LEFT | RIGHT : '┼',
        BOTTOM | LEFT | RIGHT : '┬'
}
def bgcolor(col, bg):
  return '\[\033[0;%d;%dm\]' % (col + 30, bg + 40)

def color(col):
  return '\[\033[0;%dm\]' % (col + 30)

def bcolor(col):
  return '\[\033[1;%dm\]' % (col + 30)

def bold():
  return '\[\033[1m\]'

def reset():
  return '\[\033[0m\]'

def inline(text, width, attr = color(MAGENTA)):
  remain = width - len(text) - 2
  l = ''
  for i in range(remain):
    l += lines[LEFT | RIGHT]
  return box(text, attr) + l

def box(text, attr = color(MAGENTA)):
  return lines[TOP | BOTTOM | LEFT] + attr + text + reset() +                  \
         lines[TOP | BOTTOM | RIGHT]

def trailOff():
  retval = ''
  for i in range(10):
    retval += lines[LEFT | RIGHT]
  return retval

def getWeb(parts):
  line = reset() + lines[BOTTOM | RIGHT] + lines[LEFT | RIGHT]
  cwd = os.getcwd().split('/')
  if 'www' in cwd:
    loc = cwd.index('www')
    wwwStuff = cwd[loc:]
    if len(wwwStuff) < 2:
      line += box("Websites") + trailOff()
      parts.append(line)
      parts.append(lines[TOP | RIGHT] + lines[LEFT | BOTTOM | RIGHT] +
                    trailOff())
      sites = sorted(os.listdir('.'))
      if len(sites) > 0:
        for i in range(len(sites) - 1):
          parts.append(' %s %s' %(lines[TOP | BOTTOM], sites[i]))
        parts.append('%s%s %s' % (lines[BOTTOM | RIGHT],
                               lines[TOP | LEFT] ,sites[len(sites) - 1]))
    elif len(wwwStuff) < 3:
      line += box(wwwStuff[1]) + trailOff()
      parts.append(line)
      parts.append(lines[TOP | RIGHT] + lines[LEFT | BOTTOM | RIGHT] + 
                    trailOff())
      sites = sorted(os.listdir('.'))
      if len(sites) > 0:
        for i in range(len(sites) - 1):
          parts.append(' %s %s%s.%s%s' %(lines[TOP | BOTTOM], color(RED),
                                     sites[i], wwwStuff[1], reset()))
        parts.append('%s%s %s%s.%s%s' % (lines[BOTTOM | RIGHT],
                               lines[TOP | LEFT], color(RED), 
                               sites[len(sites) - 1], wwwStuff[1], reset()))
    else:
      parts.append(line + box('http://' + wwwStuff[2] + '.' + wwwStuff[1] + '/' 
                              + '/'.join(wwwStuff[3:])) + trailOff())
  else:
    line += box('/'.join(cwd).replace(os.environ['HOME'], '~')) 
    line += lines[LEFT | RIGHT]
    line += box("\H") + trailOff()
    parts.append(line)
  return parts

def isGit():
  null = open('/dev/null')
  try:
    subprocess.check_output(['git', 'rev-parse', '--git-dir'], stderr=null)
    return True
  except:
    return False

def colorStat(stat):
  if stat[0] == ' ':
    check = stat[1]
    if 'M' == check:
      return color(BLUE) + stat + reset()
    elif 'A' == check:
      return color(GREEN) + stat + reset()
    elif 'D' == check:
      return color(RED) + stat + reset()
  else:
    check = stat[0]
    if 'M' == check:
      return bcolor(BLUE) + stat + reset()
    elif 'A' == check:
      return bcolor(GREEN) + stat + reset()
    elif 'D' == check:
      return bcolor(RED) + stat + reset()
    elif '?' == check:
      return bcolor(YELLOW) + stat + reset()
    elif 'R' == check:
      return bcolor(CYAN) + stat + reset()
  return stat

def gitStatus(parts):
  status = subprocess.check_output(['git', 'status', '-s'])
  gitDir = subprocess.check_output(['git', 'rev-parse', '--git-dir'])
  baseDir = '/'.join(gitDir.split('/')[:-1]) + '/'
  cwd = os.getcwd() + '/'
  repoDir = cwd.replace(baseDir, "")
  statuses = filter(bool, status.split('\n'))
  if len(statuses) > 0:
    retval = lines[TOP | RIGHT] + lines[LEFT | RIGHT | BOTTOM] +               \
             lines[LEFT | RIGHT]
    retval += box("Git Status", color(CYAN))
    retval += trailOff()
    parts.append(retval)
    for s in statuses:
      stat = s[:2]
      rest = s[3:]
      # s = s.replace(repoDir, "")
      parts.append(' %s %s' % (lines[TOP | BOTTOM], colorStat(s)))
    return True
  else:
    return False

def gitBranch():
  branches = subprocess.check_output(['git', 'branch']).split('\n')
  for b in branches:
    if b == '':
      continue
    if b[0] == '*':
      return b[2:]
  return ''

def gitRemote(branch):
  none = open('/dev/null')
  if branch == '':
    return ''
  try:
    return subprocess.check_output(['git', 'config', 
                    'branch.' + branch + '.remote'], stderr=none).split('\n')[0]
  except:
    return '?'

def gitOutgoing(parts, indented):
  none = open('/dev/null')
  try:
    remote = gitRemote(gitBranch())
    outgoing = subprocess.check_output(['git', 'log', '@{u}..', 
                          '--pretty=format:%h %s'], stderr=none).split('\n')
    outgoing = filter(bool, outgoing)
    if len(outgoing) > 0:
      line = lines[TOP | RIGHT] + lines[LEFT | RIGHT | BOTTOM] +               \
             lines[LEFT | RIGHT]
      if indented:
        line = ' ' + lines[RIGHT | TOP | BOTTOM] +                             \
                       lines[LEFT | RIGHT]
      line += box("Git Outgoing", color(CYAN))
      line += trailOff() 
      parts.append(line)
      for out in outgoing:
        parts.append(' %s %s' % (lines[TOP | BOTTOM], out))
      return True
    return indented
  except subprocess.CalledProcessError as e:
    return indented

def ensureGit(parts, indented):
  if not indented:
    line = lines[TOP | RIGHT] + lines[LEFT | RIGHT | BOTTOM] +                 \
           lines[LEFT | RIGHT]
    line += box("Git", color(CYAN)) + trailOff()
    parts.append(line)

def finalizeGit(parts, indented):
  line = lines[TOP | BOTTOM | RIGHT] + lines[LEFT | RIGHT]
  if indented:
    line = lines[BOTTOM | RIGHT] + lines[TOP | LEFT | RIGHT] +                 \
           lines[LEFT | RIGHT]
  branch = gitBranch()
  remote = gitRemote(branch)
  if branch == '':
    line += box('New Repository', color(CYAN))
  else:
    line += box(color(CYAN) + branch + reset() + ' -> ' + color(MAGENTA) +     \
            remote)
  line += trailOff()
  parts.append(line)

def getGit(parts):
  if isGit():
    indented = gitStatus(parts)
    indented = gitOutgoing(parts, indented)
    finalizeGit(parts, indented)
  return parts

def getDue(parts):
  currDir = os.getcwd().split('/')
  success = False
  openedFile = None
  while not success and len(currDir) > 0:
    try:
      openedFile = open('/'.join(currDir) + '/.due')
      success = True
    except IOError as e:
      del currDir[-1]
  if openedFile == None:
    return
  timeText = openedFile.read().strip()
  timeData = None
  try:
    timeData = time.mktime(time.strptime(timeText))
  except:
    return
  now = time.time()
  seconds = int(timeData - now)
  pastDue = False
  if seconds < 0:
    seconds -= 2*seconds
    pastDue = True
  days = seconds / (60 * 60 * 24)
  seconds = seconds % (60 * 60 * 24)
  hours = seconds / (60 * 60)
  seconds = seconds % (60 * 60)
  minutes = seconds / 60
  seconds = seconds % 60
  due = ""
  if days > 1:
    due += "%d days " % days
  elif days > 0:
    due += "%d day " % days
  if hours > 1:
    due += "%d hours " % hours
  elif hours > 0:
    due += "%d hour " % hours
  if minutes > 1:
    due += "%d minutes " % minutes
  elif minutes > 0:
    due += "%d minute " % minutes
  if seconds > 1:
    due += "%d seconds " % seconds
  elif seconds > 0:
    due += "%d second " % seconds

  due = due.strip()
  line = lines[TOP | BOTTOM | RIGHT] + lines[LEFT | RIGHT]

  mess = color(MAGENTA) + "Project"
  if not pastDue:
    mess += " due in: " + color(CYAN)
  else:
    mess += " was due: " + color(RED)
  if due != "":
    mess += due
    if pastDue:
      mess += " ago"
  else: 
    mess = "Project due: " + color(CYAN) + "now"
  line += box(mess) + trailOff()
  parts.append(line)

def main():
  parts = []
  getWeb(parts)
  getDue(parts)
  getGit(parts)
  # prompt = getWeb()
  # prompt += getGit()
  parts.append(lines[TOP | RIGHT] + lines[LEFT | RIGHT] + color(RED) + "\$ " + 
                reset())
  maxlen = 0
  retval = '\n'.join(parts)
  print retval

if __name__ == "__main__":
  main()
