# Authentication to SD-WAN Manager

As of software release 20.18 and higher, Cisco Catalyst SD-WAN Manager now supports JSON web token (JWT) authentication for REST API access control. For a general discussion of JWT, please refer to IETF RFC 7519. The previous method, which utilizes JSESSIONIDs, is also still supported for backward compatibility. The following sections describe both methods of authentication.

## 1. Session Based Authentication

As mentioned above, Cisco Catalyst SD-WAN Manager will also continue to support the traditional REST API access control based on sessions (JSESSIONIDs). With this method the Catalyst SD-WAN Manager creates a session for each user after successful login. The following are typical steps for a user to consume APIs using the session based authentication method:

![session-based-authentication](./images/authentication-session-based.jpg)

### 1.1. Log in with a username and password to establish a session

`POST /j_security_check` with `content type x-www-form-urlencoded` in the request header. The user name and password are submitted as `j_username` and `j_password`. The session token is in the response http cookie, `JSESSIONID={session hash}`.

```example
POST https://<SD-WAN Manager IP Address>/j_security_check
HTTP Request Header:
    {'Content-Type': 'application/x-www-form-urlencoded'}
HTTP Request Body: 
    {"j_username=<username>&j_password=<password>"}
```

When a user authenticates successfully, the response body is empty but the response header includes a valid session cookie. The session token is in the response HTTP cookie, `JSESSIONID=<session hash>`. An example is shown below:

```example
HTTP Response Header: {
'set-cookie': 'JSESSIONID=<session hash>',
...Additional headers not shown...
}
```

When a user is not authenticated successfully, the response body contains an HTML login page, indicated by an `<html>` tag. The API client should check the response body for the `<html>` tag to determine if authentication was successful.

### 1.2. Get a Cross-Site Request Forgery Prevention Token

Get a cross-site request forgery (XSRF) prevention token, necessary for most POST operations:

`GET /dataservice/client/token` with content type `application/json` in the request header. You also need to include the `JSESSIONID=<session hash>` cookie to within the request header to authenticate, as shown in the example below.

```example
GET https://<SD-WAN Manager IP address>/dataservice/client/token
HTTP Request Header:
    {'Content-Type': 'application/json', 'Cookie': 'JESSIONID=<session hash>'}
```

The XSRF token will be included in the response body as shown in the example below:

```example
HTTP Response Body:
    '<String containing the XSRF token>'
```

Use the JESSIONID cookie along with the XSRF token for further API requests.

### 1.3. Make an API Call

HTTP GET requests typically do not require an XSRF token to be included within the HTTP request header. Therefore, for GET requests, the user must only include the JSESSIONID as a cookie within the request header.

```example
GET https://<SD-WAN Manager IP address>/dataservice/<some API endpoint URL>
HTTP Request Header:
    {'Content-Type': 'application/json', 'Cookie': 'JESSIONID=<session hash>'} 
```

HTTP POST requests are in many cases not idempotent.  They can include form data which can result in changes to the Catalyst SD-WAN Manager.  As such, they typically do require an XSRF token in addition to the JSESSIONID cookie within the HTTP request header.

```example
POST https://<SD-WAN Manager IP address>/dataservice/<some endpoint>
HTTP Request Header:
    {'Content-Type': 'application/json', 'Cookie': 'JESSIONID=<session hash>', 'X-XSRF-TOKEN': '<XSRF token>'}
```

Note that for HTTP GET requests, you can also include the XSRF token within the header.  It will simply be ignored if not needed.

### 1.4. Log out and destroy the session

With the session based (JSESSIONID) authentication method, you should log out after completing requests to all necessary API endpoints. It is not only a good security practice, but also releases the allocated session resource.  

`POST /logout` with the optional `nocache=<random number>` query parameter which makes the request unique. Submit the JSESSIONID cookie within the HTTP request header.

```example
POST https://<SD-WAN Manager IP address>/logout?nocache=<random-number>`
HTTP Header: "Cookie: JESSIONID=<session hash>"
```

If the HTTP response code is 302 and redirects with the location header `https://<SD-WAN Manager IP address>/welcome.html?nocache=`, this indicates the session has been invalidated - meaning the user has been logged out.

### 1.5. Refresh Expired Tokens

The session token (JSESSIONID) for Cisco Catalyst SD-WAN Manager expires after 30 minutes of inactivity or after 24 hours, which is the total lifespan of a session. For more information, see <https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/sdwan-xe-gs-book/cisco-sd-wan-API-cross-site-request-forgery-prevention.html>

The cross-site request forgery prevention token (X-XSRF-TOKEN) is valid for the duration of the session and must be included in the header of each API request. For more information, see <https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/sdwan-xe-gs-book/cisco-sd-wan-api-cross-site-request-forgery-prevention.html>

### 1.6. Sample code to authenticate with Cisco Catalyst SD-WAN Manager

See: [Code snippet](./session.py)

## 2. JWT Based Authentication (starting from 20.18)

![jwt-authentication](images/authentication-jwt-based.jpg)

### 2.1. Log in with a username and password to receive a JWT token

Log in with a username and password to receive a JWT token (also referred to as the access token in this document):

`POST /jwt/login` with content type `application/json` in the request header. Submit the mandatory "username" and "password" attributes, along with an optional "duration" attribute, expressed in seconds (range in seconds from 1 to 604800 (7 days)), for the access token within the POST request body. The default expiration duration for the access token is 1,800 seconds (30 minutes). An example is shown below.

```example
POST https://<SD-WAN Manager IP address>:8443/jwt/login
HTTP Request Header: 
    {'Content-Type: application/json'}
HTTP Request Body: 
    {
    "username": "<String containing a username>",
    "password": "<String containing a password>",
    "duration": <Optional integer duration of range in seconds from 1 to 604800 (7 days)>
    }
```

When a user authenticates successfully, the response body will contain a JSON object of the following form:

```example
HTTP Response Body:
    {
    "token": "<String containing the access token>",
    "refresh": "<String containing the refresh token>",
    "sub": "<Optional case-sensitive string identifying the principal that is the subject of the JWT.  See RFC 7519>",
    "iss": "<Optional case-sensitive string containing the principal that issued the JWT.  See RFC 7519>",
    "aud": "<Optional case-sensitive string identifying the recipients the JWT is intended for. See RFC 7519>",
    "userGroup": "<String containing the SD-WAN Manager usergroup/role to which the userid belongs>",
    "tenant": "<String containing the SD-WAN Manager tenant name to which the userid belongs>",
    "duration": <Integer indicating the expiration duration of the access token in seconds>,
    "exp": <Integer indicating the expiration time on or after which the JWT must not be accepted.  See RFC 7519>
    "csrf": "<String containing a cross-site request forgery token, required for most POST actions>",
    "isAPIKey": <Boolean, indicating whether the access token is intended as a long-lived API key. Defaults to false>
    "tenantId": "<String containing the SD-WAN Manager tenant ID>"
    }
```

If a user fails to authenticate successfully, an HTTP 401 error will be returned.

Within the JSON object, the access token can be retrieved through the "token" claim within the response body. The "csrf" claim contains a cross-site request forgery (XSRF) prevention token, necessary for most POST operations. Hence, when using the JWT authentication method, a separate API call to `GET /dataservice/client/token` is not needed to retrieve the XSRF token.

Use the JWT token along with the XSRF token for further API requests.

Example of response:

```json
{
  "token": "eyJ0eXAiOiJqd3QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJqYmFyb3pldCIsdbaUpImlzcyI6IjNhOWEyN2VhLWQxNWUtNDEwNC05YjQxLTdiMGE5ZWExZWFjOSIsImF1ZCI6InZtYW5hZ2UiLCJ1c2VyR3JvdXAiOiJbbmV0YWRtaW5dIiwidGVuYW50IjoiTWFya2V0aW5nLURlbW8iLCJkdXJhdGlvbiI6MzYwMCwiZXhwIjoxNzUzMDk2NzE2LCJjc3JmIjoiMEIxMTAyOERQjA4RkYwOTIyQTEzOEMDlCMDczOEMyNzc5NTA2MDVBNjAyNkUwNzQ4MzVFMUVEM0NCRUQxNEJBNUQ1RDU0RTBFNTJS2V5IjpmYWxzZSwidGVuYW50SWQiOiJkZWZhdWx0In0.EMdhbdDhP3UmV34Ma8_7VNlIzfLy6gkznIBrvEeVsxCVKw2H_R-uhScs7nM9HmOi64gTsL5bS38db231aXS5_hW0U84dGgxN4dSxKG784fihlkpips9PF7n39L6N8fkqaO2UzmdtRf_FRnTIsWq1q3vmZJtAb1aMbp8MjmkRs06crcbSzQzGD2e35HgKfkNlNcnmLpvg9sxTY2QY0hjFoo3aXTmDzdlZvGY65QvXAah14zKkko8aiN30KDw",
  "refresh": "eyJ0eXAiOiJqd3QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJqYmFyb3pldCIsImNzcmYiOiIwQjExMDI4RERFMzYzRTlCMDDY3OEQwOUIwNzM4QzI3Nzk1MDYwNUE2MDI2RTA3NDgzNUUxRUABDUQzQ0JFRDE0QkE1RDVENTRFMEU1MTI0IiwiZXhwIjoyMDY0MTMxNjI1LCJ0ZW5hbnRJZCI6ImRlZmF1bHQifQ.dpy-CipMvhSo30oqml6yrCtEK4_G-VRC1mgHCntS1HkVpaUMDoRiHdcBy7HTOscHqdMfpdkOH0cbZnlfV-pGWkiR3wSsO_euiCtAUwb58SOycu8wil83StrtUoZmD1uNJdClNFHWjuZOQSS0m0oEmjDLFuqL2dOB8_671UzJsPFJSPA__3gthayTTx3MxgMDeDoIXZZjRyFopTpUVHA6hEBJuAhiTvxA",
  "sub": "admin",
  "iss": "3a9a49ea-d15e-4406-9b51-7b0a9ea1eac9",
  "aud": "vmanage",
  "userGroup": "[netadmin]",
  "tenant": "Demo",
  "duration": 3600,
  "exp": 1753096716,
  "csrf": "0B11028DDAAB66DDE363E9B08FF0922A138B3AB640DBD697E1AD03220738C2779526E074835E1ED3CBED14BA5D5D54E0E5124",
  "isAPIKey": false,
  "tenantId": "default"
} 
```

### 2.2. Make an API request

For calls to API endpoints, the user must provide the access token within the "Authorization" header of the HTTP request, in the form of a bearer token. For POST requests, the user must also provide the matching XSRF token.

```example
https://<SD-WAN Manager IP address>/dataservice/<some API endpoint URL>
HTTP Request Header:
    {'Content-Type': 'application/json', 'Authorization': 'Bearer <JWT token>', 'X-XSRF-TOKEN': '<XSRF token>'}
```

### 2.3. Refresh Expired Access Tokens

In addition to the access token, the Catalyst SD-WAN Manager also returns a refresh token, accessed through the "refresh" claim within the body of the `POST /jwt/login` API response.  The expiration duration for the refresh token is set at 1 day x duration of the access token.  Since the access token has a default expiration duration of 1,800 seconds, the expiration duration of the refresh token is 86,400 x 1,800 = 155,520,000 seconds or 1,800 days. The expiration duration of the refresh token can be increased or decreased by changing the expiration duration of the access token within the `POST /jwt/login` or `POST /jwt/refresh`(discussed below) API endpoints.

The refresh token can be used to generate a new access token without having to present the userid and password credentials through the `POST /jwt/refresh` API endpoint as follows:

```example
POST https://<SD-WAN Manager IP Address>:8443/jwt/refresh
HTTP Request Header:
    {'Content-Type': 'application/json'}
HTTP Request Body:
    {
    "refresh": "<Mandatory string containing the refresh token>",
    "duration": <Optional integer duration of range in seconds from 1 to 604800 (7 days)>
    }
```

When a user successfully refreshes the access token, the response body will contain a JSON object of the following form:

```example
HTTP Response Body:
    {
    "token": "<String containing the access token>",
    "refresh": "<String containing the refresh token>",
    }
```

Note that the refresh token returned by the `POST /jwt/refresh` API endpoint is not updated, meaning you cannot refresh the refresh token.  Once the refresh token expires, you can obtain a new access token (and new refresh token) by submitting credentials through a `POST /jwt/login` API endpoint.

### 2.4. Additional Topics

With the JWT authentication method there is no API endpoint for logging out. In order to mediate any concerns regarding access and refresh tokens still being valid after requests to all necessary API endpoints have been completed, the user can specify a short duration interval when requesting the token.