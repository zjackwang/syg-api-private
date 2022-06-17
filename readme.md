## SaveYourGroceries Private API Server

### Required HTTP Request Headers 
1. X-Hmac-Signature: HMAC signature generated from request payload and the shared private key 
2. X-Hmac-Message: String message used to generated hmac signature
3. X-Is-Test-Request: String "true" or "false. The latter allows writes to go through to the db.

### Endpoints
#### /usersubmittedgenericitemset
POST
- Add individual "generic item" to the set of user submitted generic items 
#### /usersubmittedmatcheditemset
POST
- Add individual "matched item" to the set of user submitted matched items 
- Matched item is 
{
    "scannedItemName": Str,
    "genericItemObj": GenericItem 
}
#### /userupdatedgenericitemset
POST 
- Add a pairing of "generic items". 
{
    "original": GenericItem,
    "updated": GenericItem 
}
