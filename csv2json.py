#!/usr/bin/env python3

import os
import argparse
import json

def process_id_header(id, headers):
  try:
    i = int(id)
  except ValueError:
    try:
      i = headers.index(id)
    except ValueError:
      return
  headers[i] = '_id'

def rejoin_split_strings(fields):
  # TODO improve
  # TODO test
  b_idx = []
  e_idx = []
  for i in range(len(fields)):
    curr_field = fields[i]
    if curr_field \
    and curr_field[0] == '"' \
    and curr_field[-1] != '"':
      b_idx.append(i)
    if curr_field \
    and curr_field[-1] == '"' \
    and curr_field[0] != '"':
      e_idx.append(i+1)
  for i in range(len(b_idx)):
    fields[b_idx[i]] = ','.join(fields[b_idx[i]:e_idx[i]])
    for r in range(b_idx[i]+1, e_idx[i]):
      fields.pop(r)
    # cleanup quotation marks
    fields[b_idx[i]] = fields[b_idx[i]][1:-1]

def convert_to_number(fields):
  for i in range(len(fields)):
    try:
      fields[i] = float(fields[i])
      if fields[i] * 10 % 10 == 0:
        fields[i] = int(fields[i])
    except ValueError:
      pass

def main():
  # Define command-line arguments
  parser = argparse.ArgumentParser(description='Convert CSV to MongoDB ready JSON')
  parser.add_argument('input_file', help='Input CSV file/path')
  parser.add_argument('--out', '-o', action='store', metavar='output_file', help='Output JSON file/path', dest='json_filename')
  parser.add_argument('--id', action='store', default=None, metavar='id_header', help='name of header field which should be assigned as _id')
  # TODO implement
  parser.add_argument('--noover', action='store_true', help='NOT YET IMPLEMENTED - Do not overwrite output JSON file', dest='no_overwrite')
  args = parser.parse_args()


  csv_path = os.path.abspath(args.input_file)

  if args.json_filename:
    json_filename = args.json_filename
  else:
    # same name as input file, replace .csv with .json
    json_filename = '{}.json'.format(os.path.basename(csv_path).rsplit('.',1)[0])

  # create file (overwrite existing one)
  with open(json_filename, 'w') as json_file:
    json_file.write('')

  with open(csv_path, 'r') as csv_file:
    headers = csv_file.readline()
    headers = headers.strip().split(',')
    if args.id:
      # replace desired header name with _id
      process_id_header(args.id, headers)

    for line in csv_file:
      fields = line.strip().split(',')
      # Rejoin strings
      rejoin_split_strings(fields)
      convert_to_number(fields)
      doc = {}
      for i in range(len(headers)):
        doc[headers[i]] = fields[i]
      with open(json_filename, 'a') as json_file:
        json.dump(doc,json_file, indent=None)
        json_file.write('\n')

if __name__ == '__main__':
  main()

# TODO add unit tests
# TODO add embedded fields (dot notation)
# TODO add upsert (push array fields for multiple entries with same ID)
