import argparse
import json
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--mode')
args = parser.parse_args()
config = json.load(sys.stdin)
print(json.dumps({'mode': os.getenv('APP_MODE') or args.mode or config.get('mode', 'safe')}))
