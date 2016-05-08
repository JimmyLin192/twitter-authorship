import sys
import os
from optparse import OptionParser
from sklearn.feature_extraction import DictVectorizer

def parse_labels(string):
    _, gender, age, occupation, region, _ = string.split(".")
    print (gender, int(age), occupation, region)
    return (gender, int(age), occupation, region)


def strip(string):
    string = string.lower()
    for x in ["<blog>" "</blog>" "<date>" "</date>"]:
        if x in string:
            return None
    for x in '''*,.!?:()'{}#@$%^&"''':
        string = string.replace(x, " ")
    return string

def read_xml(xml_files):
    # (gender, age, occupation, blogs)
    for fxml in xml_files:
        freqCounts = {}
        labels = parse_labels(fxml.split("/")[-1])
        fxml_handle = open(fxml, "r")
        for line in fxml_handle:
            if len(line) <= 1: continue
            line = strip(line)
            if line is None: continue
            for word in line.split(" "):
                word = word.strip(" ")
                if len(word) <= 1: continue
                if word in freqCounts: freqCounts[word] += 1
                else: freqCounts[word] = 1

        print "for XML file:", fxml
        for word in freqCounts:
            print word + ":" + str( freqCounts[word])
        fxml_handle.close()


def main(options, in_filename, out_filename):
    assert os.path.exists(in_filename), "xml_data not exists."
    if os.path.isdir(in_filename):
        xml_files = [ in_filename+f for f in os.listdir(in_filename) \
                 if os.path.isfile(in_filename+f) and f[-4:] == ".xml" ]
    elif os.path.isfile(in_filename):
        xml_files = [in_filename]
    xml_data = read_xml (xml_files)


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
