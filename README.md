# LibreLane summary

After the [LibreLane ASIC flow](https://github.com/librelane/librelane) has finished, you have a lot of files in the run directory.
This tool allows you to explore the design and get various statistics from the final_report_summary.csv file.

Video demo: https://www.youtube.com/watch?v=2wBbYU_8dZI

Article: https://www.zerotoasiccourse.com/post/librelane_output_files/

# Compatibility

These tools are currently working for LibreLane in 2025. Check other branches for other versions.

# Setup

* Clone the repo somewhere and add the path to your $PATH
* Ensure PDK_ROOT are set correctly

## Example

If you cloned the repo to /home/matt/librelane_summary and you are using bash as your shell, add this line to your ~/.bashrc:

    export PATH=$PATH:/home/matt/librelane_summary

This adds the repository path as one of the places that executables can be found. Then anywhere else in the filesystem you can run the program by typing on the commandline:

    summary.py

# Requirements

* KLayout for most of the views
* LibreLane for the open_design.py script used by KLayout

# Show all skywater cells with KLayout

* This is useful for demonstrations, use the --show-sky130 argument to show all standard cells.

# Show stats and explore a specific design/run

* Use the --design argument to select the design
* Optionally use the --run argument to choose a specific run
* If your top module is called something other than the name of your design, set it with the --top argument
* If your design is part of Caravel, it uses a different structure for output files, so use the --caravel argument

# Examples

Change the directory where you ran LibreLane, so that the `./runs` directory is in your current working directory.

Show drc, violations summary and cell usage of latest run:

    summary.py --drc --summary --yosys

Show PDN of explict run:

    summary.py --pdn --run 2
