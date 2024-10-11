import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go

from Statistics_aggregated import emoticon_df, statistics_df, endearment_df, word_statistics, message_df
statistics_df = statistics_df.T

'''
To do:
Change picture (by crtl + f on asset) if you don't stick to the regular naming scheme
'''

'''
Options for the dashboard:
'''
bg_color_dashboard = "#484965" # Background colour of the dashboard
bg_color_stats = "#2d2a3d" # Background colour of the "statistic" blocks

'''
Required functions
'''
# Reusable function to create a statistic block
def create_stat_block(value, txt_color = 'green', bg_color=bg_color_stats, height = 7):
    """
    Create a styled HTML Div block for displaying statistics.

    Args:
    - value (str): The main value to display (e.g., '00:31:23').
    - label (str): A short description or label for the value.
    - bg_color (str): Background color for the block (default is dark grey).

    Returns:
    - html.Div: A styled Dash HTML Div component.
    """
    return html.Div([
        html.H4(value, style={'color': txt_color, 'fontSize': str(min([3, 0.5 * height])) + 'vh'}),
    ], style={
        'borderRadius': '1vh',
        'padding': '1vh 2vh',  # Padding for top/bottom and left/right
        'margin': '1vh 0vh',  # Margin for separation between blocks
        'color': 'white',
        'display': 'flex',  # Set flex display for horizontal alignment
        'alignItems': 'center',  # Center content vertically
        'backgroundColor': bg_color,
        'boxShadow': '0vh 0vh 1vh rgba(255,255,255,0.1)',
        'width': '100%',  # Make the width responsive to the container size
        'maxWidth': '100%',  # Ensure it does not exceed the parent dbc.Col size
        'overflow': 'hidden',  # Handle text overflow
    })

def format_to_minutes(td):
    total_seconds = int(td.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}:{str(seconds).zfill(2)}"

def find_colours(statistics_df):
    colours = []
    for col in row_names:
        if statistics_df[col][0] == statistics_df[col][1]:
            colours.append(['green', 'green'])
        elif statistics_df[col][0] < statistics_df[col][1]:
            colours.append(['red', 'green'])
        else:
            colours.append(['green', 'red'])
    colours = [lst[::-1] if not condition else lst for lst, condition in zip(colours, more_is_better)]
    return colours

# Function to create a custom bar component
def create_custom_bar(male_freq, female_freq, emoticon, height = 5):
    """
    Create a custom HTML bar showing male and female relative frequencies.

    Args:
    - male_freq (float): Relative frequency for male (e.g., 0.3 for 30%)
    - female_freq (float): Relative frequency for female (e.g., 0.1 for 10%)
    - emoticon (str): The emoticon to display next to the bar.

    Returns:
    - html.Div: A styled Div component representing the bar.
    """
    # Calculate widths for male and female segments as percentages
    total_freq = male_freq + female_freq
    male_width = (male_freq / total_freq) * 100  # Percentage width for male
    female_width = (female_freq / total_freq) * 100  # Percentage width for female

    bar_height = 0.7 * height
    padding = 0.3 * height
    # Create a Div with the emoticon and the bar
    return html.Div([
        # Emoticon Label on the left
        html.Div(emoticon, style={
            'display': 'inline-block',
            'height': f"{bar_height}vh",
            'fontSize': f"{bar_height}vh",
            'width': f"{bar_height}vh",
            'textAlign': 'left',
            'margin': f'0 1vw 0 0'
        }),

        # Bar Container
        html.Div([
            # Male Segment of the Bar
            html.Div(style={
                'display': 'inline-block',
                'width': f'{male_width}%',
                'height': f"{bar_height}vh",
                'backgroundColor': 'blue'
            }),

            # Female Segment of the Bar
            html.Div(style={
                'display': 'inline-block',
                'width': f'{female_width}%',
                'height': f"{bar_height}vh",
                'backgroundColor': 'pink'
            }),
        ], style={'display': 'inline-block', 'width': f'{33 - 1.5 * height - 1}vw'})  # Total width of the bar
    ], style={'margin': f'{padding}vh 0'})  # Margin for spacing between bars

'''
Creating the dashboard
'''
# Create a basic Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

'''
Statistic section
'''
row_names = statistics_df.index

stat_layout = dbc.Container([dbc.Row([
        dbc.Col(
            html.Div([html.H4('\U0001f5e3 CONVERSATION STATISTICS', style={'fontSize': '3vh'})])
        )
    ])] +
    [
    dbc.Row([
        dbc.Col(html.P(row_names[i], style={'fontSize': '3vh', 'overflow': 'hidden', 'textAlign': 'left'}), width=6, style={'display': 'flex', 'alignItems': 'center'}),
        dbc.Col(create_stat_block(statistics_df.loc[row_names[i], 0]),
           style={'justifyContent': 'flex-end'}, width=6)
    ], style={'backgroundColor': bg_color_dashboard}) for i in range(len(row_names))
], fluid=True)

stat_section = dbc.Container([
    dbc.Row([stat_layout])
], style={'backgroundColor': bg_color_dashboard, 'height': '75vh'})


'''
First message section
'''
first_message_section = dbc.Container([
                            dbc.Row([
                                        html.Div([html.H4('\U0001f4ac FIRST MESSAGE', style={'fontSize': '3vh', 'textAlign': 'left', 'width': 'auto', 'height': '3vh', 'display': 'block'})]),
                                        html.Div(('"' + message_df.loc[0, "Message"] + '"').strip(), style = {'font-family': 'Lobster', 'width': 'auto'})
                                ])
              ], style={'backgroundColor': bg_color_dashboard, 'height': '10vh'})

'''
First ik hou van jou section
'''
hou_van_jous = [index for index, message in message_df['Message'].items() if "hou van jou" in message]
date_hvj = pd.Timestamp(message_df['Date'][hou_van_jous].values[0]).strftime('%Y-%m-%d %H:%M:%S')
first_hvj_section = dbc.Container([
                            dbc.Row([
                                        html.Div([html.H4('\U0001f618 FIRST "HOU VAN JOU"', style={'fontSize': '3vh', 'textAlign': 'left', 'width': 'auto', 'height': '3vh', 'display': 'block'})]),
                                        html.Div(date_hvj, style = {'font-family': 'Lato', 'width': 'auto'})
                                ])
              ], style={'backgroundColor': bg_color_dashboard, 'height': '10vh'})


'''
Emoticon usage
'''
emoticon_df.columns = ['Sender', 'Emoticon', 'Proportion']
# First find the 5 emoticons which are used the most (sum of frequencies)
unique_emojis = emoticon_df['Emoticon'].unique()

tot_prop = [(emoticon_df.loc[emoticon_df['Emoticon'] == emoji, 'Proportion'].sum(), emoji) for emoji in unique_emojis]
most_used_emojis = [emoji for _, emoji in sorted(tot_prop, key=lambda x: x[0], reverse=True)[:5]]

emoticon_frequencies = [[emoticon_df.loc[(emoticon_df['Sender'] == name) &
                         (emoticon_df['Emoticon'] == emoji), 'Proportion'].values[0]
                         for name in emoticon_df['Sender'].unique()]
                        for emoji in most_used_emojis]


# Create a list of custom bar components
bar_layout = [html.Div([html.H4('\U0001f600 EMOTICON USAGE', style={'fontSize': '3vh', 'textAlign': 'left', 'width': 'auto', 'height': '3vh', 'display': 'block'})])] + \
              [create_custom_bar(emoticon_frequencies[i][0], emoticon_frequencies[i][1], most_used_emojis[i]) for i in
              range(len(most_used_emojis))]
emoji_bar_section = dbc.Container(bar_layout, style={'padding': '1vh'})
'''
Favourite endearment
'''
image_layout = dbc.Row([
    dbc.Col(html.Img(src='assets/Picture_1.jpg', style={'width': '7vh', 'height': '7vh', 'borderRadius': '50%'}), width=6, style={'textAlign': 'left'}),
    dbc.Col(html.Img(src='assets/Picture_2.jpg', style={'width': '7vh', 'height': '7vh', 'borderRadius': '50%'}), width=6, style={'textAlign': 'right'})
], justify='center', align='center')  # Center the images below the blocks

endearment_section = dbc.Container([
                        dbc.Row([
                            dbc.Col([
                                html.Div([html.H4('\U0001f493 FAVOURITE ENDEARMENT', style={'fontSize': '3vh', 'textAlign': 'left', 'width': 'auto', 'height': '3vh', 'display': 'block'})])
                            ], width = 12)
                        ]),
                        dbc.Row([  # Nested row to place two columns side-by-side
                                dbc.Col(create_stat_block(endearment_df['Favourite endearment'][0], txt_color = 'white'), width=6),
                                dbc.Col(create_stat_block(endearment_df['Favourite endearment'][1], txt_color = 'white'), width=6)
                            ],
                        style={'justifyContent': 'flex-end'}),
                        dbc.Row([image_layout], style = {'textAlign': 'center'})
                    ])

'''
Word cloud section
'''
word_cloud_section = html.Div([
    html.H4('\u2601\ufe0f Word Cloud', style={'fontSize': '3vh', 'textAlign': 'left', 'width': 'auto', 'height': '3vh', 'display': 'block'}),
    html.Img(src='/assets/Heart_word_cloud.png', style={'width': 'auto', 'height': '45vh', 'display': 'block', 'margin': 'auto',
                                                        'backgroundColor': bg_color_dashboard})
])

'''
Cute image section
'''
cute_image_section = html.Div([
    html.H4(f'Chat of {endearment_df["Sender"][0].split(" ")[0]} and {endearment_df["Sender"][1].split(" ")[0]}', style={'fontSize': '3vh', 'textAlign': 'left', 'width': 'auto', 'height': '3vh', 'display': 'block'}),
    html.Img(src='/assets/Cute_photo.png', style={'width': 'auto', 'height': '45vh', 'display': 'block', 'margin': 'auto',
                                                        'backgroundColor': bg_color_dashboard})
])


'''
Day messaged section
'''
days_messaged_section = html.Div([
    html.Img(src='/assets/Days_messaged.png', style={'width': 'auto', 'height': '40vh', 'display': 'block', 'margin': 'auto',
                                                        'backgroundColor': bg_color_dashboard})
])

'''
Dashboard itself
'''
# Dashboard Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Container([
                dbc.Row([dbc.Col(emoji_bar_section, width = 12),
                         dbc.Col(endearment_section, width = 12),
                         dbc.Col(days_messaged_section, width = 12)
                ])
            ])
        ],
        width = 4),
        dbc.Col([
            dbc.Container([
                dbc.Row([dbc.Col(word_cloud_section, width = 12),
                         dbc.Col(cute_image_section, width = 12),
                ])
            ])
        ],
        width = 4),
        dbc.Col(
            dbc.Container([
                dbc.Row([dbc.Col(stat_section, width=12),
                         dbc.Col(first_message_section, width=12),
                         dbc.Col(first_hvj_section, width = 12)
                         ])
            ])
            , width=4)  # Second column taking up 4 out of 12 columns
    ], style={'backgroundColor': bg_color_dashboard, 'height': '100vh', 'width': '100vw'})  # Match the full height/width of the viewport
], fluid=True)

app.run_server(debug=False)
