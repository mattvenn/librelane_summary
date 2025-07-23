#!/usr/bin/env python3

import argparse
import pprint
import json
import os
import glob
import csv
import sys
import re
from shutil import which, copyfile, copytree
import datetime

def is_tool(name):
    return which(name) is not None

def check_path(path):
    paths = glob.glob(path)
    if len(paths) == 0:
        exit("ERROR: file not found: %s" % path)
    if len(paths) > 1:
        print("Warning: glob pattern found too many files, using first one: %s" % paths[0])
    
    return paths[0]

def openlane_date_sort(e):
    datestamp = os.path.basename(e)
    if re.match(r'^RUN_\d+.\d+.\d+\_\d+\.\d+\.\d+$',datestamp):
        datestamp = datestamp.replace('RUN_', '')
        timestamp = datetime.datetime.strptime(datestamp, '%Y.%m.%d_%H.%M.%S')
        return timestamp.timestamp()

    elif re.match(r'^\d+\-\d+\_\d+\-\d+$',datestamp):
            timestamp = datetime.datetime.strptime(datestamp, '%d-%m_%H-%M')
            return timestamp.timestamp()

    return -1

def summary_report(summary_file):
    # print short summary of the csv file
    status = None
    with open(summary_file) as fh:
        summary = csv.DictReader(fh)
        for row in summary:
            key = row["Metric"]
            value = row["Value"]
            if "violation" in key or "error" in key:
                print(f"{key:>70} : {value:>20}")

def full_summary_report(summary_file):
    # print short summary of the csv file
    with open(summary_file) as fh:
        summary = csv.DictReader(fh)
        for row in summary:
            key = row["Metric"]
            value = row["Value"]
            print(f"{key:>70} : {value:>20}")
                    
def drc_report(drc_file):
    last_drc = None
    drc_count = 0
    with open(drc_file) as drc:
        for line in drc.readlines():
            print(line.strip())

def antenna_report(antenna_report):
    violations = 0
    with open(antenna_report) as ant:
        for line in ant.readlines():
            m = re.match(r'\s+(PAR|CAR):\s+(\d+.\d+)\*\s+Ratio:\s+(\d+.\d+)', line)
            if m is not None:
                violations += 1
                violation = float(m.group(2))
                ratio = float(m.group(3))
                if violation > (ratio * 2):
                    print(line.strip(), ": worth fixing")
                else:
                    print(line.strip(), ": can ignore")

    if violations == 0:
            print("no antenna violations found")
    if violations > 0:
        print("For more info on antenna reports see https://www.zerotoasiccourse.com/terminology/antenna-report/")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="LibreLane summary tool")

    # or show standard cells
    parser.add_argument('--show-sky130', help='show all standard cells', action='store_const', const=True)

    parser.add_argument('--runs', help="where the design runs directory is", action='store')
    # optionally choose different name for top module and which run to use (default latest)
    parser.add_argument('--run', help="choose a specific run. If not given use latest. If not arg, show a menu", action='store', default=-1, nargs='?', type=int)

    # what to show
    parser.add_argument('--drc', help='show DRC report', action='store_const', const=True)
    parser.add_argument('--summary', help='show violations, area & status from summary report', action='store_const', const=True)
    parser.add_argument('--full-summary', help='show the full summary report csv file', action='store_const', const=True)
    parser.add_argument('--synth', help='show post techmap synth', action='store_const', const=True)
    parser.add_argument('--yosys-report', help='show cell usage after yosys synth', action='store_const', const=True)
    parser.add_argument('--antenna', help='find and list any antenna violations', action='store_const', const=True)

    parser.add_argument('--floorplan', help='show floorplan', action='store_const', const=True)
    parser.add_argument('--pdn', help='show PDN', action='store_const', const=True)
    parser.add_argument('--global-placement', help='show global placement PDN', action='store_const', const=True)
    parser.add_argument('--detailed-placement', help='show detailed placement', action='store_const', const=True)
    parser.add_argument('--gds', help='show final GDS', action='store_const', const=True)

    args = parser.parse_args()

    if not 'PDK_ROOT' in os.environ:
        exit("please set PDK_ROOT to where your PDK is installed")

    klayout_gds = os.path.join(os.path.dirname(sys.argv[0]), 'klayout_gds.xml')

    # if showing off the sky130 cells
    if args.show_sky130:
        path = check_path(os.path.join(os.environ['PDK_ROOT'], "sky130A", "libs.ref", "sky130_fd_sc_hd", "gds", "sky130_fd_sc_hd.gds"))
        command = "klayout -l %s %s" % (klayout_gds, path)
        os.system(command)
        print(command)
        exit()

    # check explicit argument
    if args.runs and os.path.exists(args.runs):
        runs_dir = args.runs
    # maybe it's in the current working directory
    elif os.path.exists('runs'):
        runs_dir = "runs"
    else:
        exit("couldn't find the runs directory, specify with --runs or change to the directory that contains it")

    list_of_files = glob.glob(runs_dir + "/*")

    if len(list_of_files) == 0:
        exit(f"no runs found in {runs_dir}")
    else:
        list_of_files.sort(key=openlane_date_sort)
        # what run to show?
        if args.run == -1:
            # default is to use the latest
            print("using latest run:")
            run_path = max(list_of_files, key=os.path.getctime)

        elif args.run is None:
            # UI for asking for which run to use
            for run_index, run in enumerate(list_of_files):
                print("\n%2d: %s" % (run_index, os.path.basename(run)), end='')
            print(" <default>\n")

            n = input("which run? <enter for default>: ") or run_index
            run_path = list_of_files[int(n)]

        else:
            # use the given run
            print(f"using run {args.run}")
            run_path = list_of_files[args.run]

    print(f"using run {run_path}")

    # check we can find a lef file, which is needed for viewing def files
    lef_path = check_path(os.path.join(os.environ['PDK_ROOT'],'sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef'))
    def_warning = "any views that use DEF files (floorplan, pdn, fine and detailed placement) will fail"
    if not os.path.exists(lef_path):
        print(f"no LEF file found, {def_warning}")

    klayout_tech = "/sky130A/libs.tech/klayout/tech/"
    lyt = check_path(os.environ['PDK_ROOT'] + klayout_tech + "sky130A.lyt")
    if not lyt:
        print("sky130A.lyt not found in PDK_ROOT, {def_warning}")

    lyp = check_path(os.environ['PDK_ROOT'] + klayout_tech + "sky130A.lyp")
    if not lyp:
        print("sky130A.lyp not found in PDK_ROOT, {def_warning}")
 
    lym = check_path(os.environ['PDK_ROOT'] + klayout_tech + "sky130A.map")
    if not lym:
        print("sky130A.map not found in PDK_ROOT, {def_warning}")

    # TODO fix path
    open_design = "/home/matt/work/asic-workshop/course/librelane/venv/lib/python3.12/site-packages/librelane/scripts/klayout/open_design.py"

    if args.summary:
        path = check_path(os.path.join(run_path, 'final', 'metrics.csv'))
        summary_report(path)

    if args.full_summary:
        path = check_path(os.path.join(run_path, 'final', 'metrics.csv'))
        full_summary_report(path)

    if args.drc:
        path = check_path(os.path.join(run_path, '*-magic-drc/reports/drc_violations.magic.rpt'))
        if os.path.exists(path):
            drc_report(path)
        else:
            print("no DRC file, DRC clean?")

    if args.synth:
        path = check_path(os.path.join(run_path, '*-yosys-synthesis/hierarchy.dot'))
        os.system("xdot %s" % path)

    if args.yosys_report:
        
        path = check_path(os.path.join(run_path, '*-yosys-synthesis/reports/stat.json'))
        with open(path) as f:
            data = f.read()
            json_data = json.loads(data)
            pprint.pprint(json_data['design'], compact=True)

    if args.antenna:
        path = check_path(os.path.join(run_path, '*-openroad-checkantennas/openroad-checkantennas.log'))
        if os.path.exists(path):
            antenna_report(path)
        else:
            print("no antenna file, did the run finish?")

    # these next 4 all need to use the open_design script as they are def files
    # the open_design script reads the arguments from the KLAYOUT_ARGV environment variable    
    if args.floorplan:
        path = check_path(os.path.join(run_path, '*-openroad-floorplan/*def'))
        os.environ["KLAYOUT_ARGV"] = f"--input-lef {lef_path} --lyt {lyt} --lym {lym} --lyp {lyp} {path}"
        os.system(f"klayout -rm {open_design}")

    if args.pdn:
        path = check_path(os.path.join(run_path, '*-openroad-generatepdn/*.def'))
        os.environ["KLAYOUT_ARGV"] = f"--input-lef {lef_path} --lyt {lyt} --lym {lym} --lyp {lyp} {path}"
        os.system(f"klayout -rm {open_design}")

    if args.global_placement:
        path = check_path(os.path.join(run_path, '*-openroad-globalplacement/*.def'))
        os.environ["KLAYOUT_ARGV"] = f"--input-lef {lef_path} --lyt {lyt} --lym {lym} --lyp {lyp} {path}"
        os.system(f"klayout -rm {open_design}")

    if args.detailed_placement:
        path = check_path(os.path.join(run_path, '*-openroad-detailedplacement/*.def'))
        os.environ["KLAYOUT_ARGV"] = f"--input-lef {lef_path} --lyt {lyt} --lym {lym} --lyp {lyp} {path}"
        os.system(f"klayout -rm {open_design}")

    if args.gds:
        path = check_path(os.path.join(run_path, 'final/gds/*.gds'))
        os.system("klayout -l %s %s" % (klayout_gds, path))

