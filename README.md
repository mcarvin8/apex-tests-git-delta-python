# Apex Tests Git Delta

This project demonstrates two ways to determine the required Apex test classes between two git commits for Salesforce deployments.

This requires Git, Python 3, and only 1 Salesforce CLI (`sfdx` or `sf`) to be installed in the environment.

## Option 1 - Declaring Tests with a File

A text file, called `runTests.txt`, will be used to set required Apex test classes to run during the deployment.

Multiple test classes should be separated with a comma (no spaces).

We will assume this file is accurately set in all commits in the desired range.

The contents of the `runTests.txt` file in every commit between the two reference points will be read
to build the delta `runTests.txt` file with all combined test classes.

The delta `runTests.txt` file created will have no duplicate test classes and will not contain test classes
which do not exist on the HEAD reference (`--new` argument).

### Use Case
`python3 ./apex_tests_git_delta_file.py --old "7cdd5548" --new "9b37bb11" --file "runTests.txt"`

## Option 2 - Declaring Tests with the Commit Message

Every commit message will contain the following regular expression if Apex tests are required for the changes:
`Apex::Class1,Class2,Class3::Apex`

The entire "Apex" string is case insensitive.

The final combined test class string will have no duplicate test classes and will not contain test classes
which do not exist on the HEAD reference (`--new` argument).

### Use Case
`python3 ./apex_tests_git_delta_commit_msg.py --old "7cdd5548" --new "9b37bb11"`

## CI/CD Usage
You can use either script with the `sfdx-git-delta` plugin to create the delta package.xml.

`sfdx sgd:source:delta --from "7cdd5548" --to "9b37bb11" --output "."`

Both scripts can be called from a bash terminal to store the output in a bash variable.

`testclasses=$(python3 ./apex_tests_git_delta_file.py --old "7cdd5548" --new "9b37bb11" --file "runTests.txt")`

`testclasses=$(python3 ./apex_tests_git_delta_commit_msg.py --old "7cdd5548" --new "9b37bb11")`

The `$testclasses` variable will contain the properly formatted test classes string for the CLI and
can be used with the `RunSpecifiedTests` parameter.

`sfdx force:source:deploy -x package/package.xml -l RunSpecifiedTests -r $testclasses --verbose`

`sf project deploy start -x package/package.xml -l RunSpecifiedTests -r $testclasses --verbose`