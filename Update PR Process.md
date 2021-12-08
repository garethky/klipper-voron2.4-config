# Update PR Process

Here is how I update my Klipper PRs. They want the PR to be 1 commit so its easy to merge and easy to revert. This process keeps the PR condensed to 1 commit even with edits and merges.

1. roll back the branch to the commit thats the PR (if need)
`git reset --hard <SHA>`

2. change the upstream to master:
`git branch -u master`

3. Go on github and pull in master from the kilpper origin

4. Then pull down those changes into your local master branch
git checkout master
git pull --rebase
git checkout temperature-wait-refactor

5. pull in everything from master and rebase on top of it
pull --rebase from master

6. do whatever work needs doing!
```
git commmit -m "fixup"
git rebase -i
...
```

6. When work is finished, switch upstream back to the remote:
git branch -u origin/temperature-wait-refactor

7. Overwrite the remote branch with your prepared change
git push --force origin
