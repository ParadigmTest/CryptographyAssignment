First, run the drone2.py, this will set the db
Then we can run our mersenneT.py script that makes use of Mersenne Twister algorithm for the PRNG

Then from Postman run a POST requests: http://127.0.0.1:5000/add_user with the following JSON body:
{
    "username": "user1",
    "password": "password1"
}

This shall add the new user with username and password to our database

We can run the following also in Postman with the same JSON body to authenticate user, and make sure that the database recognises and validates the user
http://127.0.0.1:5000/authenticate

In terminal of our running server (where we executed mersenneT.py) we shall see this:
127.0.0.1 - - [15/Jan/2024 16:59:30] "POST /authenticate HTTP/1.1" 200 -

Now we proceed to run our hacking3.py script which will do the following:

First, we obtain a sequence of 624 consecutive session tokens (`token_sequence`) by making 624 sequential authenticated requests to the `/authenticate` endpoint.
Once we have 624 consecutive session tokens (succesfully printed in terminal for verification),  we now use the extract_number() function, which we know to be invertible, from the codebase to decode each of these tokens back into the internal state integers (MT) that were generated by the server



Given that the MT2 algorithm has a period of 2^19983, we should be able to predict all future session tokens based on these internal state integers. Thus, we can write a function to generate an unlimited number of new session tokens using the obtained MT integers:

Then, we can use the generate_tokens() function to generate a new session token ('new_token') that we will use to access/attack/hack the victim's account:

We proceed to update the user's session token in the server's internal user table with the generated new_token, at this point we can use the session token to either modify the username and password, or add_user, we hacked into an actual account by changing name and password from db to a new malicious one 
fakeuser1
fakepassword1


Finally we make an authenticate request to the `/authenticate` endpoint, using our new_token and the fake user and fake password and indeed are validated by the server by receiving the following response
{'session_token': '145b8f3a'}

Hence being validated by the system and succesfully managed to attack it
