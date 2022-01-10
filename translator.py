from googletrans import Translator

tr = Translator()


def translate_to_russian(text):
    return tr.translate(text, src='en', dest='ru').text
