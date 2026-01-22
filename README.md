# Valentine Matcher

#### Video Demo: [Go to video demo](https://youtu.be/pMl6ne89VVc)
#### Description:
'Valentine Matcher' is a Python program that matches individuals based on responses to a variety of questions and finds best matches for each individual as well as the compatibilities with them! All of the data is read from CSV files in a quite flexible manner and then match results *(with compatibilities as %)* are created as either HTML and/or PDF result files, grouping respondents according to custom groups chosen by the user of the program. This project draws upon several ideas and topics from CS50, mainly python *(with the csv module)*, HTML/CSS and jinja2 for file creation from templates!


## How the program works in detail

### CSV input data
The program takes as input a CSV file containing participants’ data and responses to yes/no, single-choice, multiple-choice and rating *(on a number scale)* questions.

 - The CSV data file can be of several locales, as the program allows to set custom delimiters for cell separation and multiple choice separation in a single cell via command line arguments
 - It is possible for the program to ignore any columns that do not have any effect on matching *(such as timestamp or textual feedback question columns)*
 - Participants can choose preferred gender(s) they wish only to be matched with.
 - Participants can belong to none, one or more groups. If they do, in the result files they will not only see their best matches among all participants but also best matches in every group they belong to.
 *(for ex. high school students may belong to 'grade' and 'class' groups whereas corporate workers to 'department' and 'role' groups)

The program then parses the input CSV data file using the `csv` python module according to parameters (arguments) specified by the user.

### Match results generating
The program separates respondent data and question data, then creating a match table *(a 2d dictionary)* that stores all of the compatibility percentages between all possible pairs of respondents.

Compatibility between any two respondents is calculated using the following these steps:
 1. It calculates the points both respondents receive from a question by how well the answers to it match. This uses a different algorithm for each of the question types *(yes/no, single-choice, multiple-choice and rating)*. The points given are in a specific range: from 0 up to a precalculated maximum amount of points allowed for said question.
 2. It sums the points received from all of the questions' matching answers.
 3. Then the amount of points got for matching answers is divided by the total amount of points that could have been got from all of the question combined. This number is then multiplied by 100 to yield a compatibility score *(a math percentage)* in a range 0-100%.

After the whole match table is populated with compatibility scores *(i.e. all of the respondents have been matched with each other)*, top matches are separated for each respondent *(and in every group if these are specified)* to be used in the result file(s). It is possible to specify a maximum amount of top matches that should appear in any group and the whole pool likewise.

### Result file(s) generating
It is possible to generate **html** and/or **pdf** result files.

The html file is generated using the `jinja2` library from two html template files that also contain quite some styling. Jinja is used to insert all of the match and compatibility data dynamically with some jinja loop and if statements.
The pdf file is generated from the exact same html content *(that is first stored as a string, and then used to generate said files)*, using the `pdfkit` library.

> On how to properly install `pdfkit` and `wkhtmltopdf`, head to [this page](https://pypi.org/project/pdfkit).
> Also, if you have trouble installing either `jinja2` or `pdfkit`, you might find it useful to use a virtual environment `venv` as I did :D.

While using the program it is possible to specify what should the program do when the file to be generated already exists *(whether to ask if should override, override without asking or skip without asking using the `--on-file-exists` argument)*.

## The file structure
 * `matchmaker.py`: the entry-point of the program, the file to be run to run the program
 * `classes/`: contains class definitions that are used everywhere around the program, each class being in its own separate file *(for the most part) 
    * `respondent.py`: defines the `Respondent` class which holds the general info about the participant, groups they are part of and answers to all questions
    * `match_table.py`: defines `MatchTable` which manages the 2d dictionary containing all compatibility scores between all respondents
    * `match.py`: defines `Match` and `MatchGroup` dataclasses which store the compatibility scores between respondents to avoid ambiguity
 * `csv_io/`: contains all of the functionality for reading and parsing the csv input data file
     * `read_csv.py`: handles near all csv data file parsing and reading
     * `validate_csv.py`: contains one simple function which checks if the csv file exists
 * `matching/`: here lives all of the matching and compatibility result calculation functionality
     * `match_all.py`: helps take all data extracted from the csv data file and output a filled `MatchTable` with all compatibility percentages
     * `get_grouped_matches.py`: helps take a match table and return the list of matches in every group *(used in the generation of result files)*
 * `templates/`: contains the HTML/CSS template files for result file generation
     * `respondent_results.html`: the main HTML/CSS template
     * `_single_match_row.html`: contains the helper jinja macro that contains the html of a single result row
 * `results/`: all of the logic for generating html and pdf result files
     * `result_filepath.py`: defines helper function to generate the filename of a respondent's result file
     * `generate_html_content.py`: prepares the HTML content of the result file as a single string
     * `generate_result_file.py`: contains logic for fully generating a single html or pdf result file
     * `generate_all.py`: manages the generation of all of the result files for all of the respondents
 * `utils/`: contains general helper functions and constants
     * `cli.py`: configures the CLI for the program *(using the `argparse` library)*
     * `constants.py`: here live all of the constants for the CSV headers, data and CLI default arguments
     * `filesystem.py`: function for operating on the filesystem - making directories, getting the extension of a file, etc.
     * `jinja.py`: configuration for the `jinja2` environment

## How to format the CSV data file:
For the program to be able to determine in which columns lives what data, the very first line of the csv file must be a "header", in which you specify specific "column headings":

 - Input CSV files must include the `FULL_NAME` column heading, where the full names of the respondents are.
 - To specify the gender of the respondents use the `GENDER` column heading. As of right now you can specify the male gender with strings: `M`, `MALE`, `MAN`, the female gender with `W`, `FEMALE`,  `WOMAN`  and "other" gender with `O`, `OTHER` strings as values of respondent cells.
 -  To specify the gender(s) with which the respondents would like to be matched, include the `GENDERS_TO_MATCH_WITH` column header. In this column can be one or more gender values separated by a delimiter (`--multi-delimiter`) or with the normal delimiter (`--delimiter`) if the cell is properly escaped with double quotes `"`.
 - To specify fields in which values are the groups of respondents, use one or more `GROUP|<group name>` column headings. The `GROUP|` keyword is always the same, and right after the pipe character `|` comes the name of the group.
 *For example, to specify a group of name "departments", use a column heading `GROUP|departments`.*
 - Questions are specified by type:
     - Yes/No (`YN`): question with two possible choices, one can be selected
     - Single Choice (`SC|<n>`): single choice question with `n` amount of options. Amount of options `n` must always be specified (a positive integer).
     - Multiple Choice (`MC|<n>`): multiple choice question with `n` amount of options. Amount of options `n` must always be specified (a positive integer). Multiple options are separated the same as multiple genders in the `GENDERS_TO_MATCH_WITH` column.
     - Rating (`RT|<n>`): a rating on a number scale from 1 to `n`. The amount of options `n` is optional, as if not specified it defaults to `5` *(and thus a number range 1-5)*.

Participants’ responses must match the order of headers in the CSV file. Multi-select answers and multiple genders in the `GENDERS_TO_MATCH_WITH` column should be enclosed in quotes and separated by the multi-choice delimiter (`--multi-delimiter`) or the general delimiter (`--delimiter`) if the whole cell is properly escaped using double quotes `"`.
The csv parser ignores trailing whitespaces in the cells, so you are welcome to format the cells with whitespaces however you like!

> **Make sure to take a look at the `_examples/` folder, which contains quite a few examples input csv data files (which you should use).** Most examples files contain a lot of unnecessary whitespace just to be easier for anyone to read and comprehend - they are not needed!
> Also, I know that I have written a lot here, and believe that concrete examples (like ones in the `_examples/`) folder tell much more :D

## How to use the CLI program `matchmaker.py`
If you need quick help on what arguments there are and what they do, use the `-h` argument/flag for help: `python3 matchmaker.py -h`.

Here are the command line arguments to be used:
- `in_file`: input CSV data file filename, required, always the first argument
- `formats`: output file types, either `html`, `pdf`, or both. Required, always the second argument
- `--delimiter`: cell delimiter in the CSV file (default: `,`)
- `--multi-delimiter`: cell delimiter used for delimiting multiple options chosen by the respondent to a single question (default: `;`)
- `-p, --precision`: decimal places for compatibility values (default: `2`; `-1` for no rounding - not recommended)
- `-s, --separate-by-groups`: use this arg to put respondent result files in separate folders by groups that each respondent is in
- `-m, --max-results-in-group`: maximum number of matches to display per group and in the whole respondents' pool (default: `5`)
- `--on-file-exists`: specify behavior if a result file to be generated already exists: `ask`, `override`, or `skip` (default: `ask`).

Here are some example prompts:
 1. `matchmaker.py input.csv html` - generates html result files using csv file `input.csv`
 2. `matchmaker.py inputs/data.csv html pdf` - generates both html and pdf result files using csv file `inputs/data.csv`
 3. `matchmaker.py input.csv html pdf -p 1 -m 10` - generates both html and pdf result files, where each compatibility result is rounded to 1 decimal place. In each of the groups are showed up to 10 top matches
 4. `matchmaker.py input.csv pdf --delimiter ";" --multi-delimiter ","` - generates pdf result files where each cell is delimited by char `;` and multiple options in a single cell are delimited using `,`
 5. `matchmaker.py input.csv pdf -s --on-file-exists skip` - generate pdf result files, and put them in separate folders by which group(s) the respondents belong to. Also, if any of the files already exist, skip the generation of those ones.

> NOTE: pdf file generation, especially if generating many files, takes quite a lot of time. In case that the program got interrupted and stopped during pdf file generation, rerun the prompt with the flag `--on-file-exists` set to `override`, as it will skip the generation of already generated files, and "continue where it left off".

## Design choices

 - **Unified result file generation** - the generation of HTML and PDF files share the same function and functionality, avoiding repeating code
 - **Error handling** - a lot of `try / except` statements are used so the user of the program does not encounter any unformatted, cluttered python error messages
 - **Flexible design** - implementing new question types or headings for csv data file will be a simple process requiring minimal changes


### This is Weekintas (Vykintas Mylimas) from CS50x