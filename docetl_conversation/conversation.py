import json
import llama_index.core
from jinja2 import Environment, Template
import re
import numpy as np
from rich.console import Console

class Conversation(object):
    system_prompt = """
        You are {{name}}, a student and will be discussing various subjects with
        {% if partner_names|length == 1 %}
          me, {{partner_names|first}}, another student.
        {% else %}
          us,
          {% for partner_name in partner_names %}
            {% if loop.last %} and {% else %}, {% endif %}
            {{partner_name}}
          {% endfor %} who are also students.
        {% endif %}
        You should occasionally ask questions and can, if you see fit, be argumentative.
        Try to answer questions, and don't just answer a question with a question!
        Our professor, {{professor_name}}, will ocassionally hint at a new subject to transition to or themes to include in your reply.
        {% if partner_names|length == 1 %}
          You don't need to explicitly address me by name, as {{professor_name}} know you'll never adress him.
        {% endif %}
        Your replies shouldn't be longer than a single paragraph. It can very well be a single sentence, especially if it's a question.
    """

    conversation_prompt = """
        {% for utterance in utterances %}
          {{utterance.speaker}}: {{utterance.text}}
        {% endfor %}
        {% if utterances|length == 0 %}
           {{professor_name}}: Please start the conversation by talking a bit about {{concept}}!
        {% else %}
          {{professor_name}}: Please incorporate {{concept}} into your answer.
          {% if utterances_left_total != None and utterances_left_total <= utterances_left_threshold %}
            {% if utterances_left_total < 2 %}
              Your reply is the last reply, and you should round up this conversation.
            {% else %}
              There are {{utterances_left_total}} turns left before we have to round up this conversation.
            {% endif %}
          {% endif %}
          {% if utterances_left != None and utterances_left <= utterances_left_threshold %}
            {% if utterances_left < 2 %}
              This is your last reply. Try to make it easier for your conversation partner to round up the conversation.
            {% else %}
              You have {{utterances_left}} replies left before we have to round up this conversation.
            {% endif %}
          {% endif %}
        {% endif %}
    """
    
    names = ["Anders", "Johan"]
    professor_name="Karl"

    title_key = None
    description_key = "description"

    utterances_left_total = None
    utterances_left = {}
    utterances_left_threshold = 3
    utterance_nr = 0
    
    def __init__(self, console, items, concepts, **kw):
        self.console = console
        self.items = items
        self.concepts = concepts
        for key, value in kw.items():
            setattr(self, key, value)

        assert self.professor_name not in self.names, "The professor should never have the same name as the speakers"
            
        self.system_prompt_template = Template(self.system_prompt)
        self.conversation_prompt_template = Template(self.conversation_prompt)

        self.documents = [llama_index.core.Document(
            doc_id=(i[self.title_key]
                    if self.title_key is not None
                    else str(idx)),
            text=i[self.description_key]) for idx, i in enumerate(items)]
        self.index = llama_index.core.VectorStoreIndex.from_documents(
            self.documents)
        self.chats = {name: self.index.as_chat_engine()
                      for name in self.names}

        self.buffers = {name: [] for name in self.names}

        # Make this an instance property so it can be safely modified...
        self.utterances_left = dict(self.utterances_left)
        
        for name, chat in self.chats.items():
            prompt = re.sub(
                r"^ +", "",
                self.system_prompt_template.render(
                    name=name,
                    partner_names=set(self.names) - set([name]),
                    professor_name=self.professor_name
                ))
            print("System prompt for %s: %s\n\n" % (name, prompt))
            chat.chat(prompt)

    exchanges_per_concept = 1
    def get_exchanges_per_concept(self, concept):
        return self.exchanges_per_concept

    # FIXME: Here we might want to add randomization etc...
    def get_speaker(self, concept):
        return self.names[self.utterance_nr % len(self.names)]
    
    def __iter__(self):
        return self.converse()

    def utter(self, name, concept):
        chat = self.chats[name]
        buff = self.buffers[name]
        partner_names = set(self.names) - set([name])

        prompt = re.sub(
            r"^ +", "",
            self.conversation_prompt_template.render(
                utterances=buff,
                name=name,
                partner_names=partner_names,
                professor_name=self.professor_name,
                concept=concept,
                utterances_so_far = self.utterance_nr,
                utterances_left_total = self.utterances_left_total,
                utterances_left = self.utterances_left.get(name, None),
                utterances_left_threshold = self.utterances_left_threshold
            ))
        del buff[:]
        print("Prompt for %s: %s\n\n" % (name, prompt))
        response = chat.chat(prompt)
        utterance = {"speaker": name, "text": response.response, "concept": str(concept)}
        for partner_name in partner_names:
            self.buffers[partner_name].append(utterance)

        if self.utterances_left_total is not None:
            self.utterances_left_total -= 1
        if name in self.utterances_left:
            self.utterances_left[name] -= 1
        return utterance
        
    def converse(self):
        for concept in self.concepts:
            for j in range(0, self.get_exchanges_per_concept(concept)):
                name = self.get_speaker(concept)

                if self.utterances_left_total == 0:
                    self.console.print("utterances_left_total == 0")
                    return
                if sum(self.utterances_left.get(speaker, np.inf)
                       for speaker in self.chats.keys()) == 0:
                    self.console.print("sum(utterances_left) == 0")
                    return
                if self.utterances_left.get(name, None) == 0:
                    self.console.print("utterances_left == 0 for %s" % name)
                    continue
                
                yield self.utter(name, concept)
                self.utterance_nr += 1
