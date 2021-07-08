from selenium import webdriver
import pandas as pd
import datetime
import time
import re

def parse(profile_url):
    
    driver = webdriver.Firefox()
    
    def return_scroll_height():
        """
        Return scroll height as int
        """
        return driver.execute_script("return document.body.scrollHeight")

    def month_digit(month_str):
        return str(["Jan", "Feb", "Mar", "Apr",
                    "May", "Jun", "Jul", "Aug",
                    "Sep", "Oct", "Nov", "Dec"].index(month_str) + 1)

    def format_date(str_date):
        if re.match("\d{4}", str_date) == None:
            str_date += ", "+str(datetime.date.today().year)
    
        
        mdy = re.sub("[A-Z][a-z]{2}",
                     month_digit(str_date[:3])+",",
                     str_date).split(", ")
        ymd = mdy[2] + "." + mdy[0] + "." + mdy[1]
        return ymd
    
    driver.get(profile_url)
    time.sleep(5)

    tweets = []
    last_height = return_scroll_height()
    while True:
        for i in range(1, 12):
            try:
                xpath = f"/html/body/div/div/div/div[2]/main/div/div/div/div[1]/div/div[2]/div/div/div[2]/section/div/div/div[{i}]"
                tweets.append(driver.find_element_by_xpath(xpath).text)
            except:
                pass

        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(1)

        # Calculate new scroll height and compare with last scroll height
        new_height = return_scroll_height()
        if new_height == last_height:
            break
        if len(tweets) > 100:
            break
        last_height = new_height
        
    tweets = list(set(tweets))
    
    driver.close()

    tweet_names, tweet_logins, tweet_dates, tweet_texts = [], [], [], []

    for tweet in tweets:
        try:
            if "Retweeted" in tweet.split("\n")[0]:
                tweet_dates.append(format_date(re.findall("[A-Z][a-z]+ \d{1,2}, \d{4}|[A-Z][a-z]+ \d{1,2}",
                                                          tweet)[0]))
                tweet_names.append(re.findall(".+", tweet)[1])
                tweet_logins.append(re.findall(".+", tweet)[2])
                tweet_texts.append("\n".join(re.findall(".+", tweet)[5:]))
            else:    
                tweet_dates.append(format_date(re.findall("[A-Z][a-z]+ \d{1,2}, \d{4}|[A-Z][a-z]+ \d{1,2}",
                                                          tweet)[0]))
                tweet_names.append(re.findall(".+", tweet)[0])
                tweet_logins.append(re.findall(".+", tweet)[1])
                tweet_texts.append("\n".join(re.findall(".+", tweet)[4:]))
        except:
            pass

    tweets_df = pd.DataFrame({"names":tweet_names,
                              "logins":tweet_logins,
                              "dates (%y%m%d)":tweet_dates,
                              "texts":tweet_texts})
    
    return tweets_df
