import os
import pickle

import util


class ScoreManager:
    best_scores = {}
    run_scores = {}

    filename = 'scores.dat'

    def save(self):
        for level_name, score in self.run_scores.iteritems():
            if level_name not in self.best_scores or score < self.best_scores[level_name]:
                self.best_scores[level_name] = score
        with open(self.filename, 'wb') as f:
            pickle.dump(self.best_scores, f)

    def load(self):
        self.run_scores.clear()
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as f:
                self.best_scores = pickle.load(f)

    def log_score(self, level_name, score):
        if level_name in self.run_scores:
            self.run_scores[level_name] += score
        else:
            self.run_scores[level_name] = score

    def get_record(self, mode, level_name):
        return self.best_scores.get(util.get_filename(mode, level_name), -1)
