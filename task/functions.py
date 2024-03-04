import pandas as pd
import os.path
import random
from itertools import cycle, islice

from psychopy import prefs
prefs.hardware['audioLib'] = ['ptb']
from psychopy.sound.backend_ptb import SoundPTB as Sound
from psychopy import visual, core, event
from psychtoolbox import GetSecs, WaitSecs, hid
from psychopy.hardware.keyboard import Keyboard

def open_log(SUB_NUM, BLOCK_NUM):
    log = "data/logs/sub-" + SUB_NUM + "_blk-" + BLOCK_NUM + ".log"

    if not os.path.isfile(log): # create log file if it doesn't exist
        print(f"Creating {log}")
        d = {
        'seed': [],
        'sub_num': [],
        'block_num': [],
        'cond': [],
        'seq_num': [],
        'target': [],
        'n_target_plays': [],
        'tone_num' : [],
        'freq': [],
        'dur': [],
        'mark': [],
        'is_target': [],
        'n_targets': [],
        'response': [],
        'correct': [],
        'score': [],
        }
        print(d)
        df = pd.DataFrame(data = d)
        df.to_csv(log, mode='w', index = False)
    return(log)

def get_score(LOG):
    log = pd.read_csv(LOG)
    scores = log['score']
    if len(scores) == 0:
        score = 0
    else:
        score = scores.iloc[-1]
    score = int(score)
    return(score)

def get_seq_num(LOG):
    log = pd.read_csv(LOG)
    seq_nums = log['seq_num']
    if len(seq_nums) == 0:
        seq_num = 0
    else:
        seq_num = seq_nums.iloc[-1]
    seq_num = int(seq_num)
    return(seq_num)

def get_condition(SUB_NUM, BLOCK_NUM):
    conditions = ['short', 'low', 'long', 'high']
    n = int(SUB_NUM) % 4
    cond_list = list(islice(cycle(conditions), n, n+4))
    cond = cond_list[int(BLOCK_NUM)]
    return cond

def get_target_marks(COND):
    if COND == 'short':
        marks = [11, 21]
    elif COND == 'low':
        marks = [11, 12]
    elif COND == 'long':
        marks = [12, 22]
    elif COND == 'high':
        marks = [21, 22]
    return(marks)

def fixation(WIN):
    fixation = visual.TextStim(WIN, '+')
    fixation.draw()
    WIN.flip()
    return(fixation)

def welcome(WIN, BLOCK_NUM):
    if BLOCK_NUM == '1':
        welcome_text = visual.TextStim(WIN, text = f"Welcome to the study. \n Press 'enter' to continue.")
    else:
        welcome_text = visual.TextStim(WIN, text = f"Welcome to block number {BLOCK_NUM}/4. Please remember to minimize any movement and blinks. In some blocks the tones will appear in a pattern, in others they will be random. Please keep your gaze fixed on the + when it appears. Press 'enter' to begin.")
    welcome_text.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])

def get_distractor(DISTRACTOR_FREQS, DISTRACTOR_DURS):
    freq = random.choice(DISTRACTOR_FREQS)
    dur = random.choice(DISTRACTOR_DURS)
    return(freq, dur)

def display_instructions(WIN, text, keylist):
    display = visual.TextStim(WIN, text = text)
    print(text)
    event.clearEvents(eventType = None)
    display.draw()
    WIN.flip()
    key = event.waitKeys(keyList = keylist)
    WIN.flip()
    return key

def hear_targets(WIN, STIM):
    repeat = True
    while repeat:
        display_instructions(WIN, "Press 'space' to hear the short, low-pitched tone.", ['space'])
        Sound(STIM[11][0], secs = STIM[11][1]).play()
        print('sound played')
        WaitSecs(0.2)

        display_instructions(WIN, "Press 'space' to hear the long, low-pitched tone.", ['space'])
        Sound(STIM[12][0], secs = STIM[12][1]).play()
        WaitSecs(0.2)

        display_instructions(WIN, "Press 'space' to hear the short, high-pitched tone.", ['space'])
        Sound(STIM[21][0], secs = STIM[21][1]).play()
        WaitSecs(0.2)

        display_instructions(WIN, "Press 'space' to hear the long, high-pitched tone.", ['space'])
        Sound(STIM[22][0], secs = STIM[22][1]).play()
        WaitSecs(0.2)

        key = display_instructions(WIN, "Press 'r' to repeat these tones. Otherwise, press 'enter' to continue.", ['return', 'r'])
        print(key)
        if 'r' not in key:
            repeat = False
        
def hear_distractors(WIN, DISTRACTOR_FREQS, DISTRACTOR_DURS):
    repeat = True
    while repeat:
        key = display_instructions(WIN, "Press 'space' to hear examples of tones with random pitch and duration. Press 'enter' to continue to the rest of the instructions...", ['space', 'return'])
        freq, dur = get_distractor(DISTRACTOR_FREQS, DISTRACTOR_DURS)
        Sound(freq, secs = dur).play()
        if 'return' in key:
            repeat = False

def instructions(WIN, SCORE_NEEDED, STIM, DISTRACTOR_FREQS, DISTRACTOR_DURS):
    display_instructions(WIN, "In this task you will be asked to listen to sequences of tones. These tones will have one of two possible pitches, and one of two possible durations. In other words, some tones will be low-pitched with a short duration, some will be low-pitched with a long duration, some will be high-pitched with a short duration, and finally some will be high-pitched with long duration. Press 'enter' to hear these four tones...", ['return'])
                         
    # Play targets
    hear_targets(WIN, STIM)
        
    display_instructions(WIN, "In addition to tones with these two pitches and durations, distractor tones of random pitch and duration will also be interspersed within the tone sequence. Press 'enter' hear a few examples of these tones...", ['return'])
    
    # Play distractors
    hear_distractors(WIN, DISTRACTOR_FREQS, DISTRACTOR_DURS)
    
    display_instructions(WIN, "In each trial within each experiment block, you will be asked to count target tones of either a specific duration or pitch. For example, in some blocks you will be instructed to count the number of short tones, in other blocks you might be asked to count the number of high-pitched tones. You will get a chance to listen to examples of these target tones at the beginning of each trial. Press 'enter' to continue...", ['return'])
    
    display_instructions(WIN, f"At the end of each trial you will be asked how many times you heard the target tone during the trial. Use the number keys at the top of the keyboard to input your answer and then press 'enter' to submit it. Press 'enter' to continue...", ['return'])
    
    display_instructions(WIN, f"If you accurately report the number of target tones– or come close to the correct answer by 2– your 'score' will increase by 1. To finish each block, you will have to reach a score of {SCORE_NEEDED}. There will be 4 total blocks, each lasting 15-20 minutes. Please ask your experimenter any questions you may have about the task. Press 'enter' to continue...", ['return'])

    display_instructions(WIN, "It is important for you not to move your eyes or blink while the tones are playing. We also ask that you hold the rest of your body as still as possible. To help with this, a fixation cross '+' will be shown during the tone sequence. Keep your gaze on the fixation cross and hold your body and gaze as still as you can while the cross is on the screen. Press 'enter' to continue...", ['return'])

    display_instructions(WIN, "Please also refrain from counting with your fingers or any body parts, or from touching any of the electrodes n the cap. Press 'enter' to continue...", ['return'])

    display_instructions(WIN, "You will now complete one practice trial before experiment blocks begin. Press 'enter' to begin the practice trial...", ['return'])

def end_practice(WIN):
    display_instructions(WIN, "Thank you for completing the practice trial. Press 'enter' to proceed to the experiment trials.", ['return'])
    
def play_target(WIN, COND, STIM, TARGET_MARKS):
    # Get target sound objects
    t_snds = [Sound(STIM[TARGET_MARKS[0]][0], secs = STIM[TARGET_MARKS[0]][1]),
             Sound(STIM[TARGET_MARKS[1]][0], secs = STIM[TARGET_MARKS[1]][1])]

    target_text = visual.TextStim(WIN, text = f"Please listen for the {COND} tones. Press 'space' to hear examples of a {COND} tone. Press 'enter' to begin the trial.")
    target_text.draw()
    WIN.flip()
    target_played = False
    n_target_plays = 0
    while True:
        keys = event.getKeys(keyList = ['space', 'return'])
        if 'return' in keys and n_target_plays == 0: # Don't advance if enter was pressed before the first target play
            keys = []
        elif 'space' in keys:
            t_snd = random.choice(t_snds)
            t_snd.play()
            target_played = True
            n_target_plays += 1
            print('Target played')
        elif 'return' in keys:
            break

    return(n_target_plays)

def play_sequence(MARKER, STIM, ISI, TARGET_MARKS, DISTRACTOR_PROB, DISTRACTOR_FREQS, DISTRACTOR_DURS, n_tones):
    n_targets = 0
    force = False
    one_back = 0
    two_back = 0

    # play first tone
    tone_nums, freqs, durs, marks, is_targets = play_first_tone(MARKER, STIM, ISI, TARGET_MARKS)

    for tone_num in range(2, n_tones + 1):
        print(tone_num, end = ', ', flush = True)

        # if not force, select a random tone
        if force:
            force, mark, one_back, two_back = check_repeats(STIM, mark, one_back, two_back)
        else:
            mark = random.choice(list(STIM.keys()))

        # decide if random distractor tone is playing
        if random.random() > DISTRACTOR_PROB:
            freq = STIM[mark][0]
            dur = STIM[mark][1]
        else:
            freq, dur = get_distractor(DISTRACTOR_FREQS, DISTRACTOR_DURS)
            mark = 3
        snd = Sound(freq, secs = dur)

        # increment target count
        is_target = 0
        if mark in TARGET_MARKS:
            is_target = 1
            n_targets += 1

        # schedule sound
        now = GetSecs()
        snd.play(when = now + 0.1)
        WaitSecs(0.1)
#         MARKER.send(mark)
        WaitSecs(dur)
    
        # ISI
        WaitSecs(ISI - 0.1) # subtract buffer

        # Add jitter
        WaitSecs(random.uniform(0, 0.05))

        # save tone info
        tone_nums.append(tone_num)
        freqs.append(freq)
        durs.append(dur)
        marks.append(mark)
        is_targets.append(is_target)

    print('')
    return(tone_nums, freqs, durs, marks, is_targets, n_targets)

def play_first_tone(MARKER, STIM, ISI, target_marks):
    print('1', end = ', ', flush = True)

    first_tone_mark = 11
    while first_tone_mark in target_marks:
        first_tone_mark = random.choice(list(STIM.keys()))
    freq = STIM[first_tone_mark][0]
    dur = STIM[first_tone_mark][1]
    snd = Sound(freq, secs = dur) 

    # schedule sound
    now = GetSecs()
    snd = Sound(freq, secs = dur)
    snd.play(when = now + 0.1) # 0.1 msec buffer
    WaitSecs(0.1)
#     MARKER.send(mark)
    WaitSecs(dur)

    # Add ISI - buffer + jitter
    WaitSecs(ISI - 0.1 + random.uniform(0, 0.05))

    tone_nums = [1]
    freqs = [freq]
    durs = [dur]
    marks = [first_tone_mark]
    is_targets = [0]

    return(tone_nums, freqs, durs, marks, is_targets)

def check_repeats(STIM, mark, one_back, two_back): # CHECK THIS
    if mark == one_back == two_back:
        force = True
        replacement_mark = 11
        while replacement_mark == one_back:
            replacement_mark = random.choice(list(STIM.keys()))
    else:
        force = False
        replacement_mark = None
    two_back = one_back
    one_back = mark
    return(force, replacement_mark, one_back, two_back)

def broadcast(n_tones, var):
    if not isinstance(var, list):
        broadcasted_array = [var]*n_tones
    return(broadcasted_array)

def write_log(LOG, n_tones, SEED, SUB_NUM, BLOCK_NUM, cond, seq_num, target, 
              n_target_plays, tone_nums, freqs, durs, marks, is_targets, 
              n_targets, response, correct, score):
    print("Writing to log file")
    d = {
        'seed': broadcast(n_tones, SEED),
        'sub_num': broadcast(n_tones, SUB_NUM),
        'block_num': broadcast(n_tones, BLOCK_NUM),
        'cond': broadcast(n_tones, predictable),
        'seq_num': broadcast(n_tones, seq_num),
        'target': broadcast(n_tones, target),
        'n_target_plays': broadcast(n_tones, n_target_plays),
        'tone_num' : tone_nums,
        'freq': freqs,
        'dur': durs,
        'mark': marks,
        'is_target': is_targets,
        'n_targets': broadcast(n_tones, n_targets),
        'response': broadcast(n_tones, response),
        'correct': broadcast(n_tones, correct),
        'score': broadcast(n_tones, score),
        }
    df = pd.DataFrame(data = d)
    df.to_csv(LOG, mode='a', header = False, index = False)

def get_response(WIN):
    # Prompt response
    ask_response = visual.TextStim(WIN, text = "How many times did you hear the target tone?")
    ask_response.draw()
    WIN.flip()

    # Fetch response
    keylist = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'return', 'backspace']
    response = []
    response_text = ''

    while True:
        keys = event.getKeys(keyList = keylist)
        if response_text and 'return' in keys: # empty response not accepted
            break
        elif keys:
            if 'return' in keys:
                None
            elif 'backspace' in keys:
                response = response[:-1]
            else:
                response.append(keys)
            response_text = ''.join([item for sublist in response for item in sublist])
            WIN.flip()
            show_response = visual.TextStim(WIN, text = response_text)
            show_response.draw()
            WIN.flip()

    response = int(response_text)
    return(response)

def update_score(WIN, n_targets, response, score, SCORE_NEEDED):
    if abs(n_targets - response) == 0:
        correct = 2
        score += 1
        display_instructions(WIN, f"You are correct! There were {n_targets} targets. Your score is now {score}/{SCORE_NEEDED}. Press 'enter' to continue.", ['return'])
    elif abs(n_targets - response) <= 2:
        correct = 1
        score += 1
        display_instructions(WIN, f"Close enough! There were {n_targets} targets. Your score is now {score}/{SCORE_NEEDED}. Press 'enter' to continue.", ['return'])
    else:
        correct = 0
        display_instructions(WIN, f"There were {n_targets} targets. Your score remains {score}/{SCORE_NEEDED}. Press 'enter' to continue.", ['return'])
    return(correct, score)

def block_end(WIN, BLOCK_NUM):
    if BLOCK_NUM == "4":
        block_end_text = visual.TextStim(WIN, text = f"Congratulations, you have completed the experiment! Your experimenter will be with you shortly. Thank you for participating.")
    else:
        block_end_text = visual.TextStim(WIN, text = f"Congratulations, the block is now over. Your experimenter will be with you shortly.")
    block_end_text.draw()
    WIN.flip()
    WaitSecs(15)
