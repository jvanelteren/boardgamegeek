import streamlit as st
import pandas as pd
pd.options.display.max_rows = 20
pd.options.display.float_format = "{:,.2f}".format
pd.options.mode.chained_assignment = None
import os
from dotproductbias import DotProductBias
import model
st.info(os.getcwd())
def update():
     # refreshes table when filters are changed
     st.session_state['selected_game'] = st.session_state['selected_game']

def quickselect():
     # refreshes table when filters are changed
     st.session_state['selected_game'] = st.session_state['quick_selection']
     update()

def modelupdate():
     # refreshes table when filters are changed
     if st.session_state['model'] == 'standard':
          model.m = model.modelstandard
     elif st.session_state['model'] == 'experimental':
          model.m = model.modeltransform
     update()
# Initialisation of session state
def reset(clear_cache=False):
     if clear_cache:
          for key in st.session_state.keys():
               del st.session_state[key]
     st.session_state.setdefault('selected_game', 'Chess')
     st.session_state.setdefault('minvotes', 0)
     st.session_state.setdefault('minaverage', 0)
     st.session_state.setdefault('weight', [0.,5.])
     st.session_state.setdefault('amountresults', 10)
     st.session_state.setdefault('sorting', 'similarity')
     st.session_state.setdefault('reverse', False)
     st.session_state.setdefault('quick_selection', 'Chess')
     st.session_state.setdefault('quick_options', ['Agricola', 'Pandemic', 'Chess', 'Monopoly'])
     st.session_state.setdefault('model', 'standard')
     modelupdate()
reset()


def filter(df):
     filtered_df = df.loc[(df['usersrated'] >= st.session_state['minvotes']) &
                          (df['average'] >= st.session_state['minaverage']) &
                          (df['averageweight'] >= st.session_state['weight'][0]) &
                          (df['averageweight'] <= st.session_state['weight'][1])
                          
                          ][:st.session_state['amountresults']]
     
     # filtered_df.set_index('thumbnail', inplace=True)
     # filtered_df.index.name = None
     
     filtered_df =  filtered_df.sort_values(st.session_state['sorting'], ascending=st.session_state['reverse'])
     st.session_state['quick_options'] = filtered_df['name'][:10]
     return filtered_df
# Sidebar filters
st.sidebar.header('Options to filter and sort')
st.sidebar.slider(
    "Minimal amount of votes",0,5000, key='minvotes', step=100, on_change=update
)
st.sidebar.slider(
    "Minimum average score",0.,10., key='minaverage', step=0.1, on_change=update, format="%.1f"
)
st.sidebar.slider(
    "Weight",0.,5., key='weight', value=[0.,5.], step = 0.1, on_change=update, format="%.1f"
)
st.sidebar.radio(
    "Amount of results",[10, 100,1000], key='amountresults', on_change=update
)
st.sidebar.radio(
    "Sort based on",['similarity', 'average', 'usersrated', 'averageweight'], key='sorting', on_change=update
)
st.sidebar.checkbox(
    "Reverse sort",key='reverse', on_change=update
)
st.sidebar.radio(
    "Model",['standard', 'experimental'], key='model', on_change=modelupdate
)

st.title('BoardGameExplorer')
game = st.selectbox(label='Select a game and see what the most similar games are!', options=model.df_games.sort_values('usersrated', ascending=False)['name'], key='selected_game')
df = filter(model.most_similar_games(st.session_state['selected_game']))


st.sidebar.radio(
    "Quick select game",st.session_state['quick_options'], key = 'quick_selection', on_change=quickselect
)
if st.sidebar.button('Reset selections'):
     reset(clear_cache=True)
     st.experimental_rerun()
 



table = st.write(df.to_html(escape = False, index=False), unsafe_allow_html = True)

