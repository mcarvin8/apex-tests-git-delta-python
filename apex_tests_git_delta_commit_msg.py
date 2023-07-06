"""
    Script to set Apex tests using the git diff.
"""
import argparse
import logging
import os
import re
import subprocess
import sys


# Format logging message
logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """
        Function to pass required arguments.
        old - previous commit (from)
        new - newer commit (to)
    """
    parser = argparse.ArgumentParser(description='Determine required Apex tests between 2 commits.')
    parser.add_argument('-o', '--old')
    parser.add_argument('-n', '--new')
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
        test_classes = remove_spaces(test_classes)
    except AttributeError:
        test_classes = ''
    test_classes = test_classes.split(',')
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


def remove_spaces(string):
    """
        Function to remove extra spaces in a string.
    """
    pattern = re.compile(r'\s+')
    return re.sub(pattern, '', string)


def replace_commas(string):
    """
        Function to remove commas with a single space.
    """
    return re.sub(',', ' ', string)


def format_for_cli(test_classes):
    """
        Format test classes string for the CLI.
    """
    # Check if 'sf' is a valid command
    try:
        output = subprocess.run(['sf', '--version'], shell=True, capture_output=True, text=True, check=True)
        logging.info("sf is installed.")
        sf = True
    except subprocess.CalledProcessError:
        logging.info("sf is not installed")
        sf = False

    # Check if 'sfdx' is a valid command
    try:
        output = subprocess.run(['sfdx', '--version'], shell=True, capture_output=True, text=True, check=True)
        logging.info("sfdx is installed.")
        sfdx = True
    except subprocess.CalledProcessError:
        logging.info("sfdx is not installed.")
        sfdx = False

    # confirm 1 and only 1 executable is installed
    if sf and sfdx:
        logging.info('SF and SFDX installed on the current system. Please uninstall one and try again.')
        sys.exit(1)
    if not sf and not sfdx:
        logging.info('SF nor SFDX is installed on the current system. Please install ONE and try again.')
        sys.exit(1)

    # replace commas for the sf executable
    # test classes already formatted for sfdx executable
    if sf:
        test_classes = replace_commas(test_classes)
    return test_classes


def main(from_ref, to_ref):
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

    valid_test_classes = validate_test_classes(combined_test_classes, to_ref)
    # Format the test classes for the applicable CLI
    formatted_test_classes = format_for_cli(','.join(valid_test_classes))
    print(formatted_test_classes)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.old, inputs.new)
