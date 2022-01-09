from compare_keywords import compare_word_lists
from keywords import get_keywords_koe
from sklearn.naive_bayes import MultinomialNB
from db_functions import get_product
import random
import pickle
import numpy as np


K_PRODUCTS = 15
QUESTIONS = [("Likes to cook?",  ['cook', 'food', 'taste']), ("Likes to draw?", ['painting', 'art'])]

def predict_user_answer(q_keywords: list, product_keywords: dict):
    q_keywords_dict = {word: 1 for word in q_keywords}
    similarity = compare_word_lists(q_keywords_dict, product_keywords)
    return 1 if similarity > 0.06 else 0


def prepare_dataset(products_keywords: dict, question_keywords: list):
    answers = list()
    product_ids = []
    for product_id, product in products_keywords.items():
        answers.append([])
        product_ids.append(product_id)
        for q in question_keywords:
            answers[-1].append(predict_user_answer(q, product))
    return answers, product_ids


def train_nn(answers, products):
    clf = MultinomialNB()
    clf.fit(answers, products)
    data = pickle.dumps(clf)
    with open('Bayes_model.model', 'wb') as model_file:
        print(data, file=model_file)


def choose_gifts(user_answers):
    with open('Bayes_model.model', 'rb') as model_file:
        clf = pickle.loads(model_file.read())
    ans = clf.predict_proba(user_answers)
    product_ids = clf.classes_[np.flip(np.argsort(ans))][:K_PRODUCTS]
    return [get_product(id) for id in product_ids]


class BayesSession:
    def __init__(self):
        self.answers = [0.5] * len(QUESTIONS)
        self.unanswered_ids = list(range(len(QUESTIONS)))
        print(self.unanswered_ids)
        self.last_q_id = None
        random.shuffle(self.unanswered_ids)

    def new_answer(self, answer):
        self.answers[self.last_q_id] = answer

    def get_question(self):
        print("get question")
        if len(self.unanswered_ids) == 0:
            return None
        self.last_q_id = self.unanswered_ids.pop()
        return QUESTIONS[self.last_q_id]

    def get_presents(self):
        return choose_gifts(self.answers)


# PRODUCTS = {
#     "1982180587": """The Baseball 100
#     NEW YORK TIMES BESTSELLER
#
# “An instant sports classic.” —New York Post * “Stellar.” —The Wall Street Journal * “A true masterwork…880 pages of sheer baseball bliss.” —BookPage (starred review) * “This is a remarkable achievement.” —Publishers Weekly (starred review)
#
# A magnum opus from acclaimed baseball writer Joe Posnanski, The Baseball 100 is an audacious, singular, and masterly book that took a lifetime to write. The entire story of baseball rings through a countdown of the 100 greatest players in history, with a foreword by George Will.
#
# Longer than Moby-Dick and nearly as ambitious,​The Baseball 100 is a one-of-a-kind work by award-winning sportswriter and lifelong student of the game Joe Posnanski that tells the story of the sport through the remarkable lives of its 100 greatest players. In the book’s introduction, Pulitzer Prize–winning commentator George F. Will marvels, “Posnanski must already have lived more than 200 years. How else could he have acquired such a stock of illuminating facts and entertaining stories about the rich history of this endlessly fascinating sport?”
#
# Baseball’s legends come alive in these pages, which are not merely rankings but vibrant profiles of the game’s all-time greats. Posnanski dives into the biographies of iconic Hall of Famers, unfairly forgotten All-Stars, talents of today, and more. He doesn’t rely just on records and statistics—he lovingly retraces players’ origins, illuminates their characters, and places their accomplishments in the context of baseball’s past and present. Just how good a pitcher is Clayton Kershaw in the twenty-first- century game compared to Greg Maddux dueling with the juiced hitters of the nineties? How do the career and influence of Hank Aaron compare to Babe Ruth’s? Which player in the top ten most deserves to be resurrected from history?
#
# No compendium of baseball’s legendary geniuses could be complete without the players of the segregated Negro Leagues, men whose extraordinary careers were largely overlooked by sportswriters at the time and unjustly lost to history. Posnanski writes about the efforts of former Negro Leaguers to restore sidelined Black athletes to their due honor, and draws upon the deep troves of the Negro Leagues Baseball Museum and extensive interviews with the likes of Buck O’Neil to illuminate the accomplishments of players such as pitchers Satchel Paige and Smokey Joe Williams; outfielders Oscar Charleston, Monte Irvin, and Cool Papa Bell; first baseman Buck Leonard; shortstop Pop Lloyd; catcher Josh Gibson; and many, many more.
#
# The Baseball 100 treats readers to the whole rich pageant of baseball history in a single volume. Chapter by chapter, Posnanski invites readers to examine common lore with brand-new eyes and learn stories that have long gone unheard. The epic and often emotional reading experience mirrors Posnanski’s personal odyssey to capture the history and glory of baseball like no one else, fueled by his boundless love for the sport.
#
# Engrossing, surprising, and heartfelt, The Baseball 100 is a magisterial tribute to the game of baseball and the stars who have played it.""",
#     "B00KVI76ZS": """Elon Musk: Tesla, SpaceX, and the Quest for a Fantastic Future
#     In Elon Musk: Tesla, SpaceX, and the Quest for a Fantastic Future, veteran technology journalist Ashlee Vance provides the first inside look into the extraordinary life and times of Silicon Valley's most audacious entrepreneur. Written with exclusive access to Musk, his family and friends, the book traces the entrepreneur's journey from a rough upbringing in South Africa to the pinnacle of the global business world. Vance spent over 40 hours in conversation with Musk and interviewed close to 300 people to tell the tumultuous stories of Musk's world-changing companies: PayPal, Tesla Motors, SpaceX and SolarCity, and to characterize a man who has renewed American industry and sparked new levels of innovation while making plenty of enemies along the way.
#
#         Vance uses Musk's story to explore one of the pressing questions of our time: can the nation of inventors and creators which led the modern world for a century still compete in an age of fierce global competition? He argues that Musk--one of the most unusual and striking figures in American business history--is a contemporary amalgam of legendary inventors and industrialists like Thomas Edison, Henry Ford, Howard Hughes, and Steve Jobs. More than any other entrepreneur today, Musk has dedicated his energies and his own vast fortune to inventing a future that is as rich and far-reaching as the visionaries of the golden age of science-fiction fantasy.""",
#     "B00INIXU5I": """How We Got to Now: Six Innovations That Made the Modern World
#     From the New York Times–bestselling author of Where Good Ideas Come From and Extra Life, a new look at the power and legacy of great ideas.
#
# In this illustrated history, Steven Johnson explores the history of innovation over centuries, tracing facets of modern life (refrigeration, clocks, and eyeglass lenses, to name a few) from their creation by hobbyists, amateurs, and entrepreneurs to their unintended historical consequences. Filled with surprising stories of accidental genius and brilliant mistakes—from the French publisher who invented the phonograph before Edison but forgot to include playback, to the Hollywood movie star who helped invent the technology behind Wi-Fi and Bluetooth—How We Got to Now investigates the secret history behind the everyday objects of contemporary life.
#
# In his trademark style, Johnson examines unexpected connections between seemingly unrelated fields: how the invention of air-conditioning enabled the largest migration of human beings in the history of the species—to cities such as Dubai or Phoenix, which would otherwise be virtually uninhabitable; how pendulum clocks helped trigger the industrial revolution; and how clean water made it possible to manufacture computer chips. Accompanied by a major six-part television series on PBS, How We Got to Now is the story of collaborative networks building the modern world, written in the provocative, informative, and engaging style that has earned Johnson fans around the globe.""",
#
#     "B08H82ZRS2": """Megatek Dual T4-Pro IPX5 Waterproof Portable Bluetooth Speakers with Cool LED Lights & Wireless Stereo Pairing, 12 Watts Loud 360° HD Sound & Rich Bass, Small Speaker Set for Outdoor, Shower, & Pool
#     About this item
# CUTTING-EDGE WIRELESS STEREO PAIRING TECHNOLOGY: Want a speaker system that is small and portable but also delivers incredible immersive stereo sound? The dual Megatek T4 Pro speaker system perfectly fulfills your expectations and differentiates itself from any other single speakers: the two speakers wirelessly connect together and play music with incredible left and right stereo separation, with doubled output power (2 x 6W).
# SUPERIOR 360° HD SOUND WITH RICH BASS - The small portable design of the speakers does not compromise its sound performance. Equipped with advanced digital audio processor, high-end amplifier, well-adjusted driver and bass radiator, the Megatek T4-Pro delivers incredible high quality 360° sound with enhanced clarity of the mids and highs, and richer bass.
# DISTINCTIVE DESIGN WITH LED LIGHT SHOW – The Megatek T4-Pro is a treat for not only the ears but also the eyes. The elegant design with distinctive transparent housing, plus the cool 6-mode color-changing LED ambient lights dancing with music, will fit right in anywhere in your home, and light up your mood and party.
# INCREDIBLE VERSATILE & EASY TO USE - The built-in Bluetooth 4.2 technology offers you theconvenience to play up to 66 feet away (line of sight) from your device, with seamless and stable connection with the Echo Dot, Echo, Echo Plus, iPhone, iPad, Smartphone, Cellphone, Laptop, Mac, tablet, and all other Bluetooth enabled devices. Choose the AUX input (3.5mm type) for external sound, or connect with your computers to use them as a wireless 2.0 PC speaker system.
# SUPER PORTABILITY - The ultra-portable IPX5 water resistant speakers can be easily put into pocket, backpack, or suitcase, so you can bring them to the beach, pool and in the shower, to enjoy uninterrupted music up to 12 hours at medium volume on one full charge. Each set of speakers will come with a USB charging cable and a 3.5mm audio cable. What’s more, we will support you with our friendly customer service, and our worry-free 12-month warranty.""",
#     "B06X6K3HTS": """Fitbit Alta HR
#     About this item
# Made in the USA or Imported
# Get the power of continuous heart rate in Fitbit's slimmest design yet-all day, during workouts and beyond
# With heart rate, you can better measure calorie burn, and use zones (fat burn, cardio, and peak) to find the right workout intensity for your goals
# See how working out more can improve your health by comparing your resting heart rate trends to your activity
# With sleep stages powered by purpose heart rate, automatically track your time spent in light, deep and REM sleep and take steps toward a better night's rest
# Automatically track your steps, distance, calories burned and active minutes with up to 7 days of battery life (varies with use and other factors)""",
#     "B078HSVK7M": """Bang & Olufsen Beoplay H9i Wireless Bluetooth Over-Ear Headphones with Active Noise Cancellation, Transparency Mode and Microphone – Black - 1645026
#     About this item
# EASY LISTENING: Adjust the volume, change tracks and take calls with on-device touch controls. Enjoy added convenience with the proximity sensor that pauses playback when headphones are removed and resumes when placed back on.
# Frequency response - 20-20,000Hz and Impedance - 16 Ohms
# Lithium-Ion Battery Capacity: 770 mAh"""
# }
#
# KEYWORDS = [
#     ['metal', 'rock', 'rap', 'pop', 'music', 'sound'],
#     ['technologies', 'science', 'explorer'],
#     ['gym', 'fitness', 'sports', 'yoga', 'health', 'baseball'],
#     ['technologies', 'business', 'exploring'],
#     ['math', 'science', 'clever', 'knowledge', 'explore']
# ]
#
# for id, text in PRODUCTS.items():
#     prod_keywords = get_keywords_koe(text)
#     for question in KEYWORDS:
#         print(id, question, ':', predict_user_answer(question, prod_keywords))
#     print()
