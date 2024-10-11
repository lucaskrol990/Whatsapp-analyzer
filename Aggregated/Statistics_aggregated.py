import re
import datetime
import string
import pandas as pd
from collections import Counter
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud
from PIL import Image
import nltk
from nltk.corpus import words

'''
To dos:
Change file to read to your file
Look at option in word cloud: you can use it to add your own words to it
'''
filename = 'Chats/WhatsApp Chat with your lover.txt'

all_dutch_words = []
with open("Text dictionaries/dutch_wordlist.txt", "r", encoding='utf-8') as file:
    for line in file:
        all_dutch_words.append(line[:-1].lower())

english_words = set(words.words())


def find_names(message_strings):
    '''
    This function finds the names of senders within the messages
    '''
    names = []
    for message in message_strings: # Loop through all the messages
        name_match = re.search(r"-\s([A-Za-z\s]+):", message) # Identify the name strings
        if name_match: # If a match is found (so not None type)
            name = name_match.group(1).strip() # Select the first group out of the name string (which is the name)
                                               # and strip potential whitespaces
            if name not in names: # If name not identified before
                names.append(name) # Add to the group
    return names


def read_file(filename):
    '''
    Reads the .txt file containing the messages and stores them in a list
    '''
    messages = []
    with open(filename, "r", encoding='utf-8') as file:
        for line in file:
            if not re.search(r"[\d/]+, [\d:]+", line): # If there is no date at the start of the message
                messages[len(messages) - 1] = messages[len(messages) - 1] + '\n' + line[:-1] # It is part of the previous message
            else:
                messages.append(line[0:-1]) # -1 to exclude \n delimiter everywhere
    return messages


def remove_bot_messages(messages, names):
    '''
    Remove potential bot messages (not sent by a sender)
    '''
    idx_remove = []
    for idx, message in enumerate(messages):
        bot = True  # Assume that the message was sent by a bot (not one of the senders)
        for name in names:
            if message.find(name + ':') != -1:  # If we do find a name
                bot = False  # It is not a bot
                break  # We don't need to search further
        if bot:
            idx_remove.append(idx)

    return [message for idx, message in enumerate(messages) if idx not in idx_remove]


messages = read_file(filename)

# Extract the names from the senders
names = find_names(messages)

# Exclude potential bot messages
messages = remove_bot_messages(messages, names)

# Add the date of the message
date_time_list = []
for message in messages:
    date_time_match = re.search(r"[\d/]+, [\d:]+", message)
    date_time = datetime.datetime.strptime(date_time_match[0], '%d/%m/%Y, %H:%M')
    date_time_list.append(date_time)

sender_list = []
for message in messages:
    for name in names:
        if message.split(':')[1].find(name) != -1:  # If we do find this name
            sender_list.append(name)

message_list = []
for message in messages:
    message_list.append(message.split(':')[2])
message_df = pd.DataFrame({'Date': date_time_list, 'Sender': sender_list, 'Message': message_list})

'''
Find how many days messages were sent
'''

def days_messaged_donut_chart(message_df):
    days_messaged = message_df['Date'].dt.date.nunique()
    total_days = (message_df['Date'][message_df.shape[0] - 1] - message_df['Date'][0]).days + 1

    # Data for the diagram
    labels = ['Did message', 'No message']
    sizes = [days_messaged, total_days - days_messaged]
    colors = ['darkgreen', 'maroon']

    # Create the donut chart
    fig, ax = plt.subplots()
    wedges, texts = ax.pie(sizes, colors=colors, wedgeprops=dict(width=0.3), startangle=90, )
    ax.set_facecolor('none')  # Make the axis background transparent
    fig.patch.set_facecolor('none')  # Make the figure background transparent

    # Add a circle in the center to make it a donut (empty center)
    center_circle = plt.Circle((0, 0), 0.70, fc='none')
    fig.gca().add_artist(center_circle)

    # Add text in the center of the donut chart
    plt.text(0, 0, 'DAYS\nMESSAGED', ha='center', va='center', fontsize=18, fontweight='bold', color='white')

    # Calculate the cumulative angles to get the segment boundaries
    total_size = sum(sizes)
    angle_start = 90  # Starting angle at the top

    # Function to add curved text to donut chart
    def add_wrapped_text(ax, text, angle, radius, font_size=10, color='black'):
        """Place text that wraps along a circular arc."""
        # Calculate the angular width of the text (roughly)
        text_width = len(text) * font_size * 0.05  # Estimate of total text width in degrees

        char_width = font_size * 0.005
        char_angle = angle - text_width / 2  # Start position for the first character
        # Place each character along the arc
        for i, char in enumerate(text):
            # Calculate the angle for this character
            #char_angle = start_angle + i * (text_width / len(text))  # Spacing between characters
            char_angle += char_width / (2 * np.pi * radius) * 360
            # Calculate the position of the character using polar to Cartesian conversion
            x = radius * np.cos(np.radians(char_angle))
            y = radius * np.sin(np.radians(char_angle))

            # Rotate the character so it follows the curve of the arc
            rotation_angle = char_angle + 90  # Rotate to align along the arc

            # Add the character at the calculated position with the appropriate rotation
            ax.text(x, y, char, ha='center', va='center', fontsize=font_size, color=color,
                    rotation=rotation_angle, rotation_mode='anchor')

    # Place the text inside each segment of the donut
    for i, (size, wedge) in enumerate(zip(sizes, wedges)):
        if size > 0:
            angle = angle_start + size / 2 / total_size * 360

            # Add the text along the curvature of the donut segment
            add_wrapped_text(ax, f'{size}/{total_days}', angle, radius=0.85, font_size=14, color='white')


            # Update the starting angle for the next segment
            angle_start += size / total_size * 360

    # Equal aspect ratio ensures the pie is drawn as a circle
    ax.axis('equal')
    plt.savefig('assets/Days_messaged.png', transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close()

days_messaged_donut_chart(message_df)

'''
Find the frequency of sender
'''
def frequency_sender(message_df):
    return message_df.groupby('Sender').size().reset_index(name='\U0001F4AC Messages sent')

frequency_sender_df = frequency_sender(message_df)
'''
Find the average time between messages
'''
def avg_time_between_messages(message_df):
    time_df = message_df.copy()
    time_df = time_df[time_df['Sender'] != time_df['Sender'].shift()] # Do not count multiple messages from the same person
    time_df['Time_diff'] = time_df['Date'].diff() # Difference between message times
    time_df['Time_diff'].fillna(pd.Timedelta(0), inplace=True)
    # Round to seconds:
    time_df['Average time between messages'] = time_df['Time_diff'].dt.round('s')
    return time_df

avg_time_between_messages_df = avg_time_between_messages(message_df)


'''
Find how often a certain endearment word is used
'''

def endearment_counter(message_df):
    # Make a list containing common Dutch endearments
    word_list = []
    with open("Text dictionaries/dutch_endearments.txt", "r", encoding='utf-8') as file:
        for line in file:
            word_list.append(line[:-1].lower())

    # Create a regex pattern to match any word in word_list
    pattern = r'\b(?:' + '|'.join(map(re.escape, word_list)) + r')\b'

    # Apply regex search and count occurrences
    endearment_df = message_df.copy()
    endearment_df['word_count'] = endearment_df['Message'].str.lower().apply(lambda x: Counter(re.findall(pattern, x)))

    # Sum up the counts for each word
    endearment_counts = []
    for name in message_df['Sender'].unique():
        endearment_counts.append(sum(endearment_df.loc[endearment_df['Sender'] == name, 'word_count'], Counter()).most_common(5))

    return pd.DataFrame({'Sender': message_df['Sender'].unique(), 'Favourite endearment': [endearment_counts[i][0][0].capitalize() for i in range(len(names))]})

endearment_df = endearment_counter(message_df)
'''
Count emoji usage
'''
def emoticon_counter(message_df):
    # Define a regex pattern to match emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport & map symbols
        "\U0001F700-\U0001F77F"  # Alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric shapes extended
        "\U0001F800-\U0001F8FF"  # Supplemental arrows
        "\U0001F900-\U0001F9FF"  # Supplemental symbols & pictographs
        "\U0001FA00-\U0001FA6F"  # Chess symbols
        "\U00002600-\U000026FF"  # Miscellaneous symbols
        "\U00002700-\U000027BF"  # Dingbats
        "\U0001F1E0-\U0001F1FF"  # Flags
        "]+",
        flags=re.UNICODE
    )
    skin_tone_pattern = re.compile(r"[\U0001F3FB-\U0001F3FF]", flags=re.UNICODE)

    # Function to find and return all emojis in a message
    def emoji_search_re(text):
        return re.findall(emoji_pattern, text)

    emoji_df = message_df.copy()
    emoji_df['Emoticons (%)'] = list(map(emoji_search_re, emoji_df['Message']))
    # Sometimes multiple emojis behind each other are not treated separately, which is fixed here:
    for i in emoji_df.loc[[len(i) > 0 for i in emoji_df['Emoticons (%)']], :].index:
        for emoji in emoji_df.loc[i, 'Emoticons (%)']:
            if len(emoji) > 1:
                # Also excludes skin-tone emoji modifiers
                emoji_df.at[i, 'Emoticons (%)'] = [char for char in emoji if not skin_tone_pattern.search(char)]

    emoji_df = emoji_df.explode('Emoticons (%)') # Explode lists to separate indices
    emoticon_count = emoji_df['Emoticons (%)'].notna().sum()
    # print(f"Total number of emoticons used: {emoticon_count}")

    return round(emoji_df.groupby('Sender')['Emoticons (%)'].value_counts(normalize=True).groupby(level=0).head(50) * 100, 2)

emoticon_df = emoticon_counter(message_df)

'''
Word cloud in the form of a heart
'''
def process_words(word):
    word = word.lower()
    translator = str.maketrans('', '', string.punctuation)
    word = word.translate(translator) # Remove punctuation
    word = re.sub(r'[^\w\s]', '', word) # Remove emojis
    return word

from collections import Counter

def create_word_cloud(message_df):
    all_words = [process_words(word) for str in message_df['Message'] for word in str.split(" ")]
    # Remove numbers
    all_words = [word for word in all_words if word.isalpha()]
    # Remove some words which are not fun, too basic
    common_words = [''] # Empty string should also be removed
    with open('Text dictionaries/dutch_words_exclude.txt', "r", encoding='utf-8') as file:
        for line in file:
            common_words.append(line[:-1]) # Exclude \n

    common_words.extend(['media', 'omitted']) # Also exclude the words made by whatsapp if the image is not included
    all_words = [word for word in all_words if word not in common_words]

    # Other basic dutch words get weighed less
    basic_words = []
    with open('Text dictionaries/dutch_1000_basic.txt', "r", encoding='utf-8') as file:
        for line in file:
            basic_words.append(line[:-1])  # Exclude \n

    all_words = [word for word in all_words if word not in basic_words]
    # Option: add specific words with large number to ensure it shows up in the word cloud
    # all_words.extend(["example word"] * 50)
    heart_mask = np.array(Image.open('Heart.jpg'))

    word_counts = Counter(all_words)
    wc = WordCloud(mask=heart_mask, colormap='Reds', background_color=None, mode='RGBA').generate_from_frequencies(word_counts)

    plt.imshow(wc)
    plt.axis('off')
    plt.savefig("assets/Heart_word_cloud.png", transparent=True, bbox_inches='tight', pad_inches=0)
    plt.close()
    return all_words
    # plt.show()
create_word_cloud(message_df)

'''
Find number of words sent per person
'''
word_list = [process_words(word) for str in message_df['Message'] for word in str.split(" ")]
raw_words = [word.lower() for str in message_df['Message'] for word in str.split(" ")]
media_sent = len([word for word in raw_words if word == "omitted>"])
questions = sum([1 for word in raw_words if "?" in word])
uniquely_english_words = english_words.difference(set(all_dutch_words)) # Words which only appear in english
double_df = message_df[(message_df['Sender'] == message_df['Sender'].shift()) &
                            (message_df['Date'] - message_df['Date'].shift() > datetime.timedelta(minutes = 5))]
double_texts = sum([sum(double_df['Sender'] == name) for name in names])

love_emoji_pattern = re.compile(r'[\U0001F618\U0001F617\U0001F619\U0001F61A\U0001F48B\U00002764\U0001F495\U0001F496\U0001F497\U0001F498\U0001F49C\U0001F49B\U0001F49A\U0001F499\U0001F49F\U0001F494\U00002763]', flags=re.UNICODE)
number_of_love_emojis = sum(len(love_emoji_pattern.findall(message)) for message in message_df['Message'])

def format_to_minutes(td):
    total_seconds = int(td.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}:{str(seconds).zfill(2)}"

word_statistics = pd.DataFrame({'\U0001f4d6 Total words': [len(word_list)],
             '\U0001f453 Unique words': [len(set(word_list))],
             '\u2753 Questions asked': [questions],
             f'\U0001f482 English words': [len([word for word in word_list if word in uniquely_english_words])],
             '\U0001f647 Apologies made': [len([word for word in word_list if ("sorry" or "excuses") in word])],
             '\U0001f5bc\ufe0f Media sent': [media_sent],
             '\U0001f971 Double texts': [double_texts],
             '\U0001f48b Love emojis': [number_of_love_emojis]})
# '\u23f1 Response time': [avg_time_between_messages_df['Average time between messages'].apply(format_to_minutes)
# removed for sake of time
statistics_df = word_statistics
'''
Put all this data into one dataframe
'''

emoticon_df = emoticon_df.reset_index()
emoticon_df.columns = ['Sender', 'Emoticon', 'Proportion']
