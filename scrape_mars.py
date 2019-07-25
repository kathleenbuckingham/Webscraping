from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

def scrape_all():
    
    #driver for deployment
    executable_path = {'executable_path': './chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    news_title, news_p = mars_news(browser)
    
    #run all scraping functions in dictionary - will this become a MongoDB document? 
    data = {
        "news_title":news_title,
        "news_paragraph":news_p,
        "featured_image":featured_image(browser),
        "twitter_mars_weather": twitter_mars_weather(browser),
        "mars_facts": mars_facts(browser),
        #"mars_hemispheres": mars_hemispheres
        
    }
    
 # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    # Get first list item and wait half a second if not immediately present
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=0.5)

    html = browser.html
    news_soup = BeautifulSoup(html, "html.parser")
  
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        news_title = slide_elem.find("div", class_="content_title").get_text()
        news_p = slide_elem.find(
            "div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None
    
 # return data
    return news_title, news_p

def featured_image(browser):
    url2 = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url2)
    
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()
    
    browser.is_element_present_by_text('more info', wait_time=0.5)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()
    
  
    html = browser.html
    img_soup = BeautifulSoup(html, "html.parser")
    
    img_url_rel = img_soup.select_one('figure.lede a img')
    
    try: 
        img_url_rel= img_url_rel.get("src")
       

    except AttributeError:
        return None

 # return data

    img_url = f"https://www.jpl.nasa.gov{img_url_rel}"
   
    return img_url

def twitter_mars_weather(browser):
    url3 = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url3)

    html = browser.html
    twitter_soup = BeautifulSoup(html, "html.parser")
  
    twitter_mars_weather = twitter_soup.find_all('div', class_="js-tweet-text-container")
    first_tweet = twitter_mars_weather[0].get_text()

    
 # return data
    return first_tweet

def mars_facts(browser):
    
    url4 = 'https://space-facts.com/mars/'
    tables = pd.read_html(url4)
    df = tables[0]
    df.columns = ['Record', 'Measurement']
    # Set index to Record in preparation for import into MongoDB
    df.set_index('Record', inplace=True)
    mars_facts_dictionary = {}
    for row in df.iterrows():
        mars_facts_dictionary[row[0][:-1]] = row[1][0]
    # Convert to HTML table string and return
    
    return mars_facts_dictionary

   

#def mars_hemispheres():

    
    #finally:

    #browser.quit()

if __name__ == "__main__":
    scrape_all()