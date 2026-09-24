import argparse
import json
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--limit", type=int, default=None)
args = parser.parse_args()
items = json.load(sys.stdin)
print(json.dumps(items[:args.limit] if args.limit else items))
