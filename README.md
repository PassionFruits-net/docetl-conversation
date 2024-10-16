# A conversation geenerator for [docetl](https://github.com/ucbepic/docetl)

This is a docetl operation that generates a conversation between a number of people, based on a knowledge graph.
The conversation flow takes the knowledge graph links into account, as well as clustering of the nodes.

Example configuration

```yaml
- name: conversation
  type: conversation
  length: 6
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
[
  {
    "speaker": "Alice",
    "text": "What are some key rights that purchasers should have when buying goods or services?"
  },
  {
    "speaker": "Bob",
    "text": "When purchasing goods or services, purchasers should have the right to receive products that meet the promised quality standards, the right to accurate information about the product or service, and the right to fair pricing. How does market functionality impact these rights in your opinion?"
  },
  {
    "speaker": "Alice",
    "text": "Market functionality plays a crucial role in ensuring that purchasers' rights are upheld. In rental markets, the availability of options and competition can influence the quality, information transparency, and pricing of products or services. How do you think rental markets specifically impact the rights of purchasers in comparison to traditional purchasing markets?"
  },
  {
    "speaker": "Bob",
    "text": "Rental markets provide flexibility and access to products without the long-term commitment of ownership, but they may also limit the control and customization options for purchasers. In comparison to traditional purchasing markets, rental markets may offer lower upfront costs but could restrict ownership rights and customization choices. How do you see the balance between ownership and rental impacting purchasers' rights in different market scenarios?"
  },
  {
    "speaker": "Alice",
    "text": "The balance between ownership and rental in different market scenarios can significantly impact purchasers' rights. Licensing agreements in rental markets, for example, may restrict the usage or modification rights of purchasers compared to traditional ownership models. How do you think licensing agreements influence the rights of purchasers in terms of product usage and customization options?"
  },
  {
    "speaker": "Bob",
    "text": "Licensing agreements in rental markets, influenced by patents, can limit purchasers' rights by restricting their ability to modify or use products beyond the terms specified in the agreement. Patents play a role in protecting intellectual property but can also create barriers for purchasers in terms of customization and usage rights. How do you perceive the intersection of patents, licensing agreements, and purchasers' rights in the context of product innovation and access?"
  }
]
```

# The default prompts

Default prompts and other parameters and how to override them:

```yaml
  professor_name: Karl
  system_prompt: |
        You are {{name}}, a student and will be discussion various subjects with
        {% if partner_names|length == 1 %}
          me, {{partner_names|first}}, another student.
        {% else %}
          us,
          {% for partner_name in partner_names %}
            {% if loop.last %} and {% else %}, {% endif %}
            {{partner_name}}
          {% endfor %} who are also students.
        {% endif %}
        You should occasionally ask questions, and can if you see fit, be argumentative.
        Try to answer questions, and don't just answer a question with a question!
        Our professor, {{professor_name}}, will ocassionally hint at a new subject to transition to or themes to include in your reply.
        {% if partner_names|length == 1 %}
          You don't need to explicitly address me by name, as {{professor_name}} know you'll never adress him.
        {% endif %}
        Your replies shouldn't be longer than a single paragraph. It can very well be a single sentence, especially if it's a question.

  conversation_prompt: |
        {% if utterances|length == 0 %}
           {{professor_name}}: Please start the conversation by talking a bit about {{concept}}!
        {% else %}
          {% for utterance in utterances %}
            {{utterance.speaker}}: {{utterance.text}}
          {% endfor %}
          {{professor_name}}: Please incorporate {{concept}} into your answer.
        {% endif %}
```
