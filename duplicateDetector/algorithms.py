# -*- coding: utf-8 -*-

import sparse_dot_topn.sparse_dot_topn as ct
from scipy.sparse import csr_matrix
import pandas as pd
import numpy as np
import pylev
import re


def equal_levenshtein(string1: str, string2: str, min_index: int) -> int:
	"""recursive levenshtein. only looks at the next number of chars that could
	mean that the levenshtein distance of this string pair is higher than the
	minimum required. If it is not, calls itself on the rest of the strings.
	This way, we not check all the strings at once but do it in sections since
	the minimum distance may already be reached after checking half of the
	string, saving valuable computing resources (levenshtein has complexity
	O(m*n) where m and n are the lengths of the two strings compared)"""

	length = len(string1)
	if length <= min_index:
		return pylev.levenshtein(string1, string2)
	else:
		index = pylev.levenshtein(string1[0:min_index+1], string2[
				0:min_index+1])
		if index > min_index:
			return False
		else:
			sub_index = equal_levenshtein(string1[min_index+1:], string2[min_index+1:], min_index-index)
			if sub_index is False:
				return False
			else:
				index += sub_index
				if index > min_index:
					return False
				else:
					return index


def ngrams(string, n=3):
	string = re.sub(r'[,-./]|\sBD',r'', string)
	ngrams = zip(*[string[i:] for i in range(n)])
	return [''.join(ngram) for ngram in ngrams]


def get_matches_df(sparse_matrix, name_vector, top=None):
	non_zeros = sparse_matrix.nonzero()

	sparserows = non_zeros[0]
	sparsecols = non_zeros[1]

	if top:
		nr_matches = top
	else:
		nr_matches = sparsecols.size

	left_side = np.empty([nr_matches], dtype=object)
	right_side = np.empty([nr_matches], dtype=object)
	similarity = np.zeros(nr_matches)

	for index in range(0, nr_matches):
		left_side[index] = name_vector[sparserows[index]]
		right_side[index] = name_vector[sparsecols[index]]
		similarity[index] = sparse_matrix.data[index]

	return pd.DataFrame({'left_side': left_side, 'right_side': right_side, 'similarity': similarity})


def awesome_cossim_top(A, B, ntop, lower_bound=0):
	# force A and B as a CSR matrix.
	# If they have already been CSR, there is no overhead
	A = A.tocsr()
	B = B.tocsr()
	M, _ = A.shape
	_, N = B.shape

	idx_dtype = np.int32

	nnz_max = M * ntop

	indptr = np.zeros(M + 1, dtype=idx_dtype)
	indices = np.zeros(nnz_max, dtype=idx_dtype)
	data = np.zeros(nnz_max, dtype=A.dtype)

	ct.sparse_dot_topn(
		M, N, np.asarray(A.indptr, dtype=idx_dtype),
		np.asarray(A.indices, dtype=idx_dtype),
		A.data,
		np.asarray(B.indptr, dtype=idx_dtype),
		np.asarray(B.indices, dtype=idx_dtype),
		B.data,
		ntop,
		lower_bound,
		indptr, indices, data)

	return csr_matrix((data, indices, indptr), shape=(M, N))
