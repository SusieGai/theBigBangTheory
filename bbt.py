#!/usr/bin/env python
# coding: utf-8

# ## data source 1 - Wikipidia

# In[1]:


from bs4 import BeautifulSoup
import requests
import json
import pandas as pd
import sys
import csv
import os
import numpy as np
import seaborn as sns
import statsmodels.api as sm
import matplotlib.pyplot as plt


# In[2]:


## legal_scrap: function to check if I can legally scrap the data. 
## Return type: Boolean. Only if return True, I can continue the later steps.

def legal_scrap (url):
    content = requests.get(url)
    if content.status_code == 200:
        #print('Since the status code is 200, I can legally download and scrap the data from ',url,' Hooray!')
        return True
    else:
        print('uh oh, seems like I need to find other websites...' )
        return False


# In[3]:


# data source 1 Wikipedia
def wiki_scrap():
    # wiki_url is the website I am going to scrap in this function
    wiki_url = 'https://en.wikipedia.org/wiki/List_of_The_Big_Bang_Theory_episodes'
    if not legal_scrap(wiki_url):
        return false
    response = requests.get(wiki_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find_all('table',{'class':"wikitable plainrowheaders wikiepisodetable"})
    table_readable=pd.read_html(str(table))
    table_each_season_dict = {}
#'''table_each_seasopn_dict is a dictionary to look up the row data from wiki of each season. 
#The key is type.int of 1 to 12. '''
    df = pd.DataFrame(table_readable[0])
    for i in range(12):
        table_each_season_dict [i+1] = pd.DataFrame(table_readable[i])
        if i > 0:
            df = df.append(pd.DataFrame(table_readable[i]))
    df.reset_index(drop = True, inplace = True)
# df is the data frame that right now contains all the data from wiki. 
# df is the main data frame that I will do my analysis on
# The later code in this cell is to clean up df to make my analysis easier

# The following step is to change the 'U.S. viewers(millions)' into float type and strip the notation signs(like [14]).
    viewer_list = []   
    for i in df['U.S. viewers(millions)']:
        viewer_list.append(float(i.split('[')[0]))
    df.insert(df.shape[1],'viewers(millions)',viewer_list)
# The followering step is to seperate the 'Written by' data into Story by and Teleplay by. 
# There are 10 episode that written by and story by are note seperated. I substitute them with a unique class 'collaboration'
# Because in many cases, there are multiple story writters and teleplay writters, 
# I am going to make a dictionary of the appearance of each writters, for story and teleplay seperately.
# Most likely, the value of this dictionary will not be used. But it is good to store it just in case.
# Also, from the .keys() of this dictionary, I get the list of all the writters names, which will be used in my analysis. 
    story = []
    tele = []
    for i in df['Written by']:
        if 'Story by' not in i:
            story.append('collaboration')
            tele.append('collaboration')
        else:
            i = i.split ('Teleplay by')
            #print((i[1]))
            k = i[0].split(':')
            story.append(k[1].strip(':'))
            s = i[0].split(':')
            tele.append(s[1])
            
    count_story = {}
    for i in story:
        for k in i.split('&'):
            count_story [k.strip(' ')] = count_story.get(k.strip(' '),0)+1
    story_writter_names = list(count_story.keys())

    count_tele = {}
    for i in tele:
        for k in i.split('&'):
            count_tele [k.strip(' ')] = count_tele.get(k.strip(' '),0)+1
    tele_writter_names = list(count_tele.keys())

    df.insert(df.shape[1],'story_writer',story)
    df.insert(df.shape[1],'teleplay_writer',tele)
    df = df.drop(columns = ['Written by','Title','Original air date','Prod.code','U.S. viewers(millions)'])

# Here, I put the splited stroy_writer and teleplay_writer back to my df, 
#and dropped the original 'Written by' column since he data is duplicated.
# Also, I dropped 'Title','Original air date','Prod.code','U.S. viewers(millions)' since they are not useful or has been duplicated.

#In the following step, I want to creat a new column indicating the season number of each episode.
#I add it to my df in the end.

    k = 0
    season = 1
    season_list = []
    for i in df['No. inseason']:
        if i>= k:
            k = i
            season_list.append(season)
        else:
            k=i
            season +=1
            season_list.append(season)
    df.insert(df.shape[1],'season',season_list)
    return(df)
# right now, I have done cleaning up the data scraped from wikipedia page. 
# I will use the dataframe,df, and the two lists, story_writter_names and tele_writter_names later on.


# In[4]:


def transcrips_scraping(df): # parameter df is the result from wiki_scrap
    episode_table_url = 'https://bigbangtrans.wordpress.com/'
    transcripts_url_list = []
    transcripts_url_dict = {}
    count = 1
    if legal_scrap(episode_table_url):
        response = requests.get(episode_table_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        row = soup.find_all('a')
        for url in row:
            if url.text.startswith('Se'):
                transcripts_url_list.append((count,url.get('href')))
                transcripts_url_dict[url.text[:20]] = url.get('href')
                count = count+1
    transcripts_dict = {}
    #count = 0
    for (i,url) in transcripts_url_list:
        if legal_scrap(url):
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            transcripts = soup.find_all('p')
            pure_text_list = []
            for line in transcripts:
                pure_text_list.append(line.text)
            transcripts_dict[i] = pure_text_list
        count+=1
        #print (count,'done,next!')
    #print('Done,done!')
    
    character_list = ['Penny','Howard', 'Sheldon','Leonard','Raj','Bernadette','Amy']
    Penny = []
    Howard = []
    Sheldon = []
    Leonard = []
    Raj = []
    Bernadette = []
    Amy = []
    count_character_lines = {}
    count_character_words = {}
    average_words_per_line = []
    for i,v in transcripts_dict.items():
        words_count = 0
        count_character_lines[i]={'Penny':0,'Howard':0, 'Sheldon':0,'Leonard':0,'Raj':0,'Bernadette':0,'Amy':0}
        for character in character_list:
            for line in v:
                if line.startswith(character):
                    count_character_lines[i][character]=count_character_lines[i][character]+1
        Penny.append(count_character_lines[i]['Penny'])
        Howard.append(count_character_lines[i]['Howard'])
        Sheldon.append(count_character_lines[i]['Sheldon'])
        Leonard.append(count_character_lines[i]['Leonard'])
        Raj.append(count_character_lines[i]['Raj'])
        Bernadette.append(count_character_lines[i]['Bernadette'])
        Amy.append(count_character_lines[i]['Amy'])
        for line in v:
            words_count+= len(line.split(' '))
        average_words_per_line.append (words_count/(len(v)))
    
    new_df = {'Penny':Penny,'Howard':Howard, 'Sheldon':Sheldon,'Leonard':Leonard,
              'Raj':Raj,'Bernadette':Bernadette,'Amy':Amy,'Ave_length':average_words_per_line}
    new_df = pd.DataFrame(new_df)
    df = pd.concat([df, new_df], axis=1)
    return(df)
    


# In[5]:


# Data source 3 api from IMDb
def IMDb_api(df): # parameter df is the result from transcrips_scraping
    imdb_api_key = 'k_ff61gj6z'

    half_url = "https://imdb-api.com/en/API/SeasonEpisodes/k_6t30fr19/tt0898266/"
    season = list(range(1,13))
    url_list = []
    for i in range(12):
        season[i] = str(season[i])
        url_list.append (half_url+season[i])
    imdb_rating = []
    imdb_rating_count = []

    for url in url_list:
        response = requests.get(url)
        res = response.json()
        for i in res['episodes']:
            imdb_rating.append(i['imDbRating'])
            imdb_rating_count.append(i['imDbRatingCount'])

    imdb_rating = imdb_rating[1:]
    imdb_rating_count = imdb_rating_count[1:]
    df.insert(df.shape[1],'imdb_rating_count',imdb_rating_count)
    df.insert(df.shape[1],'imdb_rating',imdb_rating)
    return(df)


# In[6]:


def default_function():
    print('This function usually takes up to 10 mins to run. Please wait patiently...')
    df = IMDb_api(transcrips_scraping(wiki_scrap()))
    print(df[:10])
    df.to_csv('data.csv')
    #return(df)
    print(' ')
    print('default_function printing finished')


# In[7]:


def clean():
    df = pd.read_csv('data.csv')
    df = df.drop(labels = 'Unnamed: 0',axis = 1)
    new_story_writer = []
    for i in df['story_writer']:
        if i == 'collaboration':
            new_story_writer.append(0)
        else:
            new_story_writer.append(i.count('&')+1)
    #print(len(new_story_writer))
    new_teleplay_writer=[]
    for i in df['teleplay_writer']:
        if i == 'collaboration':
            new_teleplay_writer.append(0)
        else:
            new_teleplay_writer.append(i.count('&')+1)
    df.insert(df.shape[1],'story',new_story_writer)
    df.insert(df.shape[1],'tele',new_teleplay_writer)
    df = df.drop(labels = ['Directed by','story_writer','teleplay_writer'],axis = 1)
    df_with_lines = df.iloc[:231]
    x_w = df_with_lines.drop(labels = 'imdb_rating', axis = 1)
    y_w = df_with_lines['imdb_rating'].tolist()
    y_w_mean = np.mean(y_w)
    #y_w_class = []
    #for i in y_w:
        #if i<y_w_mean:
        #    y_w_class.append(0)
     #   else:
    #        y_w_class.append(1)
    #class_df_with_lines = x_w
   # class_df_with_lines.insert(x_w.shape[1],'class',y_w_class)
    return(df_with_lines,x_w,y_w)


# In[8]:


def lineplot():
    print('To see the change of over time, pleae choose ONE feature name from the following:')
    print(' ')
    print(clean()[0].columns.tolist())
    print(' ')
    print('!!! PLEASE PAY ATTENTION to the  s p a c e  and UPPER/lower case of the features name (copy/paste recommanded)')
    x = input()
    print('-'*50)
    print ('The x-axis is time (as the release of each episode), and the y-axis is the feature of your choice')
    sns.lineplot(x=range(231),y=clean()[0][x])
    plt.show()


# In[9]:


def describe():
    print(clean()[0].describe())


# In[10]:


def regression ():
    model = sm.OLS(clean()[2], clean()[1])
    results = model.fit()
    print(results.summary())


# In[18]:


def static_function():
    print('Data from static file. csv format')
    print('Printing the first 10 rows of the 279 rows')
    print(' ')
    print('The first 6 columns:')
    print(' ')
    print(pd.read_csv('data.csv').iloc[:10,:6])
    print('-'*80)
    print(' ')
    print('The middle 6 columns:')
    print(' ')
    print(pd.read_csv('data.csv').iloc[:10,6:12])
    print('-'*80)
    print(' ')
    print('The last 6 columns:')
    print(' ')
    print(pd.read_csv('data.csv').iloc[:10,12:])


# In[11]:


if __name__ == '__main__':
    if len(sys.argv) == 1:
        default_function()
    elif sys.argv[1] == '--lineplot':
        lineplot()
    elif sys.argv[1] == '--describe':
        describe()
    elif sys.argv[1] == '--regression':
        regression()
    elif sys.argv[1] == '--static':
        static_function()


# In[ ]:




