# MIPS in Amaranth
Description of a segmented RISC (MIPS) with a modular implementation in amaranth
## What is Amaranth?
The Amaranth project provides an open-source toolchain for developing hardware based on synchronous digital logic using the Python programming language, as well as evaluation board definitions, a System on Chip toolkit, and more. It aims to be easy to learn and use, reduce or eliminate common coding mistakes, and simplify the design of complex hardware with reusable components.
## Pipeline
- **IF:** Instruction fetch
- **ID:** Instruction decode
- **EX:** Execute
- **MEM:** Memory
- **WB:** Write back

 ![alt text](https://i.imgur.com/BPVdf7r.png)
 
## Installation
- Official instructions found [here](https://amaranth-lang.org/docs/amaranth/latest/install.html). This project was compiled with the development (git) version of Amaranth (installed through `pip3`).
## Testing
  * Just run in terminal
  `python3 processor.py` to generate .vcd file
  * Open processor.vcd or run `gtkwave processor.vcd`
## Files
 - The trial program "program.s" provided  is risk-free and tests all the basic exercise instructions. The "program" file is the result of the assembly of the "program.s" that will be used to test the basic exercise. The "data" file contains the data to be used for use by the "program" in the basic exercise.
