import json
import llama_index.core
from jinja2 import Environment, Template
import re

class Conversation(object):
    system_prompt = """
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
    """

    conversation_prompt = """
        {% if utterances|length == 0 %}
           {{professor_name}}: Please start the conversation by talking a bit about {{concept}}!
        {% else %}
          {% for utterance in utterances %}
            {{utterance.speaker}}: {{utterance.text}}
          {% endfor %}
          {{professor_name}}: Please incorporate {{concept}} into your answer.
        {% endif %}
    """
    
    names = ["Anders", "Johan"]
    professor_name="Karl"
    
    def __init__(self, items, concepts, **kw):
        self.items = items
        self.concepts = concepts
        for key, value in kw.items():
            setattr(self, key, value)

        assert self.professor_name not in self.names, "The professor should never have the same name as the speakers"
            
        self.system_prompt_template = Template(self.system_prompt)
        self.conversation_prompt_template = Template(self.conversation_prompt)
        
        self.documents = [llama_index.core.Document(doc_id=i["concept"], text=i["description"]) for i in items]
        self.index = llama_index.core.VectorStoreIndex.from_documents(self.documents)
        self.chats = {name: self.index.as_chat_engine()
                      for name in self.names}

        self.buffers = {name: [] for name in self.names}

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
            
    def __iter__(self):
        return self.converse()

    def converse(self):
        for i, n in enumerate(self.concepts):
            name = self.names[i % len(self.names)] # FIXME: Here we might want to add randomization etc...
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
                    concept=n
                ))
            del buff[:]
            print("Prompt for %s: %s\n\n" % (name, prompt))
            response = chat.chat(prompt)
            utterance = {"speaker": name, "text": response.response}
            for partner_name in partner_names:
                self.buffers[partner_name].append(utterance)
            yield utterance

            
