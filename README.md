# Apex Tests Git Delta

This project demonstrates a way to determine the required Apex test classes between two git commits for Salesforce deployments.

This requires Git, Python 3, and the Salesforce CLI (`sfdx` or `sf`) to be installed in the environment.

## Declaring Tests with the Commit Message

Every commit message will contain the following regular expression if Apex tests are required for the changes:
- `Apex::Class1,Class2,Class3::Apex`

Test classes can be separated by commas, spaces, or both.

The `Apex::`/`::Apex` string is case insensitive.

The final delta test class string will have no duplicate test classes and will not contain test classes which do not exist on the `--to` commit tree. This assumes the directory structure follows the default `force-app` structure.

### Use Case

By default, the test classes will be in the proper formatting for the `sf` CLI.

- `python3 ./apex_tests_git_delta.py --from "7cdd5548" --to "9b37bb11"`

Add `--sfdx` to format the test classes for the `sfdx` CLI.

- `python3 ./apex_tests_git_delta.py --from "7cdd5548" --to "9b37bb11" --sfdx`

The output of the script can be captured in a bash variable as such:

- `testclasses=$(python3 ./apex_tests_git_delta.py --from "7cdd5548" --to "9b37bb11")`

The `$testclasses` variable then can be used with the `RunSpecifiedTests` parameter of the CLI deployment command.

- `sf project deploy start -l RunSpecifiedTests -t $testclasses`
- `sfdx force:source:deploy -l RunSpecifiedTests -r $testclasses`
