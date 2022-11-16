import requests as req
from abc import abstractmethod
from argparse import ArgumentParser
from typing import Union, Literal
import json
import yaml
from pathlib import Path
import sys

class Crawlin:
	def __init__(self, **kwargs) -> None:
		self.data = dict(kwargs)

	@abstractmethod
	def crawlin (self):
		pass

	def load (self, url:Union[str, bytes], *args, **kwargs)->req.Response:
		return req.get(url, args, kwargs)

	def dump (self, type:Literal['json', 'yaml'], path:Union[Path, str, None])->str:
		if path:
			if isinstance(path, Path):
				if path.exists() and not path.is_dir():
					with path.open('w') as f:
						if type == 'json':
							json.dump(self.data, f)
						else:
							yaml.dump(self.data, f)
			else:
				if type == 'json':
					with open(path, 'w') as f:
						if type == 'json':
							json.dump(self.data, f)
						else:
							yaml.dump(self.data, f)

		if type == 'json': #json
			return json.dumps(self.data)
		else: #yaml
			return yaml.dump(self.data, sys.stdout)

def argparser ()->ArgumentParser:
	parser = ArgumentParser(
				prog= 'Crawlius, goofy ahh crawler ever',
				description= '"It\'s Crawlin Time." said Crawlius, and he started to crawlin everywhere.',
			)
	parser.add_argument('-o', '--output_path', type=str, default=None)
	return parser