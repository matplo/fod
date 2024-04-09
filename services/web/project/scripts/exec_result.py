# exec_result.py

import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'external'))

def exec_result(execute, data):
  module = execute.split('.')[0]
  function = execute.split('.')[1]
  # find the module and load it
  module = __import__(f'project.scripts.external.{module}', fromlist=[function])
  function = getattr(module, function)
  # find the function and call it
  # return eval(f'{function}("{data}")')
  # return sys.path
  return function(data)
