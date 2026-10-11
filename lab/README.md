# lab/

Small, heavily commented Python scripts, one per chapter, that you can run on your
own laptop against your own AWS account. Every script that creates an AWS resource
has a matching teardown step in `scripts/teardown.sh`.

Anything a script generates (keys, certificates, tokens) is written to `lab/out/`,
which git ignores.
