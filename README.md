Grafeas + in-toto
=================

This repository provides an interface that converts
[standard in-toto link files](https://github.com/in-toto/docs/blob/master/in-toto-spec.md#44-file-formats-namekeyid-prefixlink)
into [Grafeas occurrences](https://github.com/grafeas/grafeas/blob/master/docs/grafeas_concepts.md#occurrences),
and vice versa, in an in-toto-verifiable manner.
Grafeas supports in-toto attestations as a note and occurrence kind since
v0.1.6. However, the format of the document supported in Grafeas is slightly
different from the default attestations generated by the in-toto reference
implementations.

## Use

To convert an in-toto link into a Grafeas in-toto occurrence:

```python
from totoify_grafeas.totoifylib import GrafeasInTotoOccurrence
# in_toto_link is of type in_toto.models.metadata.Metablock enclosing an instance of in_toto.models.link.Link
# step_name and resource_uri are strings
# from_link returns a totoify_grafeas.totoifylib.GrafeasInTotoOccurrence
GrafeasInTotoOccurrence.from_link(in_toto_link, step_name, resource_uri)
```

This interface will return a Grafeas in-toto occurrence, which can be stored in
a Grafeas server using typical methods.

To convert a Grafeas in-toto occurrence into an in-toto link:

```python
from totoify_grafeas.totoifylib import GrafeasInTotoOccurrence
# path is a string that points to a Grafeas in-toto Occurrence
g = GrafeasInTotoOccurrence.load(path)
# step_name is a string that specifies the step the link corresponds to
# to_link returns a Metablock enclosing a Link
g.to_link(step_name)
```

This interface will return an in-toto link, which can be used to perform in-toto
verification.

Planned Features:
- A Grafeas transport - this would allow users to send a Grafeas in-toto
  occurrence to a specified Grafeas server
- Grafeas occurrence generation in the referece implementation - the option to
  generate a Grafeas occurrence in the in-toto Python implementation instead of
  the traditional links
