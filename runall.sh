####
#### See the README.md for details about each script.
####
#### Make sure DATA_DIR is set in the config.py file.
####
#### I suggest using the environment.yml file to set
#### up the same conda environment I used.
####

# set script to exit if any command fails
set -e

# handle command line argument
if [[ $# -gt 1 ]]; then             # exit if more than one argument provided
  echo "!! noliwc is the only allowed argument !!"; exit;
elif [[ $# -eq 1 ]]; then
  if [[ $1 != "noliwc" ]]; then     # exit if the one argument is not "noliwc"
    echo "!! noliwc is the only allowed argument !!"; exit;
  fi
fi

# setup
python setup-data_dirs.py

# scrape and clean
echo "Scraping and cleaning all data will take hours..."
python scrape-posts.py
python clean-posts.py
python scrape-users.py
python clean-users.py
python anonymize-posts.py

# describe
echo "Description analyses take just a minute altogether..."
python describe-timecourse.py
python describe-usercount.py
python describe-toplabels.py
python describe-categorycounts.py
python describe-categorypairs.py
python describe-demographics.py
python describe-wordcount.py

# validate
echo "Validation analyses are quick unless LIWCing..."
python validate-classifier.py
python validate-classifier_stats.py
python validate-wordshift.py
python validate-wordshift_plot.py
if [[ -z "$1" ]]; then # no argument supplied (ie, run liwc)
  python validate-liwc.py --words
  python validate-liwc_stats.py
  python validate-liwc_word_stats.py
  python validate-liwc_word_plot.py
fi
