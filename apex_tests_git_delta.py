"""
    Script to set Apex tests using the git diff.
"""
import argparse
import logging
import os
import re
import subprocess


# Format logging message
logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """
        Function to pass required arguments.
    """
    parser = argparse.ArgumentParser(description='Determine required Apex tests between 2 commits.')
    parser.add_argument('-f', '--from', dest='from_value')
    parser.add_argument('-t', '--to', dest='to_value')
    parser.add_argument('-s', '--sfdx', default=False, action='store_true')
    args = parser.parse_args()
    return args


def parse_test_classes(commit_message):
    """
        Extract test classes from the commit message.
    """
    try:
        test_classes = re.search(r'[Aa][Pp][Ee][Xx]::(.*?)::[Aa][Pp][Ee][Xx]', commit_message, flags=0).group(1)
        if test_classes.isspace() or not test_classes:
            raise AttributeError
    except AttributeError:
        test_classes = ''
    test_classes = re.split(r'[,\s]+', test_classes)
    test_dict = {}
    for test_class in test_classes:
        test_dict[test_class] = True
    return ' '.join(test_dict.keys())


def validate_test_classes(test_classes, commit):
    """
        Confirm test classes are valid test classes
        in the "to" commit reference.
    """
    valid_test_classes = []
    for test_class in test_classes:
        file_name = test_class + '.cls'
        full_path = f'force-app/main/default/classes/{file_name}'
        cmd = f'git ls-tree {commit} --name-only -- {full_path}'
        try:
            output = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            output_lines = output.stdout.splitlines()
            filenames = [os.path.basename(line) for line in output_lines]
            if file_name in filenames:
                valid_test_classes.append(test_class)
        except subprocess.CalledProcessError:
            continue
    return valid_test_classes


def replace_with_commas(string):
    """
        Function to replace spaces with a comma.
    """
    return string.replace(' ', ',')


def main(from_ref, to_ref, sfdx):
    """
        Main function.
    """
    commit_range = f'{from_ref}..{to_ref}'
    # Initialize an empty dictionary to store the test classes
    combined_test_classes = {}

    # Get the commit messages from the commit range
    commit_messages = subprocess.check_output(['git', 'log', '--pretty=format:%B', commit_range]).decode('utf-8').splitlines()

    # Iterate over each commit message
    for commit_message in commit_messages:
        test_classes = parse_test_classes(commit_message)
        combined_test_classes.update({test_class: True for test_class in test_classes.split()})

    # Validate test classes are in the `--to` working tree
    valid_test_classes = ' '.join(validate_test_classes(combined_test_classes, to_ref))

    # Replace spaces with commas for the `sfdx` CLI
    if sfdx:
        valid_test_classes = replace_with_commas(valid_test_classes)
    print(valid_test_classes)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.from_value, inputs.to_value,
         inputs.sfdx)
