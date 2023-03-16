#!/usr/bin/env python3
import os

import discord
import markovify
import nltk
import re

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


class POSifiedText(markovify.NewlineText):
    def word_split(self, sentence):
        words = re.split(self.word_split_pattern, sentence)
        tagged_words = []
        for tag in nltk.pos_tag(words):
            # The POS tagger gets confused when the sentence is
            # extremely short, and in particular it will fail to
            # recognize proper nouns. So for very short sentence
            # (e.g. being fed into make_sentence_with_start())
            # we will promote NN to NNP for capitalized words.
            if len(words) < 3 and tag[1] == 'NN' and list(tag[0])[0].isupper():
                tag = (tag[0], 'NNP')
            tagged_words.append("::".join(tag))
        # words = [ "::".join(tag) for tag in nltk.pos_tag(words) ]
        return tagged_words

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence


def build_model():
    with open('corpus.txt') as fd:
        corpus = fd.read()
    model = POSifiedText(corpus, state_size=2, well_formed=False)
    # model = markovify.NewlineText(corpus, state_size=2, well_formed=False)
    return model


def generate_response(model, input):
    sentence = None
    input_words = input.split()
    num_tries = 0
    while num_tries < 200:
        sentence = model.make_sentence(max_words=25)
        if sentence is None:
            continue
        valid_sentence = True
        if input != "":
            for word in input_words:
                if word not in sentence:
                    valid_sentence = False
                    break
        if valid_sentence:
            return sentence
    return "_I tried really hard, but I've got nothing for that :(_"


@client.event
async def on_message(message):
    # If the message was sent by a bot, ignore it
    if message.author.bot:
        return

    # If the message doesn't start with !drama, it's not for us
    if not message.content.startswith("!drama"):
        print("message content was not !markov: %s" % message.content)
        return

    # Generate a random response from the Markov model
    input = message.content.removeprefix("!drama")
    input = input.lstrip(" ")
    response = generate_response(model, input)
    await message.channel.send(response)


model = build_model()

# code to actually run the discord bot
token = os.environ.get('DISCORD_TOKEN')
if token == "":
    raise Exception('DISCORD_TOKEN must be set in the environment')
client.run(token)

# code to test the generation on the command line
# import sys
# for _ in range(0, 20):
#     sentence = None
#     if len(sys.argv) > 1:
#         sentence = generate_response(model, sys.argv[1])
#     else:
#         sentence = generate_response(model, "")
#     print(sentence)

