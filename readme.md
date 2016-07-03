# Batch Renamer

This program does a recursive rename on a directory given a set of
'personal' rules.

There is a file called 'exclude_re_patterns.txt' which is a list of line
separated regular expressions to be ignored in case they are found. Comments
are lines which start with '#'. An example is provided below:

    # these are a list of re patterns to exclude
    # commentaries start with '#'
    #
    # ignores any path containing the '.git' pattern
    .*\.git.*

## Example after running the program:
__From:__

    __not_for_packaging
    ├── #
    ├── #1811zz
    ├── #1811_zz
    ├── #1811_zz123123 adfadf 123 adf __
    ├── #1811_zz123123 adfadf 123 adf __12
    ├── #1811_zz123123 adfadf 123 adf __12_
    ├── 20110101_%$abba
    ├── 20150531_file
    ├── ___3help____4_1__2_.txt
    ├── authors.txt
    ├── exclude_re_patterns.txt
    ├── .git
    ├── .gitignore
    ├── readme.md
    ├── __&_test_&&&&&&&&00.txt
    ├── __&_test_&&&&&&&&01.txt
    ├── __&_test_&.txt
    ├── __&_test_&&.txt
    ├── __&_test_&&&.txt
    ├── __&_test_&&&&.txt
    ├── .this_shit__123123$%
    ├── .vim___rc__
    ├── #z00
    ├── ##z00
    └── ##_#z00
    
7 directories, 18 files

__To:__

    __not_for_packaging
    ├── 1811zz
    ├── 1811_zz
    ├── 1811_zz123123adfadf123adf
    ├── 1811_zz123123adfadf123adf_00
    ├── 1811_zz123123adfadf123adf_12
    ├── 20110101_abba
    ├── 20150531_file
    ├── ___3help_4_1_2.txt
    ├── authors.txt
    ├── empty_name_after_e
    ├── exclude_re_patterns.txt
    ├── .git
    ├── .gitignore
    ├── readme.md
    ├── ___test_00.txt
    ├── ___test_01.txt
    ├── ___test_02.txt
    ├── ___test_03.txt
    ├── ___test_04.txt
    ├── ___test.txt
    ├── .this_shit__123123$%
    ├── .vim___rc__
    ├── z00
    ├── _z00
    └── z01
    
7 directories, 18 files

Using the follwing exclude_re_patterns.txt file:

	# these are a list of re patterns to exclude
	# commentaries start with '#'
	#
	# ignores git file
	.*\.git.*
	# ignores files/folders whose filename starts with a '.' (in linux)
	.*\/\..*
	# ignores files/folders whose filename starts with a '.' (in windows)
	.*\/\\..*

## TODO

- add test module

- Fix changing uppercase to lowercase on windows not being detected as change
  such as 'Capulet' being renamed to 'capulet_00' instead of 'capulet'
