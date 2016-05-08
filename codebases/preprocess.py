import sys
import os
from optparse import OptionParser
from sklearn.feature_extraction import DictVectorizer

def parse_labels(string):
    _, gender, age, occupation, region, _ = string.split(".")
    #print (gender, int(age), occupation, region)
    return (gender, int(age), occupation, region)

def isInt_try(v):
    try:     i = int(v)
    except:  return False
    return True

to_remove = ["<blog>" "</blog>" "<date>" "</date>"]

def strip(string):
    string = string.lower()
    for x in to_remove:
        if x in string:
            return None
    for x in '''*,.!?:()-+\/'{}#@$%^&"''':
        string = string.replace(x, " ")
    return string

def read_xml(xml_files):
    # (gender, age, occupation, blogs)
    freqCounts = {}
    for fxml in xml_files:
        labels = parse_labels(fxml.split("/")[-1])
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

def read_truth(truth_file_path):
    labels_map = {}
    gender_map = {"MALE" :0, "FEMALE":1}
    age_map    = {"18-24":0, "25-34":1, "35-49":2, "50-64":3, "65-xx":4}
    fh = open (truth_file_path, "r")
    for line in fh:
        line = line.strip("\n")
        identity, gender, age = line.split(":::")
        gender, age = gender_map[gender], age_map[age]
        labels_map[identity] = (gender, age)
    fh.close()
    return labels_map

def main(options, in_filename, out_filename):
    assert os.path.exists(in_filename), "xml_data not exists."
    '''
    if os.path.isdir(in_filename):
        xml_files = [ in_filename+f for f in os.listdir(in_filename) \
                 if os.path.isfile(in_filename+f) and f[-4:] == ".xml" ]
    elif os.path.isfile(in_filename):
        xml_files = [in_filename]
    xml_data = read_xml (xml_files)
    '''
    labels_map = read_truth(in_filename)
    for x in labels_map:
        print x, labels_map[x]


if __name__ == "__main__":
    usage = "usage: python preprocess.py (options) [xml_data] [out_file]"
    parser = OptionParser(usage=usage)
    parser.add_option("-b", "--bags-of-words", action="store_true", dest="BOG", \
                      default=False, help="option to turn on bags-of-words feature representation.")
    parser.add_option("-t", "--tf-idf", action="store_true", dest="TF_IDF", \
                      default=False, help="option to turn on loop tiling.")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help="verbose")
    parser.add_option("", "--mini", action="store_true", dest="mini", help="mini")
    (options, args) = parser.parse_args()
    if len(args) != 2: 
        parser.print_help()
        parser.error("Incorrect number of arguments.")
    in_filename = args[0]
    out_filename = args[1]
    main(options, in_filename, out_filename)
