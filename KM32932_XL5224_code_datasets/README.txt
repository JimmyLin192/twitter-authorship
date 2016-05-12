CS 388 Project: 
    Authorship Identification in Age and Gender
===================================

Student I
Name: Keyon Mohebzad
EID: KM32932
Email: mrmooshy2@gmail.com

Student II
Name: Xin Lin
EID:  XL5224
Email: linxin@gmail.com


Repository
---------------------------------

pan16-author-profiling-training-dataset     Raw dataset with user information
pan16-author-profiling-twitter-downloader   twitter downloader for user information


preprocess.py   Feature extraction
get_stats.py    Explore the dataset
condor_generator.py  Condor task description generator

libraries/liblinear-2.1
libraries/libsvm-3.21
libraries/nltk_data 

Usage 
---------------------------------

0. Use tweets downloader to acquire XML with tweets corpus

    java -jar TwitterDownloader.jar -data path_to_dataset

1. get statistics of age and gender distribution

    python get_stats.py [truth.txt] [xml_dir]

statistics will be output to stdout.

2. get extracted feature from PAN-16 dataset

    python preprocess.py [truth.txt] [xml_dir] [out_features]

3. run liblinear (also see codebases/gender.linear.condor)

    train -s $s -c $c -e $e [input_features] (model_file)

4. run svm scaling
    
    svm-scale -l 0 [unscaled_input] > [scaled_output]
