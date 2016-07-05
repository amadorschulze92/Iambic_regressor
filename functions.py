import nltk 
from nltk.corpus import cmudict
import string
import numpy as np
import pandas as pd
from pprint import pprint
import re
from math import ceil
from textblob import TextBlob
import cPickle

class PoetryParser(object):


	def __init__(self, parser_name='template_name'):

		self.parser_name = parser_names


	def clean_words(self, words, verbose=True):   
	    # returns cleans words so they are usable
	    junk = ",.:?!"                              # Punctuation I dont want
	    poss_is = "'s"                              # remove possessive since doesnt add syllable and is not in corpus
	    poss_are = "'re"
	    new_words = []                             # list to collect all the cleaned words
	    for word in words:
	        word = str(word)
	        word = word.decode('utf-8').encode('ascii', 'ignore').strip()
	        if poss_is in word and poss_is == word[-2:]:
	            word = word.replace(poss_is,'')     # removed poss_is
	        elif poss_are in word and poss_are == word[-3:]:
	            word = word.replace(poss_are, '')   # remove poss_are
	        elif word[-2:] == "'d":
	            word = word.replace("'d","")
	        else:
	            word = word.replace("'","")
	        if '...' in word:
	            word = word.replace('...','')
	        for j in junk:
	            word = word.replace(j,'')           # remove junk
	        if '--' in word:
	            word = word.replace('-','')
	        elif '-' in word:                         # splits hyphenated words
	            hyph = word.split('-')
	            new_words.append(hyph[0].decode('utf-8').encode('ascii', 'ignore').strip())
	            new_words.append(hyph[1].decode('utf-8').encode('ascii', 'ignore').strip())
	        else:
	            new_words.append(word)              # put cleaned word in new_words
	    return new_words

	# This function was taken from 'http://eayd.in/?p=232' and modified, I found, with the modifications, it to be more 
	# effective for known modern words than the function I originally created. But this function worked less well against 
	# abbreviations, old english, or slang.

	def sylco(self, new_words, verbose=False) :
	    syllables = []
	    for word in new_words:
	        word = word.lower()
	        # exception_add are words that need extra syllables
	        # exception_del are words that need less syllables

	        exception_add = ['serious','crucial']
	        exception_del = ['fortunately','unfortunately']

	        co_one = ['cool','coach','coat','coal','count','coin','coarse','coup','coif','cook','coign','coiffe','coof','court']
	        co_two = ['coapt','coed','coinci']

	        pre_one = ['preach']

	        syls = 0 #added syllable number
	        disc = 0 #discarded syllable number

	        #1) if letters < 3 : return 1
	        if len(word) <= 3 :
	            word_syl = 1
	            syllables.append(word_syl)
	            continue

	        #2) if doesn't end with "ted" or "tes" or "ses" or "ied" or "ies", discard "es" and "ed" at the end.
	        # if it has only 1 vowel or 1 set of consecutive vowels, discard. (like "speed", "fled" etc.)

	        if word[-2:] == "es" or word[-2:] == "ed" :
	            doubleAndtripple_1 = len(re.findall(r'[eaoui][eaoui]',word))
	            if doubleAndtripple_1 > 1 or len(re.findall(r'[eaoui][^eaoui]',word)) > 1 :
	                if word[-3:] == "ted" or word[-3:] == "tes" or word[-3:] == "ses" or word[-3:] == "ied" or word[-3:] == "ies" :
	                    pass
	                else :
	                    disc+=1

	        #3) discard trailing "e", except where ending is "le"  

	        le_except = ['whole','mobile','pole','male','female','hale','pale','tale','sale','aisle','whale','while']

	        if word[-1:] == "e" :
	            if word[-2:] == "le" and word not in le_except :
	                pass

	            else :
	                disc+=1

	        #4) check if consecutive vowels exists, triplets or pairs, count them as one.

	        doubleAndtripple = len(re.findall(r'[eaoui][eaoui]',word))
	        tripple = len(re.findall(r'[eaoui][eaoui][eaoui]',word))
	        disc+=doubleAndtripple + tripple

	        #5) count remaining vowels in word.
	        numVowels = len(re.findall(r'[eaoui]',word))

	        #6) add one if starts with "mc"
	        if word[:2] == "mc" :
	            syls+=1

	        #7) add one if ends with "y" but is not surrouned by vowel
	        if word[-1:] == "y" and word[-2] not in "aeoui" :
	            syls +=1

	        #8) add one if "y" is surrounded by non-vowels and is not in the last word.

	        for i,j in enumerate(word) :
	            if j == "y" :
	                if (i != 0) and (i != len(word)-1) :
	                    if word[i-1] not in "aeoui" and word[i+1] not in "aeoui" :
	                        syls+=1

	        #9) if starts with "tri-" or "bi-" and is followed by a vowel, add one.

	        if word[:3] == "tri" and word[3] in "aeoui" :
	            syls+=1

	        if word[:2] == "bi" and word[2] in "aeoui" :
	            syls+=1

	        #10) if ends with "-ian", should be counted as two syllables, except for "-tian" and "-cian"

	        if word[-3:] == "ian" : 
	        #and (word[-4:] != "cian" or word[-4:] != "tian") :
	            if word[-4:] == "cian" or word[-4:] == "tian" :
	                pass
	            else :
	                syls+=1

	        #11) if starts with "co-" and is followed by a vowel, check if exists in the double syllable dictionary, if not, check if in single dictionary and act accordingly.

	        if word[:2] == "co" and word[2] in 'eaoui' :

	            if word[:4] in co_two or word[:5] in co_two or word[:6] in co_two :
	                syls+=1
	            elif word[:4] in co_one or word[:5] in co_one or word[:6] in co_one :
	                pass
	            else :
	                syls+=1

	        #12) if starts with "pre-" and is followed by a vowel, check if exists in the double syllable dictionary, if not, check if in single dictionary and act accordingly.

	        if word[:3] == "pre" and word[3] in 'eaoui' :
	            if word[:6] in pre_one :
	                pass
	            else :
	                syls+=1

	        #13) check for "-n't" and cross match with dictionary to add syllable.

	        negative = ["doesn't", "isn't", "shouldn't", "couldn't","wouldn't"]

	        if word[-3:] == "n't" :
	            if word in negative :
	                syls+=1
	            else :
	                pass  

	        #14) Handling the exceptional words.

	        if word in exception_del :
	            disc+=1

	        if word in exception_add :
	            syls+=1    

	        # calculate the output
	        word_syl = numVowels - disc + syls
	        syllables.append(word_syl)
	    syllables = [x for x in syllables if x != 0]
	    return syllables

	def compile_meter_list(self, new_words, verbose=True):
	    # simplifies and compiles cmu cormpus info into listed list
	    iambic = cmudict.dict()                     # connect to cmu corpus, called iambic
	    big_list = []                               # list to collect all the different versions of words and their meter
	    for word in new_words:                      # get word from list of clean words
	        syl_num = sylco([word])
	        word_n_versions_list = []               # list has each word and the different versions
	        word_n_versions_list.append(word)       # add word
	        versions_list = []                      # list of all diff versions
	        try:                                    # if word is in corpus
	            for n,x in enumerate(iambic[word.lower()]): # get versions for each word
	                version = []                    # list for each version
	                version.append(word+str(n))     # add word+version
	                meter_list = []                 # list holds word version's meter
	                for y in x:                     # for word in cmu-dict sent
	                    for char in y:              # for character in word
	                        if char.isdigit() == True: # if the char is a number
	                            meter_list.append(int(char)) # add number to meter
	                version.append(meter_list)      # add meter to the word version
	                versions_list.append(version)   # add all the versions to one list
	            word_n_versions_list.append(versions_list) # add list of diff versions to word and versions list
	            big_list.append(word_n_versions_list)       
	        except:                                 # if word isnt in corpus
	            version = []                        # empty version
	            version.append(word+str(0))         # add word1
	            meter_list = []                     # empty meter list
	            if len(syl_num) == 1:
	                for syl in range(syl_num[0]):          # for each syllable...
	                    meter_list.append(-1)           # add 0 to meter_list
	                version.append(meter_list)          # add empty meter list to version
	                versions_list.append(version)       # add version w/ word1 to versions list
	                word_n_versions_list.append(versions_list) # add list of diff versions to word and versions list
	                big_list.append(word_n_versions_list) # adds word and versions to big list
	    return big_list

	def find_best(self, line, intended_syllables, optimal=[0,1,0,1,0,1,0,1,0,1,0,1], verbose=True):
	    # finds best version of meter for each word and creates the best meter for the line.
	    optimal_line = []
	    optimal_meter = []
	    
	    syllable_index = 0
	    
	    for syllables, word_list in zip(intended_syllables, line):
	        
	        if verbose:
	            print 'Current syllable index:', syllable_index
	            print 'Current word key:', word_list
	        
	        best_score = float('Inf')
	        best_inflections = []
	        
	        for word, inflection_option in word_list[1]:
	                
	            if not len(inflection_option) == 0:
	                
	                if len(inflection_option) > syllables:
	                    inflection_option = inflection_option[:syllables]
	                
	                current_optimal = optimal[syllable_index:syllable_index+syllables]
	                score = sum([abs(i - o) for i, o in zip(inflection_option, current_optimal)])
	                
	                if verbose:
	                    print 'Word inflections option:', inflection_option, 'score:', score

	                if score < best_score:
	                    best_inflections = inflection_option
	                    best_score = score
	                elif score == 10 and syllables == 10:
	                    best_inflections = inflection_option
	                    best_score = score
	        
	        optimal_line.append([word_list[0],[word_list[0], best_inflections]])
	        optimal_meter.append(best_inflections)
	        syllable_index = syllable_index + syllables
	        
	        if verbose:
	            print 'Current optimal line:\n', 
	            pprint(optimal_line)
	            print '-----------------------------------------\n'
	        
	    return optimal_line, optimal_meter

	def get_sentiment(self, new_words, verbose=False):
	    line = ' '.join(new_words)
	    feels = TextBlob(str(line))
	    return feels.sentiment

	def parse_sonnet_lines(self, sonnet_lines, author, verbose=1):
	    
	    # We're making the DataFrame at the end, from the full set of parsed
	    # lines, so first set up the "container" of columns.
	    # DataFrames can take numpy arrays where a list of lists is equivalent
	    # to each row an internal list, columns lengths of the interal lists.
	    syllable_inflection_columns = []
	    word_list_column = []
	    sonnet_num_list = []
	    author_list = []
	    polarity_list = []
	    subjectivity_list = []
	    
	    # Track how many completed and skipped lines. Ideally the only skipped
	    # lines are at the beginning and end, but skips regardless.
	    completed_lines = 0
	    skipped_lines = 0
	    
	    # Iterate through the sonnet lines. Keep track of line index
	    # in case you want to add more information from the sonnet lines later.
	    for line_index, line in enumerate(sonnet_lines):
	        
	        # Print out tracking information. It's slow so nice to see where it is.
	        if verbose == 1:
	            if (line_index % 10 == 0):
	                print 'sonnet line:', line_index+1, 'complete inflections:', len(syllable_inflection_columns)
	        
	        # skip if nothing there
	        if line == np.nan:
	            line = 'empty'
	        
	        # Split words in the line. Then cleans the words
	        words = line.split()
	        cleaned_words = clean_words(words, verbose=False)
	        
	        # If len < 2 skip.
	        if len(cleaned_words) < 1:
	            continue
	        elif clean_words == ['empty']:
	            continue
	        elif len(cleaned_words) == 1:
	            sonnet_num = cleaned_words[0]
	        else:
	            
	            # Set up the current row for the DataFrame, which is an internal list
	            # for the list of lists.
	            syllable_inflection_row = []
	            
	            # Append the index of the line in the original sonnet_lines list.
	            # This will be column 1 of the DataFrame.
	            syllable_inflection_row.append(line_index)
	            
	            if (verbose == 2): 
	                print 'counting syllables'
	            line_syllables = sylco(cleaned_words, verbose=False)
	            sum_line_syllables = sum(line_syllables)
	            
	            # Append the syllable count. Column 2 of the DataFrame.
	            syllable_inflection_row.append(sum_line_syllables)
	            
	            # Append sentiment
	            feels = get_sentiment(cleaned_words)
	            
	            if (verbose == 2): 
	                print 'compiling meter list'
	            word_listed_list = compile_meter_list(cleaned_words, verbose=False)
	            
	            if (verbose == 2): 
	                print 'finding optimal meter'
	            optimal_line, optimal_meter = find_best(word_listed_list, line_syllables,
	                                                    verbose=False)
	            optimal_meter_compress = [i for sublist in optimal_meter for i in sublist]
	            
	            # Some lines don't have 12 syllables. For the missing syllables add -1s 
	            # to the end of the list until 12 syllables long.
	            if len(optimal_meter_compress) < 12:
	                missing_inflections = [-1 for i in range(12-len(optimal_meter_compress))]
	                optimal_meter_compress = optimal_meter_compress + missing_inflections
	            
	            for inflection in optimal_meter_compress:
	                # Append string indicators for inflections, for dummy coding in your
	                # model later.
	                if inflection == 1:
	                    syllable_inflection_row.append('stress')
	                elif inflection == 0:
	                    syllable_inflection_row.append('unstress')
	                elif inflection == -1:
	                    syllable_inflection_row.append('missing')
	            
	            # Check to make sure the row is actually 14 columns long, 
	            # or the DataFrame creation at the end will break.
	            if len(syllable_inflection_row) == 13:
	                if verbose: 
	                    print 'Missing columns in row!!', len(syllable_inflection_row)
	                syllable_inflection_row.append('missing')
	                print "Fixed it!!", len(syllable_inflection_row)
	                # adds the syllable row
	                syllable_inflection_columns.append(syllable_inflection_row)
	                # adds list of words for that row
	                word_list_column.append(cleaned_words)
	                # adds which sonnet it is
	                if author == "shakespeare":
	                    sonnet_num_list.append(int(1+ceil(line_index/16)))
	                else:
	                    sonnet_num_list.append(int(1+ceil(line_index/14)))
	                # adds author
	                author_list.append(author)
	                # adds sentiment
	                polarity_list.append(feels.polarity)
	                subjectivity_list.append(feels.subjectivity)
	            elif len(syllable_inflection_row) < 14:
	                if verbose: 
	                    print 'Missing columns in row !!', len(syllable_inflection_row)
	                    print 'LEAVING THIS LINE OUT!!'
	                    skipped_lines += 1
	            elif len(syllable_inflection_row) == 15:
	                if syllable_inflection_row[-1] == "missing":
	                    del syllable_inflection_row[-1]
	                    print "Fixed it !!", len(syllable_inflection_row)
	                    # adds the syllable row
	                    syllable_inflection_columns.append(syllable_inflection_row)
	                    # adds list of words for that row
	                    word_list_column.append(cleaned_words)
	                    # adds which sonnet it is
	                    if author == "shakespeare":
	                        sonnet_num_list.append(int(1+ceil(line_index/16)))
	                    else:
	                        sonnet_num_list.append(int(1+ceil(line_index/14)))
	                    # adds author
	                    author_list.append(author)
	                    # adds sentiment
	                    polarity_list.append(feels.polarity)
	                    subjectivity_list.append(feels.subjectivity)
	            elif len(syllable_inflection_row) > 14:
	                if verbose: 
	                    print 'Too many columns in row !!', len(syllable_inflection_row)
	                    print 'LEAVING THIS LINE OUT!!' 
	                    skipped_lines += 1
	            else:
	                # adds the syllable row
	                syllable_inflection_columns.append(syllable_inflection_row)
	                # adds list of words for that row
	                word_list_column.append(cleaned_words)
	                # adds which sonnet it is
	                if author == "shakespeare":
	                    sonnet_num_list.append(int(1+ceil(line_index/16)))
	                else:
	                    sonnet_num_list.append(int(1+ceil(line_index/14)))
	                # adds author
	                author_list.append(author)
	                # adds sentiment
	                polarity_list.append(feels.polarity)
	                subjectivity_list.append(feels.subjectivity)
	            
	            print 'sonnet number', line_index
	            completed_lines += 1
	            
	    if verbose == 1:
	        print 'completed_lines:', completed_lines, 'skipped lines:', skipped_lines
	    
	    # Turn the list of lists into a numpy array. This creates a matrix
	    # of dimensions (num_sonnet_lines x 14).
	    syllable_inflection_columns = np.array(syllable_inflection_columns)
	    
	    print "FINISHED !!!"
	    return syllable_inflection_columns, word_list_column, sonnet_num_list, author_list, polarity_list, subjectivity_list

def text_line_parser(self, noise_list):
    text_list = []
    meter_list = []

    for sind, sentence in enumerate(noise_list):
        sentence = sentence.split()
        cleaned_words = clean_words(sentence)
    #     print cleaned_words
        line_syllables = sylco(cleaned_words)

        line_cutoff = 0
        cutoff_sentence = []
        for ind, ls in enumerate(line_syllables):
            line_cutoff += ls
            if (line_cutoff >= 9) and (line_cutoff <= 12):
                cutoff_sentence = cleaned_words[0:ind]
            elif line_cutoff > 12:
                break

        if len(cutoff_sentence) == 0:
            continue
        else:
            #valid_sentences.append(cutoff_sentence)
            print 'viable sentence index:', sind

            #print line_syllables
            word_listed_list = compile_meter_list(cutoff_sentence)

            error = 3
            bad_optimal = [[1,1,1,1,1,1,1,1,1,1,1,1],[0,0,0,0,0,0,0,0,0,0,0,0]]

            for optimal in bad_optimal:
                optimal_line, optimal_meter = find_best(word_listed_list, line_syllables, optimal=optimal, verbose=False)
                omc = [item for sublist in optimal_meter for item in sublist]

                matched_length = len([x for x, o, in zip(omc, optimal[0:len(omc)]) if x in [o, 2]])

                if not (matched_length >= len(opt_meter_compress)-error):
                        continue
                else:
                    print 'actually optimal:', sind
                    text_list.append(cutoff_sentence)
                    meter_list.append(opt_meter_compress)
    return text_list, meter_list

# saving:
# filepath = open('filename.p', 'w')
# cPickle.dump(current_text_lines, filepath)
# filepath.close()
#
# loading:
# filepath = open('filename.p', 'r')
# loaded_text_lines = cPickle.load(filepath)
# filepath.close()


# running a script:
# first, add the function to the class
# change the functions it needs to self.whatever()
# at the bottom of the script your class is in:
#

# this goes at the very bottom at the script:
# if __name__ == '__main__':
    
#     austen_text_file = 'some_file_path'
#     pp = PoetryParser()
    
#     austen_text = pp.parse_austen_text()
    
#     pickle_filepath = 'pickle_filepath.p'
    
#     # your new function which is part of PoetryParser now:
#     pp.get_invalid_lines(austen_text_file, pickle_filepath)

# now, to run the script:
# > python poetry_parser.py

def text_to_df(self, text_list, meter_list, author):    

    syllable_inflection_columns = []
	word_list_column = []
    sonnet_num_list = []
    author_list = []
    polarity_list = []
    subjectivity_list = []

    # Track how many completed and skipped lines. Ideally the only skipped
    # lines are at the beginning and end, but skips regardless.
    completed_lines = 0
    skipped_lines = 0

    for line_index, (t, m) in enumerate(zip(text_list, meter_list)):
        print t, m
        # Set up the current row for the DataFrame, which is an internal list
        # for the list of lists.
        syllable_inflection_row = []

        # Append the index of the line in the original sonnet_lines list.
        # This will be column 1 of the DataFrame.
        syllable_inflection_row.append(line_index)

        print 'counting syllables'
        line_syllables = sylco(t, verbose=False)
        sum_line_syllables = sum(line_syllables)

        # Append the syllable count. Column 2 of the DataFrame.
        syllable_inflection_row.append(sum_line_syllables)

        # Append sentiment
        feels = get_sentiment(t)

        if len(meter_list) < 12:
            missing_inflections = [-1 for i in range(12-len(m))]
            optimal_meter_compress = m + missing_inflections

        for inflection in m:
            # Append string indicators for inflections, for dummy coding in your
            # model later.
            if inflection == 1:
                syllable_inflection_row.append('stress')
            elif inflection == 0:
                syllable_inflection_row.append('unstress')
            elif inflection == -1:
                syllable_inflection_row.append('missing')
            elif inflection == 2:
                if syllable_inflection_row[-1] == 1:
                    syllable_inflection_row.append('unstress')
                elif syllable_inflection_row[-1] == 0:
                    syllable_inflection_row.append('stress')
                else:
                    syllable_inflection_row.append('unstress')

                # Check to make sure the row is actually 14 columns long, 
                # or the DataFrame creation at the end will break.
        if len(syllable_inflection_row) == 13:
            print 'Missing columns in row!!', len(syllable_inflection_row)
            syllable_inflection_row.append('missing')
            print "Fixed it!!", len(syllable_inflection_row)
            # adds the syllable row
            syllable_inflection_columns.append(syllable_inflection_row)
            # adds list of words for that row
            word_list_column.append(t)
            # adds which sonnet it is
            sonnet_num_list.append(line_index)
            # adds author
            author_list.append(author)
            # adds sentiment
            polarity_list.append(feels.polarity)
            subjectivity_list.append(feels.subjectivity)
        elif len(syllable_inflection_row) < 14:
            print 'Missing columns in row !!', len(syllable_inflection_row)
            print 'LEAVING THIS LINE OUT!!'
            skipped_lines += 1
        elif len(syllable_inflection_row) == 15:
            if syllable_inflection_row[-1] == "missing":
                del syllable_inflection_row[-1]
                print "Fixed it !!", len(syllable_inflection_row)
                # adds the syllable row
                syllable_inflection_columns.append(syllable_inflection_row)
                # adds list of words for that row
                word_list_column.append(t)
                # adds which sonnet it is
                sonnet_num_list.append(line_index)
                # adds author
                author_list.append(author)
                # adds sentiment
                polarity_list.append(feels.polarity)
                subjectivity_list.append(feels.subjectivity)
        elif len(syllable_inflection_row) > 14:
            print 'Too many columns in row !!', len(syllable_inflection_row)
            print 'LEAVING THIS LINE OUT!!' 
            skipped_lines += 1
        else:
            # adds the syllable row
            syllable_inflection_columns.append(syllable_inflection_row)
            # adds list of words for that row
            word_list_column.append(t)
            # adds which sonnet it is
            sonnet_num_list.append(line_index)
            # adds author
            author_list.append(author)
            # adds sentiment
            polarity_list.append(feels.polarity)
            subjectivity_list.append(feels.subjectivity)

        print 'sonnet number', line_index
        completed_lines += 1

    print 'completed_lines:', completed_lines, 'skipped lines:', skipped_lines

    # Turn the list of lists into a numpy array. This creates a matrix
    # of dimensions (num_sonnet_lines x 14).
    syllable_inflection_columns = np.array(syllable_inflection_columns)

    print "FINISHED !!!"
    return syllable_inflection_columns, word_list_column, sonnet_num_list, author_list, polarity_list, subjectivity_list

	def create_dataframe(self, syllable_inflection_columns, word_list_column, sonnet_num_list, author_list, polarity_list, subjectivity_list):
	    # Set up column names.
	    column_names = ['sonnet_index','syllables','s1','s2','s3','s4','s5',
	                    's6','s7','s8','s9','s10','s11','s12']
	    
	    # Turn the matrix into a DataFrame with the column names.
	    sonnet_df = pd.DataFrame(syllable_inflection_columns, columns=column_names)
	    sonnet_df['word_list'] = word_list_column
	    sonnet_df['sonnet_num'] = sonnet_num_list
	    sonnet_df['author'] = author_list
	    sonnet_df['polarity'] = polarity_list
	    sonnet_df['subjectivity'] = subjectivity_list
	    
	    return sonnet_df