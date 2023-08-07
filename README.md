# Apex Tests Git Delta

This project demonstrates a way to determine the required Apex test classes between two git commits for Salesforce deployments.

This requires Git, Python 3, and the Salesforce CLI (`sfdx` or `sf`) to be installed in the environment.

## Declaring Tests with the Commit Message

Every commit message will contain the following regular expression if Apex tests are required for the changes:
`Apex::Class1,Class2,Class3::Apex`

The entire "Apex" string is case insensitive.

The final combined test class string will have no duplicate test classes and will not contain test classes
which do not exist on the HEAD reference (`--new` argument).

### Use Case
By default, the test classes will be in the proper formatting for the `sfdx` CLI.
`python3 ./apex_tests_git_delta.py --old "7cdd5548" --new "9b37bb11"`

Add `--sf` to format the test classes for the `sf` CLI.
`python3 ./apex_tests_git_delta.py --old "7cdd5548" --new "9b37bb11" --sf`

The output of the script can be captured in a bash variable as such:

`testclasses=$(python3 ./apex_tests_git_delta.py --old "7cdd5548" --new "9b37bb11")`

The `$testclasses` variable then can be used with the `RunSpecifiedTests` parameter of the CLI deployment command.

`sfdx force:source:deploy -x package/package.xml -l RunSpecifiedTests -r $testclasses --verbose`

`sf project deploy start -x package/package.xml -l RunSpecifiedTests -r $testclasses --verbose`