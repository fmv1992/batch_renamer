# Batch Renamer

This program simple does a recursive rename on a directory given a set of
'personal' rules.

There is a file called 'exclude_re_patterns.txt' which is a list of line separated re expressions to be ignore in case they are found. Comments are lines which start with '#'. An example is provided below:

    # these are a list of re patterns to exclude
    # commentaries start with '#'
    #
    # ignores git file
    .*\.git.*
