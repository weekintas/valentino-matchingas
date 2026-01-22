###############################
#   CSV DATA FILE CONSTANTS   #
###############################

# Required csv headers
HEADER_FULL_NAME = "FULL_NAME"

# Optional csv headers
HEADER_GENDER = "GENDER"
HEADER_GENDERS_TO_MATCH_WITH = "GENDERS_TO_MATCH_WITH"

# Optional csv headers with parameters
HEADER_GROUP_PREFIX = "GROUP"

# Other csv data file constants
CSV_DATA_DEFAULT_DELIMITER = ","
CSV_DATA_DEFAULT_MC_DELIMITER = ";"
"""The delimiter which separates multiple options chosen in a single question rather than separating different questions
like `CSV_DATA_DEFAULT_DELIMITER` does"""
CSV_DATA_PARAMETER_DELIMITER = "|"
PARAM_INDEX_NUM_OPTIONS: int = 0
"""The index, at which in the question's params list is the `num_options`"""

# NOTE: you can find headers for specifying questions (question_types) in classes/question_data.py
# NOTE: genders must be specified according to the classes/gender.py Gender.from_string method


#####################
#   CLI CONSTANTS   #
#####################

CLI_DEFAULT_MAX_RESULTS_IN_GROUP: int = 5


###################################
#   RESULT GENERATING CONSTANTS   #
###################################

ALL_PARTICIPANTS_GROUP_TITLE = "Among all participants"
