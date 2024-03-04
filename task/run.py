#!/usr/bin/env python3

from psychopy import visual, core, event
from psychtoolbox import WaitSecs
from events import EventMarker
from functions import *

# constants
STIM = { # keys are event markers, first value is freq, second is duration
    11: [130, 0.2],
    12: [130, 0.4],
    21: [210, 0.2],
    22: [210, 0.4]
    }
DISTRACTOR_FREQS = [150, 170, 190]
DISTRACTOR_DURS = [0.25, 0.3, 0.35]
DISTRACTOR_PROB = 1/8

SEQ_LEN_MIN = 42
SEQ_LEN_MAX = 50
ISI = 0.2
SCORE_NEEDED = 24
PRACTICE_SCORE_NEEDED = 1

# ask for subject and block number
SUB_NUM = input("Input subject number: ")
BLOCK_NUM = input("Input block number (1-4): ")
TUTORIAL = input("Run tutorial and instructions (y/n)? ")

# set subject number and block as seed
SEED = int(SUB_NUM + "0" + BLOCK_NUM)
print("Current seed: " + str(SEED))
random.seed(SEED)

# set up keyboard, window and RTBox
WIN = visual.Window(
    size = (500, 300), # comment out and set fullscr = True
    screen = -1,
    units = "norm",
    fullscr = False,
    pos = (0, 0),
    allowGUI = False)
# MARKER = EventMarker()
MARKER = None

# open log file
LOG = open_log(SUB_NUM, BLOCK_NUM)
score = get_score(LOG)
print(f"score: {score}")
seq_num = get_seq_num(LOG)
print(f"seq_num: {seq_num}")

# randomly select condition
COND = get_condition(SUB_NUM, BLOCK_NUM)
print(f'condition: {COND}')
TARGET_MARKS = get_target_marks(COND)

# listen to all three tones and display instructions
welcome(WIN, BLOCK_NUM) 

# instructions and practice trial
practice_passed = False
if TUTORIAL == "y":
    instructions(WIN, SCORE_NEEDED, STIM, DISTRACTOR_FREQS, DISTRACTOR_DURS)

    while not practice_passed:

        # Play target
        n_target_plays = play_target(WIN, COND, STIM, TARGET_MARKS)
        WaitSecs(1)

        # Play tones
        fixation(WIN)
        WaitSecs(1)
        tone_nums, freqs, durs, marks, is_targets, n_targets = play_sequence(
            MARKER, STIM, ISI, TARGET_MARKS, DISTRACTOR_PROB, DISTRACTOR_FREQS, 
            DISTRACTOR_DURS, 30)
        WIN.flip()
        WaitSecs(0.5)

        # Get response
        response = get_response(WIN)
        correct, practice_passed = update_score(WIN, n_targets, response, 0, 1)
    end_practice(WIN)
    
# experiment block
# play sequences until SCORE_NEEDED is reached or seq_num >= 25
while score < SCORE_NEEDED:
    seq_num += 1
    print(f'seq_num: {seq_num}')

    # Play target
    n_target_plays = play_target(WIN, COND, STIM, TARGET_MARKS)
    WaitSecs(2)

    # Play tones
    n_tones = random.randint(SEQ_LEN_MIN, SEQ_LEN_MAX)
    fixation(WIN)
    WaitSecs(2)
    tone_nums, freqs, durs, marks, is_targets, n_targets = play_sequence(
        MARKER, STIM, ISI, TARGET_MARKS, DISTRACTOR_PROB, DISTRACTOR_FREQS, 
        DISTRACTOR_DURS, n_tones)
    WaitSecs(0.5)

    # Get response
    print(f'n_targets: {n_targets}')
    response = get_response(WIN)
    print(f'response: {response}')
    correct, score = update_score(WIN, n_targets, response, score, 
                                  SCORE_NEEDED)
    print(f'score: {score}')

    # Write log file
    write_log(LOG, n_tones, SEED, SUB_NUM, BLOCK_NUM, cond, seq_num, target, 
              n_target_plays, tone_nums, freqs, durs, marks, is_targets, 
              n_targets, response, correct, score)
    WaitSecs(1)
    
    # Break if 3 extra sequences have been played
    if seq_num >= SCORE_NEEDED + 3:
        break
        
block_end(WIN, BLOCK_NUM)

print("Block over.")

core.quit()
