
import os

for file in os.listdir("topuserstweets"):
	os.rename("topuserstweets/"+file, "topuserstweets/"+file.lower())
