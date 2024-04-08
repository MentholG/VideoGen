import tweepy

# auth = tweepy.OAuth1UserHandler(
#    "API / EfsFcK59e51XMNEMkJ1EPC3nr", "API / fwuR7cHLZX8s3yPIvzg10PXSTJvVzqamE4oVTeda0ELxgTgCZZ",
#    "1754691630446346240-YiQ7IPXqkpIXyCYPdphzcI6IIDM2Js", "bSHorAGIei44du9Jyw7Q1r2h26kwtVdnbCfC3fJGN73qG"
# )
# api = tweepy.API(auth)
# # Replace these with your own keys and tokens
# api_key = "EfsFcK59e51XMNEMkJ1EPC3nr"
# api_key_secret = "fwuR7cHLZX8s3yPIvzg10PXSTJvVzqamE4oVTeda0ELxgTgCZZ"
# access_token = "1754691630446346240-YiQ7IPXqkpIXyCYPdphzcI6IIDM2Js"
# access_token_secret = "bSHorAGIei44du9Jyw7Q1r2h26kwtVdnbCfC3fJGN73qG"

# auth = tweepy.OAuthHandler(api_key, api_key_secret)
# auth.set_access_token(access_token, access_token_secret)

# api = tweepy.API(auth)

auth = tweepy.OAuth2BearerHandler("AAAAAAAAAAAAAAAAAAAAAOuEtAEAAAAAYzhz9at0NqpBPPew4uuZyIg4lOI%3Dceb4QX1DX1WxOMd8sQtaW8buJJfWooAm2OfZKIuqDc3xR2LS3M")
api = tweepy.API(auth)

query = 'OpenAI'  # Example search query
count = 5  # Number of results to retrieve

# Search for users
users = api.search_users(q=query, count=count)

for user in users:
    print(f"Username: {user.screen_name}, Name: {user.name}")

# Define your search keyword(s)
# search_keyword = "OpenAI"

# Search tweets
# tweets = api.search_tweets(q=search_keyword)

# # Print the text of each tweet
# for tweet in tweets:
#     print(tweet.text)