liblinear_template = '''
##################################################################
universe = vanilla

Initialdir = /u/jimmylin/workspace/twitter-authorship/codebases
Executable = ../libraries/liblinear-2.1/train

+Group   = "GRAD"
+Project = "INSTRUCTIONAL"
+ProjectDescription = "CS388 Final Project"

Log = %(log_path)s/%(name)s.log

Notification = complete
Notify_user = jimmylin@utexas.edu

Arguments = -s %(s)d -c 1e%(c)d -e 1e%(e)d -v 10 -q raw_features_scale 

Output = %(log_path)s/%(name)s.result
Error  = %(log_path)s/%(name)s.err
Queue 1

'''

libsvm_template = '''
##################################################################
universe = vanilla

Initialdir = /u/jimmylin/workspace/twitter-authorship/codebases
Executable = ../libraries/libsvm-3.21/svm-train

+Group   = "GRAD"
+Project = "INSTRUCTIONAL"
+ProjectDescription = "CS388 Final Project"

Log = %(log_path)s/%(name)s.log

Notification = complete
Notify_user = jimmylin@utexas.edu

Arguments = -s %(s)d -c 1e%(c)d -e 1e%(e)d -v 10 -q raw_features_scale 

Output = %(log_path)s/%(name)s.result
Error  = %(log_path)s/%(name)s.err
Queue 1

'''

def generate_liblinear_condor():
    string = ""
    param = {"log_path": "../results/scaled"}
    for s in range(8):
        param["s"] = s
        for c in range(-1, 2):
            param["c"] = c
            for e in range(-7, -2):
                param["e"] = e
                param["name"] = "_s%d_c%d_e%d" % (s,c,e)
                string += liblinear_template % param
    print string

def generate_libsvm_condor():
    string = ""
    param = {"log_path": "../results/libsvm"}
    for s in range(2):
        param["s"] = s
        for c in range(-1, 2):
            param["c"] = c
            for e in range(-7, -2, 2):
                param["e"] = e
                for t in range(4):
                    param["t"] = t
                    param["name"] = "_s%d_t%d_c%d_e%d" % (s,t,c,e)
                    string += libsvm_template % param
    print string


if __name__ == "__main__":
    generate_libsvm_condor()
