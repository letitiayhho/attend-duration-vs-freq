from psychopy import visual, core, event
from psychtoolbox import WaitSecs
from events import EventMarker
from functions import *

# constants
FREQS = [110, 150, 210]
    # Tags should be AB,
    # where A is predictability where random = 1, predictable = 2
    # where B is tone number where 110 = 1, 150 = 2, 210 = 3
SEQ_LENS = [46, 50, 54]
TONE_LEN = 0.3
ISI = 0.3
SCORE_NEEDED = 25

# ask for subject and block number
SUB_NUM = input("Input subject number: ")
BLOCK_NUM = input("Input block number (1-6): ")

# set subject number, block and seq_num as seed
SEED = int(SUB_NUM + "0" + BLOCK_NUM + str(seq_num))
print("Current seed: " + str(SEED))
random.seed(SEED)

# set up keyboard, window and RTBox
WIN = visual.Window(size = (1920, 1080),
    screen = -1,
    units = "norm",
    fullscr = False,
    pos = (0, 0),
    allowGUI = False)
KB = get_keyboard('Dell Dell USB Entry Keyboard')
MARKER = EventMarker()

# open log file
LOG = open_log(SUB_NUM, BLOCK_NUM)
score = get_score(LOG)
print(f"score: {score}")
seq_num = get_seq_num(LOG)
print(f"seq_num: {seq_num}")

# randomly select condition
predictability_order = get_predictability_order()
predictable = predictability_order[int(BLOCK_NUM) - 1] # boolean

# listen to all three tones and display instructions
welcome(WIN, BLOCK_NUM) 
hear_tones(WIN, TONE_LEN, FREQS)
instructions(WIN)

# practice trial
while score < 1:
    target = get_target(FREQS)

    # Play target
    n_target_plays = play_target(WIN, TONE_LEN, target)
    ready(WIN)
    WaitSecs(1)

    # Play tones
    fixation(WIN)
    WaitSecs(1)
    if predictable:
        tone_nums, freqs, marks, is_targets, n_targets = play_predictable_sequence(
            MARKER, FREQS, TONE_LEN, ISI, condition, target, 30)
    else:
        tone_nums, freqs, marks, is_targets, n_targets = play_random_sequence(
            MARKER, FREQS, TONE_LEN, ISI, condition, target, 30)
    WIN.flip()
    WaitSecs(0.5)

    # Get response
    response = get_response(WIN)
    correct, score = update_score(WIN, n_targets, response, score, SCORE_NEEDED)

end_practice(WIN)
    
# experiment block
# play sequences until SCORE_NEEDED is reached or seq_num >= 25
while score < SCORE_NEEDED:
    n_tones = get_n_tones(SEQ_LENS)
    target = get_target(FREQS)

    # Play target
    n_target_plays = play_target(WIN, TONE_LEN, target)
    ready(WIN)
    WaitSecs(1)

    # Play tones
    fixation(WIN)
    WaitSecs(1)
    if predictable:
        tone_nums, freqs, marks, is_targets, n_targets = play_predictable_sequence(
            MARKER, FREQS, TONE_LEN, ISI, target, 30)
    else:
        tone_nums, freqs, marks, is_targets, n_targets = play_random_sequence(
            MARKER, FREQS, TONE_LEN, ISI, target, 30)    WIN.flip()
    WaitSecs(0.5)

    # Get response
    response = get_response(WIN)
    print(f'n_targets: {n_targets}')
    print(f'response: {response}')
    correct, score = update_score(WIN, n_targets, response, score, SCORE_NEEDED)
    print(f'score: {score}')
    seq_num += 1
    print(f'seq_num: {seq_num}')

    # Write log file
    write_log(LOG, n_tones, SEED, SUB_NUM, BLOCK_NUM, predictable, seq_num, target, n_target_plays, tone_nums,
              freqs, marks, is_targets, n_targets, response, correct, score)
    WaitSecs(1)
    
    # Break if more than 25 sequences have been played
    if seq_num >= 25:
        break
        
block_end()

print("Block over.")

core.quit()
