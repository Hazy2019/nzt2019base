#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import re
import os
import subprocess

def show_help():
    print("%s <filename>" % sys.argv[0])

def output_file(filename, lines, more_idx):
    print("output %d lines to %s, with readmore at %d line..." % (len(lines), filename, more_idx))
    with open(filename, "w") as f:
        for i in range(len(lines)):
            if i == more_idx:
                f.write("<!--more-->\n")
            f.write(lines[i])

def add_readmore_tag(filename, summary_lines = 5):
    tmp_file = ""
    run = False
    with open(filename, "r") as f:
        lines = f.readlines()

        end_front_idx = 0
        to_input_idx = -1
        hit_fq = 0
        hit_ctn = 0
        for i in range(len(lines)):
            if lines[i] == "<!--more-->\n": # already have
                print("%s already have readmore tag at %d line..." % (filename, i))
                return

        for i in range(len(lines)):
            if (not (re.match("^-+\n$", lines[i]) is None)):
                hit_fq = hit_fq + 1
                if (hit_fq == 2):
                    end_front_idx = i
                    break

        for i in range(len(lines)):
            if (i > end_front_idx):
                if (re.match("^\s*$", lines[i]) is None): # is not a blank line
                    hit_ctn = hit_ctn + 1
                    if (hit_ctn == (summary_lines + 1)):
                        to_input_idx = i
                        break

        if to_input_idx > 0:
            fpath = os.path.dirname(os.path.abspath(filename))
            fbase = os.path.basename(filename)
            tmp_file = "%s/.%s~" % (fpath, fbase)
            output_file(tmp_file, lines, to_input_idx)
            run = True
    if run:
        print("try to mv %s %s" % (tmp_file, filename))
        subprocess.run(["mv", tmp_file, filename])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
    else:
        add_readmore_tag(sys.argv[1])
