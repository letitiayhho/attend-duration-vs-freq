#!/usr/bin/env python3

#SBATCH --time=00:15:00 # only need 15 minutes for regular logreg, need like 4 hrs for logregcv
#SBATCH --partition=broadwl
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --mem-per-cpu=8000
#SBATCH --mail-type=all
#SBATCH --mail-user=letitiayhho@uchicago.edu
#SBATCH --output=logs/decoding_%j.log

import mne
import numpy as np

import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from mne.decoding import SlidingEstimator, cross_val_multiscore

from util.io.bids import DataSink

def main(Zxxs, events):
    X = Zxxs

    # Create target array
    labels = pd.Series(events[:, 2])
    y = labels.replace({10001 : 0, 10002 : 1, 10003 : 2, 10004 : 3, 10005 : 4})
    le = preprocessing.LabelEncoder()
    y = le.fit_transform(y)

    # Decode
    print("---------- Decode ----------")
    n_stimuli = 5
    metric = 'accuracy'

    clf = make_pipeline(
        StandardScaler(),
        LogisticRegression(solver = 'liblinear')
    )

    print("Creating sliding estimators")
    time_decod = SlidingEstimator(clf)

    print("Fit estimators")
    scores = cross_val_multiscore(
        time_decod,
        X, # a trials x features x time array
        y, # an (n_trials,) array of integer condition labels
        cv = 5, # use stratified 5-fold cross-validation
        n_jobs = -1, # use all available CPU cores
    )
    scores = np.mean(scores, axis = 0) # average across cv splits

    # Save decoder score_shape
    print("---------- Save decoder scores ----------")
    sink = DataSink(DERIV_ROOT, 'decoding')
    scores_fpath = sink.get_path(
        subject = sub,
        task = task,
        run = run,
        desc = 'stft',
        suffix = 'scores',
        extension = 'npy',
    )
    print('Saving scores to: ' + scores_fpath)
    np.save(scores_fpath, scores)

    # Plot
    print("---------- Plot ----------")
    fig, ax = plt.subplots()
    ax.plot(range(len(scores)), scores, label = 'score')
    ax.axhline(1/n_stimuli, color = 'k', linestyle = '--', label = 'chance')
    ax.set_xlabel('Times')
    ax.set_ylabel(metric)  # Area Under the Curve
    ax.legend()
    ax.set_title('Sensor space decoding')

    # Save plot
    fig_fpath = FIGS_ROOT + '/subj-' + SUB + '_' + 'task-pitch_' + 'run-' + RUN + '_stft' + '.png'
    print('Saving figure to: ' + fig_fpath)
    plt.savefig(fig_fpath)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    Zxxs = sys.argv[1]
    events = sys.argv[2]
    main(Zxxs, events)