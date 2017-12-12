Grafeas + in-toto
=================

This repository contains an extension to grafeas that allows it to produce (and
use) in-toto metadata to secure the software supply chain.

This is done by adding the following fields to the grafeas api:


## Operation

An Operation will be extended with an in-toto layout metadata as part of it's
metadata field. This will describe the operation in depth and can be used to
verify that all the notes and ocurrences are correct

You can load an in-toto layout into grafeas the following way:

```shell
$ grafeas-load --layout [in-toto.layout] --host [URL]
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

## Ocurrences

Ocurrences are the closest type of metadata that could match a link. As such, a
small extension to the current metadata format would allow for it to hold the
link metadata fields. You can test this using the client-side tool
`grafeas-run`

```python
$ grafeas-run --host [url] --key [signing-key] --name [ocurrence-name] -- command [arg1] [arg2]...[argn]
```

This will run a command, record in-toto metadata, genearte a grafeas message
and post it on the grafeas server.
