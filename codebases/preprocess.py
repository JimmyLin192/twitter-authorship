import sys
import os
from optparse import OptionParser
import xml.etree.ElementTree as ET
from HTMLParser import HTMLParser
#from sklearn.feature_extraction import DictVectorizer
import nltk
from nltk.corpus import words as word_list
#from nltk.corpus import opinion_lexicon
from collections import Counter
from math import log

def parse_labels(string):
    _, gender, age, occupation, region, _ = string.split(".")
    #print (gender, int(age), occupation, region)
    return (gender, int(age), occupation, region)

def isInt_try(v):
    try:     i = int(v)
    except:  return False
    return True

def strip(string):
    string = string.lower()
    for x in '''*,.!?:()-+\/'{}[]#@$%^&"''':
        string = string.replace(x, " ")
    return string

def is_word_all_character (string):
    # check if all character is a letter
    for x in string:
        if not x.isalpha(): 
            return False 
    return True

'''
def read_xml(xml_files):
    # (gender, age, occupation, blogs)
    freqCounts = {}
    for fxml in xml_files:
        #labels = parse_labels(fxml.split("/")[-1])
        fxml_handle = open(fxml, "r")
        for line in fxml_handle:
            if len(line) <= 1: continue
            line = strip(line)
            if line is None: continue
            for word in line.split(" "):
                word = word.strip(" ")
                if len(word) <= 1: continue
                if isInt_try(word): continue
                if word in freqCounts: freqCounts[word] += 1
                else: freqCounts[word] = 1
        fxml_handle.close()
        #print "for XML file:", fxml
    for word in freqCounts:
        print word + ":" + str( freqCounts[word])
'''
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def read_xml(xml_files):
    # (gender, age)
    id2tweets = {}
    for fxml in xml_files:
        fxml_base = os.path.basename(fxml)
        user_id = fxml_base.strip(".xml")
        print "Processing User:", user_id
        tree = ET.parse(fxml)
        documents = tree.getroot().find("documents")
        all_tweets = []
        for doc in documents.findall("document"):
            tweet = doc.text
            if tweet is None: continue
            s = MLStripper()
            s.feed(tweet)
            tweet = s.get_data()
            all_tweets.append(tweet)
        id2tweets[user_id] = all_tweets

    #for user in id2tweets:
    #    print user + ":", len(id2tweets[user])
    return id2tweets

def read_truth(truth_file_path):
    id2labels = {}
    gender_map = {"MALE" :0, "FEMALE":1}
    age_map    = {"18-24":0, "25-34":1, "35-49":2, "50-64":3, "65-xx":4}
    fh = open (truth_file_path, "r")
    for line in fh:
        line = line.strip("\n")
        identity, gender, age = line.split(":::")
        gender, age = gender_map[gender], age_map[age]
        id2labels[identity] = (gender, age)
    fh.close()
    return id2labels

def get_freq_counts (id2tweets):
    freqCounts = {}
    posfreqCounts = {}
    extrafreqCounts = {'OOV':0, '7letter':0, 'wordcnt':0}
    id2localFreq = {}
    id2posFreq = {}
    id2extraFreq = {}
    for user_id in id2tweets:
        all_tweets = id2tweets[user_id]
        all_tweets_freqs = []
        all_tweets_posfreqs = []
        all_tweets_extrafreqs = []
        for tweet in all_tweets:        
            
            extra_freq = {'OOV':0, '7letter':0, 'wordcnt':0}
            
            tokens = nltk.word_tokenize(tweet)
            tagged = nltk.pos_tag(tokens)
            pos_freqs = Counter(tag for word,tag in tagged)
            
            for tag in pos_freqs:
                if tag in posfreqCounts: posfreqCounts[tag] += pos_freqs[tag]
                else: posfreqCounts[tag] = pos_freqs[tag]
            
            local_freq = {}
            tweet = strip(tweet)
            words = tweet.split(" ")
            
            extra_freq['wordcnt'] += len(words)
            extrafreqCounts['wordcnt'] += len(words)
            
            for word in words:
                word = word.strip(" ")
                
                if len(word)>6:
                    extra_freq['7letter'] += 1
                    extrafreqCounts['7letter'] += 1
                
                if word not in word_list.words():
                    extra_freq['OOV'] += 1
                    extrafreqCounts['OOV'] += 1

                if not is_word_all_character(word): continue
                if len(word) <= 1 or len(word) > 20: continue
                if isInt_try(word): continue
                #
                if word in freqCounts: freqCounts[word] += 1
                else: freqCounts[word] = 1
                if word in local_freq: local_freq[word] += 1
                else: local_freq[word] = 1
            #
            all_tweets_freqs.append(local_freq)
            all_tweets_posfreqs.append(pos_freqs)
            all_tweets_extrafreqs.append(extra_freq)
        id2localFreq[user_id] = all_tweets_freqs
        id2posFreq[user_id] = all_tweets_posfreqs
        id2extraFreq[user_id] = all_tweets_extrafreqs
    #
    return freqCounts, id2localFreq, posfreqCounts, id2posFreq, extrafreqCounts, id2extraFreq

def get_string (word):
    return u''.join((word,":")).encode('utf-8').strip()

def main(options, truth_file_path, xml_dir, out_filename):
    # input processing
    assert os.path.exists(xml_dir), "xml_data not exists."
    if os.path.isdir(xml_dir):
        xml_files = [ os.path.join(xml_dir,f) for f in os.listdir(xml_dir) \
                     if os.path.isfile(os.path.join(xml_dir,f)) and f[-4:] == ".xml" ]
    elif os.path.isfile(xml_dir):
        xml_files = [ xml_dir ]

    # read xml and truth file(s)
    id2tweets = read_xml (xml_files)
    id2labels = read_truth (truth_file_path)

    freqCounts, id2localFreq, posfreqCounts, id2posFreq, extrafreqCounts, id2extraFreq = get_freq_counts (id2tweets)
    
    
    age_category = [0, 0, 0, 0, 0]
    word_category = {} #{(word:[c0 c1 c2 c3 c4])}
    
    for user_id in id2localFreq:
        age = id2labels[user_id][1]    
        for tweet in id2localFreq[user_id]:
            for word in tweet:
                age_category[age] += tweet[word]
                if word in word_category: word_category[word][age] += tweet[word]
                else:
                    cat = [0, 0, 0, 0, 0]
                    cat[age] = tweet[word]
                    word_category[word] = cat
        
    ig = {}
    total_words = 0
    for word in freqCounts:
        total_words += freqCounts[word]
    
    for word in word_category:
        sum = 0.0;
        p_t = freqCounts[word]/total_words
        p_not_t = 1 - p_t
        for i in range(5):
            p = age_category[i]/total_words
            sum -= p*log(p)
            p2 = word_category[word][i]/freqCounts[word]
            sum += p_t*p2*log(p2)
            p3 = (age_category[i]-word_category[word][i])/(total_words-freqCounts[word])
            sum += p_not_t*p3*log(p3)
        ig[word] = sum
        
    sorted_ig = sorted(ig.items(),key=lambda x: -x[1])
    
    # get unigram features
    word2index, index = {}, 1
    for word in sorted_ig:
        if index == 1001: #only use the top 1000 unigrams based on information gain
            break
        word2index.update({word:index})
        index += 1
    
    for word in sorted_ig:
        print(word,': ',str(sorted_ig[word]),'\n')
    
    # get unigram pos features  
    tag2index = {}
    for tag in posfreqCounts:
        tag2index.update({tag:index})
        index += 1
    
    # get other features  
    feat2index = {}
    for feat in extrafreqCounts:
        feat2index.update({feat:index})
        index += 1
    
    
    out_handle = open(out_filename, "w+")
    for user_id in id2localFreq: 
        all_tweets_freqs = id2localFreq[user_id]
        all_tweets_posfreqs = id2posFreq[user_id]
        all_tweets_extrafreqs = id2extraFreq[user_id]
        
        tweet_count = 0
        instance_str = [None] * len(all_tweets_freqs)
        for tweet_freq in all_tweets_freqs:
            pairs = []
            for word in tweet_freq:
                if word in word2index:
                    pairs.append((word2index[word], tweet_freq[word]))
            pairs.sort(key=lambda x: x[0])
            instance_str[tweet_count] = str(id2labels[user_id][1])
            for index,value in pairs: instance_str[tweet_count] += " %d:%d" % (index, value)
            tweet_count = tweet_count + 1
            
        tweet_count = 0
        for pos_freq in all_tweets_posfreqs:
            pairs = []
            for tag in pos_freq:
                pairs.append((tag2index[tag], pos_freq[tag]))
            pairs.sort(key=lambda x: x[0])
            #instance_str[tweet_count] = str(id2labels[user_id][1])
            for index,value in pairs: instance_str[tweet_count] += " %d:%d" % (index, value)
            tweet_count = tweet_count + 1
            
        tweet_count = 0
        for extra_freq in all_tweets_extrafreqs:
            pairs = []
            for feat in extra_freq:
                pairs.append((feat2index[feat], extra_freq[feat]))
            pairs.sort(key=lambda x: x[0])
            #instance_str[tweet_count] = str(id2labels[user_id][1])
            for index,value in pairs: instance_str[tweet_count] += " %d:%d" % (index, value)
            tweet_count = tweet_count + 1
            
        for s in instance_str:
            out_handle.writelines([s, "\n"])
            
    out_handle.close()

if __name__ == "__main__":
    usage = "usage: python preprocess.py (options) [truth_file] [xml_dir] [out_file]"
    parser = OptionParser(usage=usage)
    parser.add_option("-b", "--bags-of-words", action="store_true", dest="BOG", \
                      default=False, help="option to turn on bags-of-words feature representation.")
    parser.add_option("-t", "--tf-idf", action="store_true", dest="TF_IDF", \
                      default=False, help="option to turn on loop tiling.")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help="verbose")
    parser.add_option("", "--mini", action="store_true", dest="mini", help="mini")
    (options, args) = parser.parse_args()
    if len(args) != 3: 
        parser.print_help()
        parser.error("Incorrect number of arguments.")
    truth_file_path = args[0]
    xml_dir = args[1]
    out_filename = args[2]
    main(options, truth_file_path, xml_dir, out_filename)
