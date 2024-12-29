from twilio.rest import Client 
import secrets_1
 
account_sid = secrets_1.TWILIO_ACCOUNT_SID
auth_token = secrets_1.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token) 
 
message = client.messages.create( 
                              from =secrets_1.WA_FROM,   
                              body='Your Yummy Cupcakes Company order of 1 dozen frosted cupcakes has shipped and should be delivered on July 10, 2019.',      
                              to=secrets_1.WA_TO 
                          ) 
 
print(message.sid)
