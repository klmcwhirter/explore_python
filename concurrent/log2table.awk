#!/usr/bin/gawk -f

BEGIN {
    print "| Command Line | Results | Elapsed Time |"
    print "| :-- | :--: | --: |"
}

$0 ~ "^python" {
    cli = $0
}

/perfect numbers/ {
    rb = index($0, "[")
    re = index($0, "]")
    results = substr($0, rb, re - rb + 1)

    print "| " cli " | " results " | " $NF " |"
}
