Grafeas + in-toto
=================

This repository contains an extension to grafeas that allows it to produce (and
use) in-toto metadata to secure the software supply chain.

This is done by adding the following fields to the grafeas api:


## Operation

An Operation will be extended with an in-toto layout metadata as part of it's
metadata field. This will describe the operation in depth and can be used to
verify that all the notes and occurrences are correct

You can load an in-toto layout into grafeas the following way:

```shell
$ grafeas-load [-t <server url>] -i <project id> -l <path/to/layout>
```

This will load a layout as the operation, and will namespace the
steps/inspections within it. As part of the load procedure, the
steps/inspections will also be cross-referenced with Notes:

## Notes

Notes are akin to step definitions in in-toto. We extended the grafeas api to
hold a reference to the step definition for each note. When loading an in-toto
layout into grafeas, the script will also generate a series of notes with the
proper namespacing (see namespacing) in order to produce a series of notes for
each step and inspection.

## Occurrences

Occurrences are the closest type of metadata that could match a link. As such, a
small extension to the current metadata format would allow for it to hold the
link metadata fields. You can test this using the client-side tool
`grafeas-run`

```shell
$ grafeas-run [-t <server url>] -i <project id> -k
              <path/to/signing/key> -n <step name>
              [-m <material/path> [<material/path> ...]]
              [-p <product/path> [<product/path> ...]]
               -- [<command to run> [<command to run> ...]]
```

This will run a command, record in-toto metadata, genearte a grafeas message
and post it on the grafeas server.
