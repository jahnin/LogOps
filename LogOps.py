'''
LogOps.py

List all events for a specified time period.
    Author: Jahnin Rajamoni(jrajamon@vmware.com)
    Copyright: 2019 VMware Australia
'''

import sys, os, re, gzip, glob
from optparse import OptionParser
from datetime import datetime

# Exit if Python 3 is not available
if int(sys.version[0]) != 3:
    print('Aborted: Python 3.x required')
    sys.exit(1)

print("\n")
print("██╗      ██████╗  ██████╗       ██████╗ ██████╗ ███████╗")
print("██║     ██╔═══██╗██╔════╝      ██╔═══██╗██╔══██╗██╔════╝")
print("██║     ██║   ██║██║  ███╗ ███ ██║   ██║██████╔╝███████╗")
print("██║     ██║   ██║██║   ██║     ██║   ██║██╔═══╝ ╚════██║")
print("███████╗╚██████╔╝╚██████╔╝     ╚██████╔╝██║     ███████║")
print("╚══════╝ ╚═════╝  ╚═════╝       ╚═════╝ ╚═╝     ╚══════╝\n")

# Globals
ignoreType_format = re.compile(r'(\.tar\.gz$)|(\.zip$)|(\.vmdk$)|(\.vmx$)|(\.dump$)|(\.dump.gz$)|(\.dmp$)|(\.core)') #do not process files with specific extensions
gz_format = re.compile(r'(\.gz)')
count = 0
check = 0
noMatch = ""
foundMatch = ""
filePath = ""
eventCheck = 0
notFound = 0

#Date patterns - add date patterns here
regex_format01 = re.compile(r'20\d{2}(-)((0[1-9])|(1[0-2]))(-)((0[1-9])|([1-2][0-9])|(3[0-1]))(T)(([0-1][0-9])|(2[0-3])):([0-5][0-9]):([0-5][0-9])')  # 2018-05-12T05:05:11
regex_format02 = re.compile(r'20\d{2}(-)((0[1-9])|(1[0-2]))(-)((0[1-9])|([1-2][0-9])|(3[0-1]))(\s)(([0-1][0-9])|(2[0-3])):([0-5][0-9]):([0-5][0-9])')  # 2018-05-12 05:05:11
regex_format03 = re.compile(r'((0[1-9])|([1-2][0-9])|(3[0-1]))(-)(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(-)(20\d{2})(\s)(([0-1][0-9])|(2[0-3])):([0-5][0-9]):([0-5][0-9])')  # 12-May-2018 05:05:11
regex_format04 = re.compile(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\s)((0[1-9])|([1-2][0-9])|(3[0-1]))(,)(\s)(20\d{2})(\s)(([0-1][0-9])|(2[0-3])):([0-5][0-9]):([0-5][0-9])') # May 12, 2018 05:05:11 AM
regex_format05 = re.compile(r'((0[1-9])|([1-2][0-9])|(3[0-1]))(\/)(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\/)(20\d{2})(:)(([0-1][0-9])|(2[0-3])):([0-5][0-9]):([0-5][0-9])')  # 12/May/2018:05:05:11
regex_format06 = re.compile(r'((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\s)((0[1-9])|([1-2][0-9])|(3[0-1]))(\s)(([0-1][0-9])|(2[0-3])):([0-5][0-9]):([0-5][0-9]))')  # May 12 05:05:11

#combined_format = re.compile(regex_format01.pattern + regex_format02.pattern + regex_format03.pattern + regex_format04.pattern + regex_format05.pattern + regex_format06.pattern)

# for date objects
compare_format = "%Y-%m-%d%H:%M:%S"
compare_format01 = "%Y-%m-%dT%H:%M:%S"  # 2018-05-12T05:05:11
compare_format02 = "%Y-%m-%d %H:%M:%S"  # 2018-05-12 05:05:11
compare_format03 = "%d-%b-%Y %H:%M:%S"  # 12-May-2018 05:05:11
compare_format04 = "%b %d, %Y %-I:%M:%S %p"  # May 12, 2018 05:05:11 AM
compare_format05 = "%d/%b/%Y:%H:%M:%S"  # 12/May/2018:05:05:11
compare_format06 = "%b %d %H:%M:%S"  # May 12 05:05:11



#Colors
green = "\033[1;32;40m"
red = "\033[1;31;40m"
whiteBold = "\033[1;37;40m"
white = "\033[0;37;40m"
highlight = "\033[1;37;44m"

# Function to check if a file is binary
def is_binary(file_name):
    try:
        if ignoreType_format.search(file_name):
            return True
        elif gz_format.search(file_name): #if file is gzipped
            gzf=gzip.open(file_name,'rt') 
            gzf.close()
            return False
        else:
            with open(file_name,'tr') as check_file:  # try open file in text mode
                check_file.read()
                check_file.close()
                return False
    except:
        return True

# Function to write dashes - cosmetic
def print_dashes(outStr):
    for p in range(len(outStr)):
        outFh.write("-")

# Function to process each file
def process_file(filePath):
    global count, check, noMatch, foundMatch, eventCheck, notFound
    if not is_binary(filePath) and filePath.find("LogOps-Output") < 0:
        try:
            if(gz_format.search(filePath)):
                fh = gzip.open(filePath, 'rt')
            else:
                fh = open(filePath, 'r')
        except:
            print("Error opening file: "+filePath)

        print(green+"--------------------", end="")
        for i in range(len(filePath)):
            print("-", end="")
        print("\n| Processing File:", filePath, "|")
        print("--------------------", end="")
        for i in range(len(filePath)):
            print("-", end="")
        print(white)
        
        #Extract date and time based on regex
        for line in fh:
            try:
                if regex_format01.search(line):
                    logDate = datetime.strptime(regex_format01.search(line).group(), compare_format01)
                    eventCheck = 0
                elif regex_format02.search(line):
                    logDate = datetime.strptime(regex_format02.search(line).group(), compare_format02)
                    eventCheck = 0
                elif regex_format03.search(line):
                    logDate = datetime.strptime(regex_format03.search(line).group(), compare_format03)
                    eventCheck = 0
                elif regex_format04.search(line):
                    logDate = datetime.strptime(regex_format04.search(line).group(), compare_format04)
                    eventCheck = 0
                elif regex_format05.search(line):
                    logDate = datetime.strptime(regex_format05.search(line).group(), compare_format05)
                    eventCheck = 0
                elif regex_format06.search(line):
                    logDate = datetime.strptime(regex_format06.search(line).group()+str(startDate.year), compare_format06+"%Y")
                else:
                    notFound = 1
                    logDate = datetime.now()

                #Print events if date/time is within specified time period.
                if startDate <= logDate <= endDate:
                    if check < 1:
                        outStr = "| Log File: "+filePath+" |"
                        for p in range(len(outStr)):
                            outFh.write("-")
                        outFh.write("\n"+outStr+"\n")
                        for p in range(len(outStr)):
                            outFh.write("-")
                        foundMatch = foundMatch+"\n"+filePath
                        check = 1
                    eventCheck = 1
                    outFh.write("\n"+line.rstrip())
                    print(line.rstrip())
                    count = count + 1
                
                #Print events that follow that do not have a timestamp.
                if eventCheck: 
                    if notFound:
                    #print("empty regex")
                        outFh.write("\n"+line.rstrip())
                        print(line.rstrip())
                notFound = 0
            except (ValueError, IndexError):
                pass
        if check == 1:
            outFh.write("\n\n")
            check = 0
        if count == 0:
            noMatch = noMatch+"\n"+filePath
            print(red+"NO MATCH FOUND"+white)
        count = 0
        print("\n\n")
        fh.close()

# Help Menu
usage_text = """\
usage: logOps --sdate YYYY-MM-DD --stime HH:MM:SS --edate YYYY-MM-DD --etime HH:MM:SS <File/DIR>

options:
  --sdate YYYY-MM-DD    Input Start Date in YYYY-MM-DD format
  --stime HH:MM:SS      Input Start Time in HH:MM:SS format
  --edate YYYY-MM-DD    Input End Date in YYYY-MM-DD format
  --etime HH:MM:SS      Input End Time in HH:MM:SS format
  <File/DIR>            Specify file/diretory containing files
  --help -h             Show this help message and exit

Example: logOps --sdate 2019-06-03 --stime 10:00:00 --edate 2019-06-04 --etime 14:00:00 var/run/log/
"""
error_text = red+"\nMissing input parameters. Review arguments and check date/time format\n\n"+white

# Exit if script is called without all arguments
if len(sys.argv) < 9 or "-h" in sys.argv or "--help" in sys.argv:
    if len(sys.argv) > 2:
        sys.stderr.write(error_text)
    #parser.print_help(sys.stderr)
    sys.exit(usage_text)

parser = OptionParser()
parser.add_option("--sdate", action="store", default=None, dest="start_Date")
parser.add_option("--stime", action="store", default=None, dest="start_Time")
parser.add_option("--edate", action="store", default=None, dest="end_Date")
parser.add_option("--etime", action="store", default=None, dest="end_Time")
(options, args) = parser.parse_args()



# Define Date and Time format and check format
date_format = "%Y-%m-%d"
time_format = "%H:%M:%S"

sdate = options.start_Date
edate = options.end_Date
stime = options.start_Time
etime = options.end_Time

try:
    startDate = datetime.strptime(sdate, date_format)
    endDate = datetime.strptime(edate, date_format)
    startTime = datetime.strptime(stime, time_format)
    endTime = datetime.strptime(etime, time_format)
except:
    sys.stderr.write(red+"\nInvalid Date/Time Format. Please review input parameters.\n\n"+white)
    sys.exit(usage_text)

#Start and End Date from user input
startDate = datetime.strptime(sdate+stime, compare_format)
endDate = datetime.strptime(edate+etime, compare_format)

if endDate < startDate:
    sys.stderr.write(red+"\nStart date/time is invalid or occurs after end date/time. Please review input parameters.\n\n"+white)
    sys.exit(usage_text)

print(whiteBold+"\n\nFinding events from "+highlight+"Date:", sdate,"Time:", stime, whiteBold+" to "+highlight+"Date:", edate,"Time:", etime, whiteBold+"\n"+white)

# Get path. Its a list if wildcards are used.
userDir = sys.argv[9:]
if not userDir:
    userDir = ["."]

# Create file for output
try:
    fileName = str("LogOps-Output-"+str(datetime.now().time())+".txt")
    outFh = open(fileName, "w+")
except:
    sys.stderr.write("Unable to create output file:", fileName)

#outStr = "LogOps.py: Listing events from all files under "+workingDir+" from "+sdate+" "+stime+" to "+edate+" "+etime+" ..."
outStr = "logOps: Listing events from "+sdate+" "+stime+" to "+edate+" "+etime+" ..."
outFh.write(outStr+"\n")
outFh.write("\n")

# Process files and directories
for path in userDir:
    if os.path.isfile(path):
        process_file(path)
    else:
        for dirpath, subdirs, files in os.walk(path):
            for file in files:
                process_file(str(os.path.join(dirpath, file)))
                
#list files that do not contain log entries
if noMatch != "":
    print(highlight+"There are no log entries between", sdate, stime, "and", edate, etime, "in the following log files:"+white+"\n", noMatch)

#list files that contain log entries
if foundMatch != "":
    print("\n"+highlight+"The following logs contain events between "+sdate+" "+stime+" and "+edate+" "+etime+" "+white,foundMatch+"\n")

if noMatch == "" and foundMatch == "":
    print(red+"NO MATCH FOUND\n"+white)
 
# Write events to output file 
outStr = "The following logs contain events between "+sdate+" "+stime+" and "+edate+" "+etime+":"
outFh.write("\n"+outStr+"\n")
print_dashes(outStr)
outFh.write(foundMatch)
outStr = "There are no events between "+sdate+" "+stime+" and "+edate+" "+etime+" in the following log files:"
outFh.write("\n\n"+outStr+"\n")
print_dashes(outStr)
outFh.write(noMatch)
outFh.close()
