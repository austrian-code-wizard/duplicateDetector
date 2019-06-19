# -*- coding: utf-8 -*-

from duplicateDetector.algorithms import equal_levenshtein, awesome_cossim_top, ngrams, get_matches_df
from sklearn.feature_extraction.text import TfidfVectorizer
from duplicateDetector.utils import measure, get_data_and_labels
from duplicateDetector.visualizer import deploy_graph
from networkx.readwrite import json_graph
from multiprocessing import Process
from pyjarowinkler import distance
from duplicateDetector import ROOT_PATH
import networkx as nx
import pandas as pd
import webbrowser
import json


class PairHolder:
	"""class that stores the most similar pairs and performs the computation
	of the levenshtein distances"""

	def __init__(self, data):
		self._pairs = {}
		assert isinstance(data, pd.DataFrame)
		self._data = data
		self._runs = 0
		self._vis_server_process = None
		self._vis_server_ip = "127.0.0.1"
		self._vis_server_port = 8000

	@classmethod
	def get_holder_from_excel(cls, file_path: str):
		assert file_path[-5:] == ".xlsx"
		xl = pd.ExcelFile(file_path)
		sheet = xl.sheet_names[0]
		df1 = xl.parse(sheet)
		return PairHolder(df1)

	@classmethod
	def get_holder_from_dataframe(cls, df: pd.DataFrame):
		return PairHolder(df)

	@staticmethod
	def save_to_csv(result: pd.DataFrame, path) -> str:
		result = result.round(3)
		with open(path, "w+") as f:
			result.to_csv(f, index=False, encoding='utf-8')
		return path

	@staticmethod
	def create_graph(pairs, min_cluster_size):
		nodes = []
		for row in pairs.itertuples():
			nodes.append((row[1], row[2], row[3]))
		G = nx.Graph()
		G.add_weighted_edges_from(nodes)
		delete = set()
		for component in nx.connected_components(G):
			if len(component) < min_cluster_size:
				delete = delete.union(component)
		for node in delete:
			G.remove_node(node)
		return G

	@staticmethod
	def plot_graph_motplotlib(self, graph):
		nx.draw(graph, with_labels=True, width=0.6, node_color="w", node_size=800, font_family='Arial Unicode MS',
				scale=4, edge_color="grey")
		return True

	def get_unique_column_values(self, column_name):
		unique_values = self._data[column_name].unique()
		return [x for x in unique_values if str(x) != 'nan']

	def get_df_rows_from_pairs(self, pairs, field_type) -> pd.DataFrame:
		left = self._data[self._data[field_type].isin(pairs["left_side"])]
		right = self._data[self._data[field_type].isin(pairs["right_side"])]
		all = left.append(right)
		return all.drop_duplicates()

	def load_data(self, new_dataset: pd.DataFrame) -> bool:
		self._data = new_dataset
		return True

	def plot_graph(self, graph):
		g_json = json_graph.node_link_data(graph)
		with open(ROOT_PATH+"force/cluster.json", "w+") as f:
			f.write(json.dumps(g_json))
		if self._vis_server_process is None:
			self._vis_server_process = Process(target=deploy_graph, args=(self._vis_server_ip, self._vis_server_port))
			self._vis_server_process.start()
		webbrowser.open(f"http://{self._vis_server_ip}:{self._vis_server_port}")
		return True

	def _levenshtein_step(self, value_1: str, value_2: str, label_1, label_2, max_score: int) -> bool:
		"""takes in two customer data structures (list or dict) and computes
		whether their levensthein distance is close enough that they should be
		stored in the list of the top n (self._size) pairs. Returns True if
		that is the case and False otherwise"""

		index = 0
		diff = len(value_1)-len(value_2)
		index += abs(diff)
		if index > max_score:
			return False
		if diff > 0:
			value_1 = value_1[0:len(value_2)]
		elif diff < 0:
			value_2 = value_2[0:len(value_1)]
		res = equal_levenshtein(value_1, value_2, max_score-index)
		if res is False:
			return False
		else:
			index += res
		if index <= max_score:
			self._pairs["left_side"].append(label_1)
			self._pairs["right_side"].append(label_2)
			self._pairs["similarity"].append(index)
			return True
		else:
			return False

	def _jaro_winkler_step(self, value_1: str, value_2: str, label_1, label_2, max_score: int) -> bool:
		index = 0
		index += 1-distance.get_jaro_distance(value_1, value_2)
		if index <= max_score:
			self._pairs["left_side"].append(label_1)
			self._pairs["right_side"].append(label_2)
			self._pairs["similarity"].append(index)
			return True
		else:
			return False

	def _run(self, max_score: int, keys: list, label_field, step_method, data_limit=None, filter_field=None,
			 filter_value=None):
		self._runs = 0
		data, labels = get_data_and_labels(self._data, keys, label_field, data_limit=data_limit, filter_field=filter_field,
												 filter_value=filter_value)
		if len(data) == 0:
			return pd.DataFrame()
		for i in range(0, len(data)):
			for j in range(i+1, len(data)):
				self._runs += 1
				try:
					step_method(data[i], data[j], labels[i], labels[j], max_score)
				except Exception as e:
						raise e
		print(f"{self._runs} comparisons\n")
		return self._pairs

	@measure
	def run_levenshtein(self, max_score: int, keys: list, label_field, data_limit=None, filter_field=None,
						filter_value=None) -> pd.DataFrame:
		result = self._run(max_score, keys, label_field, self._levenshtein_step, data_limit=data_limit,
						   filter_field=filter_field, filter_value=filter_value)
		return pd.DataFrame(result).sort_values(['similarity'], ascending=True)

	@measure
	def run_jaro_winkler(self, max_score: float, keys: list, label_field, data_limit=None, filter_field=None,
						 filter_value=None) -> pd.DataFrame:
		result = self._run(max_score, keys, label_field, self._jaro_winkler_step, data_limit=data_limit,
						   filter_field=filter_field, filter_value=filter_value)
		return pd.DataFrame(result).sort_values(['similarity'], ascending=False)

	@measure
	def run_cosine(self, min_score: float, keys: list, label_field, data_limit=None, filter_field=None,
						filter_value=None) -> pd.DataFrame:
		data_strings, labels = get_data_and_labels(self._data, keys, label_field, data_limit=data_limit,
														 filter_field=filter_field, filter_value=filter_value)
		vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams)
		tf_idf_matrix = vectorizer.fit_transform(data_strings)
		matches = awesome_cossim_top(tf_idf_matrix, tf_idf_matrix.transpose(), 10, min_score)
		matches_df = get_matches_df(matches, labels, top=None)
		matches_df = matches_df[matches_df.left_side != matches_df.right_side]
		matches_df = matches_df.round(3)
		return matches_df.sort_values(['similarity'], ascending=False)

	@measure
	def cluster_levenshtein(self, max_score: float, keys: list, label_field, data_limit=None, min_cluster_size=3,
					filter_field=None, filter_value=None) -> list:

		result = self.run_levenshtein(max_score, keys, label_field, data_limit, filter_field=filter_field,
								 filter_value=filter_value)
		graph = self.create_graph(result, min_cluster_size)
		results = []
		for k in nx.connected_components(graph):
			results.append(self._data[self._data[label_field].isin(k)])
		return results

	@measure
	def cluster_jaro_winkler(self, max_score: float, keys: list, label_field, data_limit=None, min_cluster_size=3,
					   filter_field=None, filter_value=None) -> list:

		result = self.run_jaro_winkler(max_score, keys, label_field, data_limit, filter_field=filter_field,
								 filter_value=filter_value)
		graph = self.create_graph(result, min_cluster_size)
		results = []
		for k in nx.connected_components(graph):
			results.append(self._data[self._data[label_field].isin(k)])
		return results

	@measure
	def cluster_cosine(self, min_score: float, keys: list, label_field, data_limit=None, min_cluster_size=3,
						filter_field=None, filter_value=None) -> list:

		result = self.run_cosine(min_score, keys, label_field, data_limit, filter_field=filter_field,
								 filter_value=filter_value)
		graph = self.create_graph(result, min_cluster_size)
		results = []
		for k in nx.connected_components(graph):
			results.append(self._data[self._data[label_field].isin(k)])
		return results

	@measure
	def plot_levenshtein(self, max_score: float, keys: list, label_field, data_limit=None, min_cluster_size=3,
					filter_field=None, filter_value=None) -> str:

		result = self.run_levenshtein(max_score, keys, label_field, data_limit, filter_field=filter_field,
									  filter_value=filter_value)
		graph = self.create_graph(result, min_cluster_size)
		self.plot_graph(graph)
		return f"http://{self._vis_server_ip}:{self._vis_server_port}"

	@measure
	def plot_jaro_winkler(self, max_score: float, keys: list, label_field, data_limit=None, min_cluster_size=3,
						 filter_field=None, filter_value=None) -> str:

		result = self.run_jaro_winkler(max_score, keys, label_field, data_limit, filter_field=filter_field,
									   filter_value=filter_value)
		graph = self.create_graph(result, min_cluster_size)
		self.plot_graph(graph)
		return f"http://{self._vis_server_ip}:{self._vis_server_port}"

	@measure
	def plot_cosine(self, min_score: float, keys: list, label_field, data_limit=None, min_cluster_size=3,
					filter_field=None, filter_value=None) -> str:

		result = self.run_cosine(min_score, keys, label_field, data_limit, filter_field=filter_field,
								 filter_value=filter_value)
		graph = self.create_graph(result, min_cluster_size)
		self.plot_graph(graph)
		return f"http://{self._vis_server_ip}:{self._vis_server_port}"


