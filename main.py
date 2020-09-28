### This program is a very simple lemmatizer, which learns a
### lemmatization function from an annotated corpus. The function is
### so basic I wouldn't even consider it machine learning: it's
### basically just a big lookup table, which maps every word form
### attested in the training data to the most common lemma associated
### with that form. At test time, the program checks if a form is in
### the lookup table, and if so, it gives the associated lemma; if the
### form is not in the lookup table, it gives the form itself as the
### lemma (identity mapping).

### The program performs training and testing in one run: it reads the
### training data, learns the lookup table and keeps it in memory,
### then reads the test data, runs the testing, and reports the
### results.

### The program takes two command line arguments, which are the paths
### to the training and test files. Both files are assumed to be
### already tokenized, in Universal Dependencies format, that is: each
### token on a separate line, each line consisting of fields separated
### by tab characters, with word form in the second field, and lemma
### in the third field. Tab characters are assumed to occur only in
### lines corresponding to tokens; other lines are ignored.
import sys
import re

### Global variables

# Paths for data are read from command line
train_file = sys.argv[1]
test_file = sys.argv[2]

# Counters for lemmas in the training data: word form -> lemma -> count
lemma_count = {}

# Lookup table learned from the training data: word form -> lemma
lemma_max = {}

# Variables for reporting results
training_stats = ['Wordform types', 'Wordform tokens', 'Unambiguous types', 'Unambiguous tokens', 'Ambiguous types',
                  'Ambiguous tokens', 'Ambiguous most common tokens', 'Identity tokens']
training_counts = dict.fromkeys(training_stats, 0)

test_outcomes = ['Total test items', 'Found in lookup table', 'Lookup match', 'Lookup mismatch',
                 'Not found in lookup table', 'Identity match', 'Identity mismatch']
test_counts = dict.fromkeys(test_outcomes, 0)

accuracies = {}

### Training: read training data and populate lemma counters

train_data = open(train_file, 'r', encoding="utf8")

for line in train_data:

    # Tab character identifies lines containing tokens
    if re.search('\t', line):

        # Tokens represented as tab-separated fields
        field = line.strip().split('\t')

        # Word form in second field, lemma in third field
        form = field[1]
        lemma = field[2]

        ######################################################
        ### Insert code for populating the lemma counts    ###

        if form not in lemma_count.keys():
            lemma_count[form] = {}
            if lemma not in lemma_count[form].keys():
                lemma_count[form][lemma] = 1
            else:
                lemma_count[form][lemma] += 1
        else:
            if lemma not in lemma_count[form].keys():
                lemma_count[form][lemma] = 1
            else:
                lemma_count[form][lemma] += 1

        ######################################################

### Model building and training statistics
word_types = 0
ambiguous_types = 0
ambiguous_tokens = 0
unambiguous_tokens = 0
word_form_tokens = 0
unambiguous_types = 0
identity_token = 0
ambiguous_most_common_tokens = 0

for form in lemma_count.keys():

    ######################################################
    ### Insert code for building the lookup table      ###
    ######################################################
    lemma_max[form] = list(lemma_count[form].keys())
    ######################################################
    ### Insert code for populating the training counts ###
    word_types += 1
    word_form_tokens += sum(list(lemma_count[form].values()))
    if len(lemma_max[form]) == 1:
        unambiguous_types += 1
    else:
        ambiguous_types += 1

    if len(lemma_count[form]) == 1:
        unambiguous_tokens += sum(list(lemma_count[form].values()))
    else:
        ambiguous_tokens += sum(list(lemma_count[form].values()))
        ambiguous_most_common_tokens += max(lemma_count[form].values())
    for lem in lemma_count[form].keys():
        if lem == form:
            identity_token += lemma_count[form][lem]

    ######################################################

training_counts['Wordform types'] = word_types
training_counts['Wordform tokens'] = word_form_tokens
training_counts['Unambiguous types'] = unambiguous_types
training_counts['Unambiguous tokens'] = unambiguous_tokens
training_counts['Ambiguous types'] = ambiguous_types
training_counts['Ambiguous tokens'] = ambiguous_tokens
training_counts['Ambiguous most common tokens'] = ambiguous_most_common_tokens
training_counts['Identity tokens'] = identity_token

### Calculate expected accuracy if we used lookup on all items ###

accuracies['Expected lookup'] = (training_counts['Unambiguous tokens'] + training_counts[
    'Ambiguous most common tokens']) / training_counts['Wordform tokens']

### Calculate expected accuracy if we used identity mapping on all items ###

accuracies['Expected identity'] = training_counts['Identity tokens'] / training_counts['Wordform tokens']

### Testing: read test data, and compare lemmatizer output to actual lemma

test_data = open(test_file, 'r', encoding="utf8")

for line in test_data:

    # Tab character identifies lines containing tokens
    if re.search('\t', line):

        # Tokens represented as tab-separated fields
        field = line.strip().split('\t')

        # Word form in second field, lemma in third field
        form = field[1]
        lemma = field[2]

        ######################################################
        ### Insert code for populating the test counts     ###
        test_counts['Total test items'] += 1
        if form in lemma_max.keys():
            test_counts['Found in lookup table'] += 1
            if len(lemma_max[form]) == 1 and lemma == lemma_max[form][0]:
                test_counts['Lookup match'] += 1
            elif lemma in lemma_max[form]:
                if lemma_count[form][lemma] == max(list(lemma_count[form].values())):
                    test_counts['Lookup match'] += 1
                else:
                    test_counts['Lookup mismatch'] += 1
            else:
                test_counts['Lookup mismatch'] += 1

        else:
            test_counts['Not found in lookup table'] += 1
            if form == lemma:
                test_counts['Identity match'] += 1
            else:
                test_counts['Identity mismatch'] += 1

        ######################################################

accuracies['Lookup'] = test_counts['Lookup match'] / test_counts['Found in lookup table']

### Calculate accuracy on the items that used the lookup table ###

accuracies['Identity'] = test_counts['Identity match'] / test_counts['Not found in lookup table']

### Calculate accuracy on the items that used identity mapping ###

accuracies['Overall'] = (test_counts['Lookup match'] + test_counts['Identity match']) / test_counts['Total test items']

### Calculate overall accuracy ###

### Report training statistics and test results

output = open('lookup-output.txt', 'w')

output.write('Training statistics\n')

for stat in training_stats:
    output.write(stat + ': ' + str(training_counts[stat]) + '\n')

for model in ['Expected lookup', 'Expected identity']:
    output.write(model + ' accuracy: ' + str(accuracies[model]) + '\n')

output.write('Test results\n')

for outcome in test_outcomes:
    output.write(outcome + ': ' + str(test_counts[outcome]) + '\n')

for model in ['Lookup', 'Identity', 'Overall']:
    output.write(model + ' accuracy: ' + str(accuracies[model]) + '\n')

output.close
