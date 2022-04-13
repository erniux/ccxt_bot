from twilio.rest import Client 
import secrets
 
account_sid = secrets.TWILIO_ACCOUNT_SID
auth_token = secrets.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token) 
 
message = client.messages.create( 
                              from_='whatsapp:+14155238886',  
                              body='Your Yummy Cupcakes Company order of 1 dozen frosted cupcakes has shipped and should be delivered on July 10, 2019. Details: http://www.yummycupcakes.com/',      
                              to='whatsapp:+5214427505679' 
                          ) 
 
print(message.sid)
