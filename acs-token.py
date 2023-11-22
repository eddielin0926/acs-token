import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from azure.communication.identity import CommunicationIdentityClient, CommunicationUserIdentifier
 

app = FastAPI()
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate the identity client
connection_string = os.environ.get("ACS_CONNECTION_STRING")
client = CommunicationIdentityClient.from_connection_string(connection_string)

ids = {}
for name, value in os.environ.items():
    print("{0}: {1}".format(name, value))
    ids[name] = value

def get_acs_token(id):
    identity = CommunicationUserIdentifier(id)
    token_result = client.get_token(identity, ["voip"])
    return token_result[0]  
 
@app.get("/tokens/{user_id}")
def get_token(user_id: str):
    return get_acs_token(user_id)

@app.get("/ids/{user_name}")
def get_id(user_name: str):
    ID = f"ACS_ID_{user_name.upper().replace('-','')}"
    if ID not in ids:
        raise HTTPException(status_code=404, detail="id not found")
    id = ids[ID]
    token = get_acs_token(id)
    return {
        "id": id,
        "token": token
    }

if __name__=="__main__":
    uvicorn.run("acs-token:app", host='0.0.0.0', port=8000)
