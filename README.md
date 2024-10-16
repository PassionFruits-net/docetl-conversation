# A conversation geenerator for [docetl](https://github.com/ucbepic/docetl)

This is a docetl operation that generates a conversation between a number of people, based on a knowledge graph.
The conversation flow takes the knowledge graph links into account, as well as clustering of the nodes.

Example configuration

```yaml
- name: conversation
  type: conversation
  length: 5
  names:
    - Alice
    - Bob
  title_key: concept
  description_key: description
  link_key: related_to    # A list of titles related to this title
  cluster_key: clusters # You must have run a clustering operation first
```

Example output:

```json
```
