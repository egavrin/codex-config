import argparse
import json
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--threads', type=int)
args = parser.parse_args()
data = json.load(sys.stdin)
threads = data.get('file', {}).get('threads') or data['defaults']['threads']
threads = os.getenv('THREADS') or threads
threads = args.threads or threads
print(json.dumps({'threads': int(threads)}))
