FROM python:3-slim

RUN pip3 install discord.py markovify nltk
RUN python3 -m nltk.downloader -d /usr/local/share/nltk_data averaged_perceptron_tagger
COPY bot.py /
COPY corpus.txt /
USER nobody:nogroup
ENTRYPOINT ["/bot.py"]
