# OpenLane summary

After the [OpenLane ASIC flow](https://github.com/efabless/openlane) has finished, you have a lot of files in the run directory.
This tool allows you to explore the design and get various statistics from the final_report_summary.csv file.

Video demo: https://www.youtube.com/watch?v=2wBbYU_8dZI

Article: https://www.zerotoasiccourse.com/post/openlane_output_files/

# Compatibility

These tools are currently working for MPW7 tagged OpenLane.

# Setup

* Clone the repo somewhere and add the path to your $PATH
* Ensure OPENLANE_ROOT and PDK_ROOT are set correctly

## Example

If you cloned the repo to /home/matt/openlane_summary and you are using bash as your shell, add this line to your ~/.bashrc:

    export PATH=$PATH:/home/matt/openlane_summary

This adds the repository path as one of the places that executables can be found. Then anywhere else in the filesystem you can run the program by typing on the commandline:

    summary.py

# Requirements

* KLayout for most of the views
* GDS3D for 3D GDS view: https://github.com/trilomix/GDS3D

# Show all skywater cells with KLayout

* This is useful for demonstrations, use the --show-sky130 argument to show all standard cells.

# Show stats and explore a specific design/run

* Use the --design argument to select the design
* Optionally use the --run argument to choose a specific run
* If your top module is called something other than the name of your design, set it with the --top argument
* If your design is part of Caravel, it uses a different structure for output files, so use the --caravel argument

# Examples

Show drc, violations summary and cell usage of latest run:

    summary.py --design led_blinky --drc --summary --yosys

Show PDN of explict run:

    summary.py --design led_blinky --pdn --run 2

Show 3D GDS view of user_project_wrapper part of Caravel:

    summary.py --design user_project_wrapper --caravel --gds-3d
