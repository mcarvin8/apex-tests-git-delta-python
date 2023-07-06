"""
    Script to build the runTests.txt using the git diff.
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
        file - file with test classes
    """
    parser = argparse.ArgumentParser(description='Create the runTests.txt file between 2 commits.')
    parser.add_argument('-o', '--old')
    parser.add_argument('-n', '--new')
    parser.add_argument('-f', '--file', default='runTests.txt')
    args=parser.parse_args()
    return args


def get_git_diff(file_path, commit_range):
    """
        Get the diff of the file over the commit range.
    """
    diff_output = subprocess.check_output(['git', 'diff', '--unified=0', commit_range, '--', file_path])
    diff_output = diff_output.decode('utf-8')
    return diff_output


def get_file_contents(commit, file_path):
    """
        Get the file content for the specific git commit.
    """
    try:
        contents = subprocess.check_output(['git', 'show', f'{commit}:{file_path}'])
        return contents.decode('utf-8')
    except subprocess.CalledProcessError:
        return ''


def parse_test_classes(file_contents):
    """
        Add each test class separated by commas to the dictionary.
    """
    test_classes = file_contents.split(',')
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


def create_combined_test_file(test_file, test_classes):
    """
        Overwrite the test file.
    """
    with open(test_file, 'w', encoding='utf-8') as file:
        file.write(test_classes)


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


def format_for_cli(testclasses):
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
        logging.info('SF and SFDX installed on the current system. Please un-install one and try again.')
        sys.exit(1)
    if not sf and not sfdx:
        logging.info('SF nor SFDX is installed on the current system. Please install ONE and try again.')
        sys.exit(1)

    # format test classes for applicable CLI
    if sf:
        testclasses = remove_spaces(testclasses)
        testclasses = replace_commas(testclasses)
    elif sfdx:
        testclasses = remove_spaces(testclasses)
    return testclasses


def main(from_ref, to_ref, test_file):
    """
        Main function.
    """
    commit_range = f'{from_ref}..{to_ref}'
    # Initialize an empty dictionary to store the test classes
    combined_test_classes = {}

    # Iterate over each commit in the range
    for commit in subprocess.check_output(['git', 'rev-list', commit_range]).decode('utf-8').splitlines():
        file_contents = get_file_contents(commit, test_file)
        test_classes = parse_test_classes(file_contents)
        combined_test_classes.update({test_class: True for test_class in test_classes.split()})
    valid_test_classes = validate_test_classes(combined_test_classes, to_ref)
    # Create the combined test file
    create_combined_test_file(test_file, ','.join(valid_test_classes))
    # Format the test classes for the applicable CLI
    formatted_test_classes = format_for_cli(','.join(valid_test_classes))
    print(formatted_test_classes)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.old, inputs.new, inputs.file)
