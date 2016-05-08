import sys
import os
from optparse import OptionParser
import xml.etree.ElementTree as ET
from HTMLParser import HTMLParser
from sklearn.feature_extraction import DictVectorizer

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
    id2localFreq = {}
    for user_id in id2tweets:
        all_tweets = id2tweets[user_id]
        local_freq = {}
        for tweet in all_tweets:
            tweet = strip(tweet)
            words = tweet.split(" ")
            for word in words:
                word = word.strip(" ")
                if not is_word_all_character(word): continue
                if len(word) <= 1 or len(word) > 20: continue
                if isInt_try(word): continue
                #
                if word in freqCounts: freqCounts[word] += 1
                else: freqCounts[word] = 1
                if word in local_freq: local_freq[word] += 1
                else: local_freq[word] = 1
        #
        id2localFreq[user_id] = local_freq
    #
    return freqCounts, id2localFreq

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

    freqCounts, id2localFreq = get_freq_counts (id2tweets)
    word2index, index = {}, 1
    for word in freqCounts:
        word2index.update({word:index})
        index += 1
    # get unigram features
    
    out_handle = open(out_filename, "w+")
    for user_id in id2localFreq: 
        instance_str = str(id2labels[user_id][0])
        local_freq = id2localFreq[user_id]
        for word in local_freq:
            instance_str += " %d:%d" % (word2index[word], local_freq[word])
        #
        out_handle.writelines([instance_str, "\n"])
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
