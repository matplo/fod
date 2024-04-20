#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import yaml


# need at least 3 arguments
if len(sys.argv) < 3:
		print("Usage: python3 %s <input_file> <output_file>" % sys.argv[0])
		sys.exit(1)
  
# input file
input_file = sys.argv[1]

# output file
output_file = sys.argv[2]

# check if input file exists
if not os.path.exists(input_file):
		print("Input file %s does not exist" % input_file)
		sys.exit(1)

  
# read input file as yaml
print("Input file %s..." % input_file)
with open(input_file, 'r') as f:
		data = yaml.safe_load(f)


# read output file as yaml
if not os.path.exists(output_file):
  data2 = {}
else:
	print("Merging with %s..." % output_file)
	with open(output_file, 'r') as f:
			data2 = yaml.safe_load(f)


# merge dictionaries from both files and write to output as yaml
data2.update(data)
with open(output_file, 'w') as f:
		yaml.safe_dump(data2, f, default_flow_style=False)  

print("Written %s..." % output_file)

