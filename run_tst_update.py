
from glob import glob
import sys
import subprocess
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import shutil
import platform
import time
import string
# from string import replace
from datetime import datetime
import json

#====================================================
testsuite_directory = []
sender_on_windows = 'ns_gui_regression@intel.com'

cc_mail1 = "nani.subramanian@intel.com,sangx.phan@intel.com"
to_addr1 = "maix.tan@intel.com"
cc_mail0 = ""
to_addr0 = "maix.tan@intel.com"
cc_mail2 = ""
to_addr2 = "tan.mai@terralogic.com"
recipient=""

os.environ["DISPLAY"] = ":1.0"
platforms = {"Windows": "Windows", "Linux": "Linux"}
os_system = platform.system()
thisdir = os.getcwd()

def run_test(build_version=""):
    base_test_directory = os.path.dirname(os.path.realpath(__file__)) + "/"
    if "\\" in base_test_directory:
        base_test_directory = string.replace(base_test_directory, "\\", "/")
    
    total_tsuite = 0
    total_tscase = 0
    tscase_errors = []
    
    args = sys.argv
    for i in range(2, len(args)):
        if os_system == platforms["Linux"]:
            bash_command = "find " + base_test_directory + " -name *" + args[i] + "*"
            process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
            output = process.communicate()[0]
            out_arrs = output.strip().split("\n")
        else:
            os.chdir(base_test_directory)
            bash_command = "dir *" + args[i] + "* /b/s"
            process = subprocess.Popen(bash_command.split(), shell=True, stdout=subprocess.PIPE)
            output = process.communicate()[0]
            temp = output.strip().split("\r\n")
            out_arrs = []
            for i in temp:
                if "\\" in i:
                    i = string.replace(i, "\\", "/")
                out_arrs.append(i)

        existing = {}
        for i in out_arrs:
            dir_abspath = os.path.abspath(i)
            if "\\" in dir_abspath:
                dir_abspath = string.replace(dir_abspath, "\\", "/")
            pattern = base_test_directory + "([^/]+)/.+"
            rs = re.findall(pattern, dir_abspath)
            if len(rs) == 0:
                continue
            tssuite_dir = base_test_directory + re.findall(pattern, dir_abspath)[0] + "/"
            if tssuite_dir in existing:
                item = existing[tssuite_dir]
            else:
                testsuite_directory.append(tssuite_dir)
                existing[tssuite_dir] = len(out_arrs) - 1

    if len(testsuite_directory) == 0:
        return 
    
    start_squish_server()
    testsuite_directory.sort()
    start_time = time.time()
    
    if os.path.exists("html_report"):
        shutil.rmtree("html_report")
    os.mkdir("html_report")

    for d in (testsuite_directory):
        source_file ="C:\\Users\\maitanx\\backup_ini\\NocStudio.ini"
        destination_folder ="C:\\Users\\maitanx\\.NetSpeed\\"
        shutil.copy2(source_file, destination_folder)
        print "in folder + " + d + "\n"
        total_tsuite += 1
        bash_command = "squishrunner --debugLog alpw --port 4322 --testsuite " + d + " --reportgen html,html_report"
        print "begin execute testsuite"
        if os_system == platforms["Linux"]:
            process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
            print "processing data"
        else:            
            process = subprocess.Popen(bash_command.split(), shell=True, stdout=subprocess.PIPE)
            print "processing data"
        process.communicate()[0]
        time.sleep(5)
          
    temp = (time.time() - start_time) / 3600
    elapsed_time = float("{0:.2f}".format(temp))
 
    current_date = datetime.now()
    temp = str(current_date).split()
    current_day = string.replace(temp[0], "-", "_")
    current_time = string.replace(temp[1].split(".")[0], ":", "_")
    total_tscase = getTotalTestcase()
    tscase_errors = getTestcaseErrors()
    week = int(datetime.today().strftime("%W")) + 1
    if week < 10:
        weekReport = "0" + str(week)
    else: 
        weekReport = str(week)
    report_link = "\\\\samba.zsc11.intel.com\\nfs\\site\\proj\\CFG\\scratch2\\tanmaix\\report\\" + str(datetime.today().year) + "\\" + "week"  + str(weekReport)
    os.system("xcopy html_report " + report_link  + " /E/H/C/I")

    subject = "GUI Automation Test Report W" + str(weekReport) + "." + str(datetime.today().year)
    content = ""
    content += 'This is the automation test report for NocStudio this week. \n'
    content +="\n";
    content += "Total Test cases: " + str(total_tscase) + "\n"
    content += "Total Time: " + str(elapsed_time) + "(h)\n"
    content += "Failed Test cases: " + str(len(tscase_errors)) + "\n"
    content += "Commit ID: " + str(build_version) + "\n"
    content +="\n";
    content += 'Please click below link to read more details: \n'
    content += "file:///" + report_link + "\\index.html" + "\n"
    
    #Check if fail test cases >50, don't sent email
    fail_tcs = len(tscase_errors)
    if fail_tcs > 50:
        send_mail(to_addr=to_addr2, cc_mail=cc_mail2, subject=subject, content=content, file_location="")
        send_mail(to_addr=to_addr0, cc_mail=cc_mail0, subject=subject, content=content, file_location="")
    else:
        send_mail(to_addr=to_addr1, cc_mail=cc_mail1, subject=subject, content=content, file_location="")
        send_mail(to_addr=to_addr2, cc_mail=cc_mail2, subject=subject, content=content, file_location="")
    
    shutil.rmtree("html_report")
    
    # stop squishServer
    stop_squish_server()

def start_squish_server():
    bash_command = "squishserver --port 4322"
    if os_system == platforms["Linux"]:    
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    else:
        process = subprocess.Popen(bash_command.split(), shell=True, stdout=subprocess.PIPE)
    
    return process.returncode

def stop_squish_server():
    bash_command = "squishserver --stop"
    if os_system == platforms["Linux"]:
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    else:
        process = subprocess.Popen(bash_command.split(), shell=True, stdout=subprocess.PIPE)
    
    return process.returncode

def send_mail(to_addr="", cc_mail="", subject="Netspeed", content="Auto", file_location=""):
    if os_system == platforms["Linux"]:
        bash_command = ["mail", "-s", subject, recipient]
        try:
            process = subprocess.Popen(bash_command, stdin=subprocess.PIPE)
        except Exception, error:
            print error
        process.communicate(content)
    else:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_on_windows
        msg['To'] = to_addr
        msg['CC'] = cc_mail
        recipient = to_addr.split(",") + cc_mail.split(",")
        
        msg.attach(MIMEText(content, 'plain'))

        if file_location != "":
            filename = os.path.basename(file_location)
            attachment = open(file_location, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
            msg.attach(part)
        s = smtplib.SMTP('smtp.intel.com')
        s.sendmail(sender_on_windows, recipient, msg.as_string())
        s.quit()
    print "sent sucessfully!"

def getTotalTestcase():
    total_tst = 0
    for d in (testsuite_directory):
        for test in os.listdir(d):
            if test.startswith("tst_"):
                total_tst += 1
    return total_tst

def getTestcaseErrors():
    tstcase_errors = []
    data = []
    f = open(thisdir + "\\html_report\\data\\results-v1.js", "r")
    content = f.read().strip('\n')
    content = content.lstrip("var data = [];\ndata.push( ").rstrip(");")
    content_json = content.replace("data.push(", "").replace(");", ",\n");
    data = json.loads("[" + content_json + "]")

    for suites in data:
        for suite_data in suites["tests"]:
            for tst_data in suite_data["tests"]:
                if tst_data["type"] == "testcase":
                    tst_data_str = str(tst_data)
                    if "u'result': u'ERROR'" in tst_data_str or "u'result': u'FAIL'" in tst_data_str or "u'result': u'FATAL'" in tst_data_str:
                        tstcase_errors.append(tst_data["name"])
    f.close
    return tstcase_errors

def help():
    print "usage:"
    print "python2 run_tst_update.py <build-version> <suite-filter>*"
    print ""
    print "Ex:"
    print "python2 run_tst_update.py cfg_turnin41233 bdd_test"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        help()
        exit
    if not sys.argv[1].startswith("cfg_turnin"):
        help()
        exit
    run_test(sys.argv[1])
