import sys
import os
from optparse import OptionParser
import xml.etree.ElementTree as ET
from HTMLParser import HTMLParser
from sklearn.feature_extraction import DictVectorizer


gender_map = {"MALE" :0, "FEMALE":1}
age_map    = {"18-24":0, "25-34":1, "35-49":2, "50-64":3, "65-xx":4}

def parse_labels(string):
    _, gender, age, occupation, region, _ = string.split(".")
    #print (gender, int(age), occupation, region)
    return (gender, int(age), occupation, region)

def read_xml(xml_files, id2labels):
    # (gender, age)
    id2tweets = {}
    gender_count = {"MALE" :0, "FEMALE":0}
    age_count    = {"18-24":0, "25-34":0, "35-49":0, "50-64":0, "65-xx":0}
    for fxml in xml_files:
        fxml_base = os.path.basename(fxml)
        user_id = fxml_base.strip(".xml")
        # print "Processing User:", user_id
        tree = ET.parse(fxml)
        documents = tree.getroot().find("documents")
        all_tweets = []
        for doc in documents.findall("document"):
            tweet = doc.text
            if tweet is None: continue
            all_tweets.append(tweet)
        id2tweets[user_id] = all_tweets
        num_tweets  = len(all_tweets)
        gender, age = id2labels[user_id]
        gender_count[gender] += num_tweets
        age_count[age]       += num_tweets

    #for user in id2tweets:
    #    print user + ":", len(id2tweets[user])
    return id2tweets, gender_count, age_count

def read_truth(truth_file_path):
    id2labels = {}
    gender_count = {"MALE" :0, "FEMALE":0}
    age_count    = {"18-24":0, "25-34":0, "35-49":0, "50-64":0, "65-xx":0}
    fh = open (truth_file_path, "r")
    for line in fh:
        line = line.strip("\n")
        identity, gender, age = line.split(":::")
        gender_count[gender] += 1
        age_count[age] += 1
        id2labels[identity] = (gender, age)
    fh.close()
    return id2labels, gender_count, age_count

def main(options, truth_file_path, xml_dir):
    # input processing
    assert os.path.exists(xml_dir), "xml_data not exists."
    if os.path.isdir(xml_dir):
        xml_files = [ os.path.join(xml_dir,f) for f in os.listdir(xml_dir) \
                     if os.path.isfile(os.path.join(xml_dir,f)) and f[-4:] == ".xml" ]
    elif os.path.isfile(xml_dir):
        xml_files = [ xml_dir ]
    # read xml and truth file(s)
    print "=============> USER STATISTICS <=============="
    id2labels, gender_count, age_count = read_truth (truth_file_path)
    total_users = len(xml_files)
    for x in gender_count: print x, gender_count[x], 1.0*gender_count[x]/total_users
    for x in age_count: print x, age_count[x], 1.0*age_count[x]/total_users

    print "=============> TWEET STATISTICS <=============="
    id2tweets, gender_count, age_count = read_xml (xml_files, id2labels)
    total_tweets = sum( [len(x) for x in id2tweets.values()] )
    for x in gender_count: 
        print x, gender_count[x], 1.0*gender_count[x]/total_tweets
    for x in age_count: 
        print x, age_count[x], 1.0*age_count[x]/total_tweets

if __name__ == "__main__":
    usage = "usage: python preprocess.py (options) [truth_file] [xml_dir]"
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()
    if len(args) != 2: 
        parser.print_help()
        parser.error("Incorrect number of arguments.")
    truth_file_path = args[0]
    xml_dir = args[1]
    main(options, truth_file_path, xml_dir)
