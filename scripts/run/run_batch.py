import optparse
import glob
import sys
import os
import subprocess
import datetime

def kill(proc_pid):
    process = psutil.Process(proc_pid)
    print(process)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()
		
if __name__=="__main__":
    # Options
    parser = optparse.OptionParser()
    parser.add_option("-m", "--mitsuba", help="the mitsuba .sh or MTS executable")
    parser.add_option('-t','--technique', help='technique name', default=[], action="append")
    parser.add_option('-s','--time', help='time of running (in sec)', default=None)
    parser.add_option('-i','--input', help='input scene name (%path_scene%_%tech%.xml)')
    parser.add_option('-o','--output', help='output directory')
    parser.add_option('-j','--jobs', help='nb thread per jobs', default=12)
    parser.add_option('-A','--automatic', help='replace -t usage by finding all files', default=False, action="store_true")
    (options, args) = parser.parse_args()

    # === Error handling
    if(options.input == None):
        print("\nError: Need input values\n")
        parser.print_help()
        sys.exit(1)
    if(options.output == None):
        print("\nError: Need output values\n")
        parser.print_help()
        sys.exit(1)
    if(options.time == None):
        print("\nError: Need to specify time\n")
        parser.print_help()
        sys.exit(1)

    print("Techniques input: ", options.technique)
        
    # === Create output directory
    if(not os.path.exists(options.output)):
        os.makedirs(options.output)

    # List all files we need to render
    # Note that if automatic mode is used. Manually input techniques are not taken into account
    if(len(options.technique) != 0 and options.automatic):
        print(""""[WARN] Automatic mode and manually technique input is detected.
        Just ignore manual input and usefully automatic detection""")

    # Technique array will store all techniques names
    techniques = []
    if(options.automatic):
        print(" === Automatic finding ...")
        files = glob.glob(options.input+"*.xml")
        for fileXML in files:
            filename = os.path.basename(fileXML)
            filenameRoot = os.path.basename(options.input)
            tech = filename[len(filenameRoot)+1:-4]
            print("   * Find: %s" % tech)
            techniques.append(tech)
    else:
        # If we use manual, just copy technique names
        for tech in options.technique:
            techniques.append(tech.strip())

    dateStart = datetime.datetime.now()
    dateEnd = dateStart + datetime.timedelta(seconds=int(options.time)*len(techniques))
    for tech in techniques:
        print("[INFO] End of rendering tasks: ", "{:%H:%M}".format(dateEnd))
        command = [options.mitsuba, "-p", str(options.jobs)]
        # Add output
        command += ["-o", options.output + os.path.sep + tech]
        # Add input
        command += [options.input + "_" + tech + ".xml"]

        print("[DEBUG] Run computation for", tech)
        # Start foo as a process
        try:
            proc = subprocess.check_output(command, shell=False, timeout=int(options.time))
        except subprocess.TimeoutExpired:
            #proc.kill()
            print("Process killed :)")
