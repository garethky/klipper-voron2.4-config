## Fix SSH on Startup
New MacOS is stupid! On startup, running this fixes things:
```
ssh -T git@github.com
```

## How To Rebase

How to rebase the klipper master branch and get it under existing changes

1. Go to github and pull in the latest version of the master branch to my fork by clicking the "Sync Fork" button
1. fetch this locally
1. Find the commit you want to rebase onto master and get its codes: tolqqxls | bde02995
1. use jj rebase with -s to rebase descendants:
	`jj rebase  --source <id to move> --destination <master commit id>`
	e.g.
	`jj rebase  --source 00b4a9d1 --destination master`
