"""
An implementation of spherical k-means, a variant of k-means clustering
useful for text clustering or other applications where inputs should be
length-normalized.

This implementation was made for the purpose of producing a visualization, so
instead of a single call that iterates until stability, it has a tick() method
to perform a single iteration.
"""
import numpy as np
from sklearn.preprocessing import normalize
# LICENSE:
# Copyright 2016 Eric Alzheimer
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__    = "Eric Alzheimer"
__copyright__ = "Copyright 2016 Eric Alzheimer"
__license__   = "MIT"

import matplotlib.pyplot as plt
def plot_kmeans(x):
    """ Plot the state of the k-means clusterer (see class below)"""
    plt.scatter(x.records()[:,0], x.records()[:,1], marker=',', c=x.classes(), cmap=plt.get_cmap("coolwarm"))
    plt.scatter(x.medoids()[:,0], x.medoids()[:, 1], marker=",", c="black")
    plt.show()

class IterativeSphericalKMeans:
    """
    Implements "iterative" spherical k-means. This is "iterative" because it
    is designed to allow the user to control when to run an iteration. This
    way, the state during each iteration can be visualized.
    """
    def __init__(self, initial_k, num_features, max_k=10, max_records=500):
        """
        initial_k:    Number of clusters
        num_features: Number of features in each vector
        max_k:        Max number of clusters
        max_records:  Max number of input vectors (records)
        """
        self.k = initial_k
        if self.k > max_k:
            self.k = max_k
        elif self.k < 1:
            self.k = 1

        self.num_records = 0
        self.next_to_replace = 0
        self.num_features = num_features
        self.max_records = max_records
        self.max_k = max_k

        # Input data:
        self._records = np.empty((max_records, num_features))

        # Clusters:
        self._medoids = np.zeros((max_k, num_features))

        # Classification (cluster number) for each record
        self._classes = np.zeros(max_records, dtype=int)

        # Need random initial positions for each medoid
        for medoid in self.medoids():
            medoid[...] = self._random_angle()

    def classes(self):
        return self._classes[:self.num_records]

    def records(self):
        return self._records[:self.num_records]

    def medoids(self):
        return self._medoids[:self.k]

    def _random_angle(self):
        """Returns a random positive angle"""
        return normalize(np.abs(np.random.randn(self.num_features).reshape(1, -1)))

    def iterate(self):
        # First, classify each record
        # A record is classified by the index of the medoid is is most similar
        # to (ie, largest dot product)
        self.classes()[...] = self.records().dot(self.medoids().transpose()).argmax(axis=1).astype(int)
        # Wow that was easy

        # Now update each medoid
        # New medoid is constructed by summing all cluster members and then
        # renormalizing
        classes = self.classes()
        records = self.records()
        for i, medoid in enumerate(self.medoids()):
            medoid[...] = normalize(((classes == i).reshape(-1, 1) * 
                records).sum(axis=0).reshape(1, -1))
            if (medoid == 0).all():
                medoid[...] = self._random_angle()

    def set_k(self, new_k):
        if new_k > self.max_k:
            new_k = self.max_k
        elif new_k < 1:
            new_k = 1

        while new_k > self.k:
            self._medoids[self.k] = self._random_angle()
            self.k += 1

        while new_k < self.k:
            self.k -= 1

    def shuffle(self):
        for medoid in self.medoids():
            medoid[...] = self._random_angle()

    def add_record(self, record):
        nrecord = normalize(np.asarray(record).reshape(1, -1))
        self._records[self.next_to_replace] = nrecord
        self.next_to_replace += 1
        
        if self.next_to_replace >= self.max_records:
            self.next_to_replace = 0

        if self.num_records < self.max_records:
            self.num_records += 1

    def add_records(self, records):
        for record in records:
            self.add_record(record)

